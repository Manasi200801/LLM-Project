"""
Summarize refusals and non answers from the output of score_prompts.py.

score_prompts.py saves, for every prompt, outside_mass: the probability that the
next token is NOT an answer letter (1 minus the summed letter probabilities).
This script turns that into tables per model, language, persona, template,
item and option order.

Signals:
  outside_mass       continuous. Mean per group and share of prompts at or
                     above --threshold.
  top1_non_letter    the most likely next token is not a valid answer letter.
  top1_ambiguous     the most likely token is "I" on an item that has an option
                     I (9 or more options, here Q36a). It could be the answer or
                     the start of "I cannot". It is NOT counted as non letter.
                     refusal_generate.py resolves these cases.

The prompt ends with the prefill "Answer:", so a real refusal can hide in these
token level signals. Run refusal_generate.py and pass its folder with --gen to
add generated labels. Rates from generated text use only the stratified sample
(source sample or both), never the flagged prompts, which are not representative.

Files written to --out:
  summary_model_language.csv   one row per model and language (also printed)
  by_condition.csv             model x language x persona x template
  by_item.csv                  model x language x item
  by_order.csv                 model x language x order_id (position bias check)
  paired_language.csv          EN vs DE outside mass on matched prompts
  nonletter_tokens.csv         what the model says instead of a letter
  flagged_prompts.csv          prompts with a reason: outside, non_letter, ambiguous_I
  generation_summary.csv       (with --gen) label shares per model, language, mode
  generation_by_persona.csv    (with --gen) label shares per model, language, persona, mode

Usage:
  python refusal_analysis.py --results results --out refusal_out
  python refusal_analysis.py --results results --out refusal_out --gen refusal_gen
  python refusal_analysis.py --results results --extra_words my_refusal_words.txt
"""
import argparse
import glob
import json
import os
import string

import pandas as pd

from refusal_common import REFUSAL_WORDS, classify_token, load_words


def row_features(row, threshold, refusal_words):
    letters = set(string.ascii_uppercase[: int(row["n_options"])])
    tokens = json.loads(row["top_tokens"])
    top1_token, top1_prob = tokens[0]
    top1_cat = classify_token(top1_token, letters, refusal_words)
    nonletter = next(
        ((t, p) for t, p in tokens
         if classify_token(t, letters, refusal_words) != "answer_letter"),
        (None, None),
    )
    ambiguous = top1_token.strip() == "I" and "I" in letters
    reasons = []
    if row["outside_mass"] >= threshold:
        reasons.append("outside")
    if top1_cat != "answer_letter":
        reasons.append("non_letter")
    if ambiguous:
        reasons.append("ambiguous_I")
    return pd.Series({
        "top1_token": top1_token,
        "top1_prob": top1_prob,
        "top1_category": top1_cat,
        "top1_non_letter": top1_cat != "answer_letter",
        "top1_ambiguous": ambiguous,
        "top_nonletter_token": nonletter[0],
        "top_nonletter_prob": nonletter[1],
        "outside_ge_threshold": row["outside_mass"] >= threshold,
        "reason": "+".join(reasons),
    })


def load_results(results_dir, threshold, refusal_words):
    paths = sorted(glob.glob(os.path.join(results_dir, "*.csv")))
    if not paths:
        raise FileNotFoundError(f"No CSV files found in {results_dir}")
    df = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    # order_id is not saved by score_prompts.py, but it is part of prompt_id.
    df["order_id"] = (
        df["prompt_id"].str.extract(r"_(rev|rot\d+|shuf\d+)$")[0].fillna("official")
    )
    feats = df.apply(row_features, axis=1, threshold=threshold,
                     refusal_words=refusal_words)
    return pd.concat([df, feats], axis=1)


def aggregate(df, keys):
    return (
        df.groupby(keys)
        .agg(
            n_prompts=("prompt_id", "count"),
            mean_outside=("outside_mass", "mean"),
            median_outside=("outside_mass", "median"),
            max_outside=("outside_mass", "max"),
            share_outside_ge_threshold=("outside_ge_threshold", "mean"),
            share_top1_non_letter=("top1_non_letter", "mean"),
            share_top1_ambiguous=("top1_ambiguous", "mean"),
        )
        .reset_index()
        .round(4)
    )


def paired_language(df):
    """Compare EN and DE outside mass on matched prompts.

    Pairs share model, persona, template, item and option order. The wording
    differs between languages, so this is a matched comparison, not an
    identical text comparison.
    """
    keys = ["model", "persona", "template_id", "item_id", "order_id"]
    wide = df.pivot_table(index=keys, columns="language", values="outside_mass")
    if not {"DE", "EN"} <= set(wide.columns):
        return pd.DataFrame()
    wide = wide.dropna(subset=["DE", "EN"])
    rows = []
    for model, g in wide.groupby(level="model"):
        diff = g["DE"] - g["EN"]
        p_value = None
        try:
            from scipy.stats import wilcoxon
            p_value = float(wilcoxon(diff).pvalue) if (diff != 0).any() else 1.0
        except ImportError:
            pass
        rows.append({
            "model": model,
            "n_pairs": len(diff),
            "mean_outside_EN": g["EN"].mean(),
            "mean_outside_DE": g["DE"].mean(),
            "mean_diff_DE_minus_EN": diff.mean(),
            "wilcoxon_p": p_value,
        })
    return pd.DataFrame(rows).round(4)


def load_generations(gen_dir):
    paths = sorted(glob.glob(os.path.join(gen_dir, "gen_*.csv")))
    if not paths:
        raise FileNotFoundError(f"No gen_*.csv files found in {gen_dir}")
    return pd.concat([pd.read_csv(p, keep_default_na=False) for p in paths],
                     ignore_index=True)


def label_shares(gen, keys):
    counts = gen.groupby(keys + ["label"]).size().unstack("label", fill_value=0)
    shares = counts.div(counts.sum(axis=1), axis=0).add_prefix("share_")
    shares.insert(0, "n", counts.sum(axis=1))
    return shares.reset_index().round(4)


def attach_generation_labels(flagged, gen):
    """Add the generated label and the start of the text to flagged prompts."""
    cols = {}
    for mode in sorted(gen["mode"].unique()):
        g = gen[gen["mode"] == mode].drop_duplicates(["model", "prompt_id"])
        g = g.set_index(["model", "prompt_id"])
        cols[f"gen_label_{mode}"] = g["label"]
        cols[f"gen_text_{mode}"] = g["generated_text"].str.replace("\n", " ").str[:80]
    extra = pd.DataFrame(cols).reset_index()
    return flagged.merge(extra, on=["model", "prompt_id"], how="left")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results",
                    help="Folder with the CSV files written by score_prompts.py")
    ap.add_argument("--out", default="refusal_out")
    ap.add_argument("--threshold", type=float, default=0.2,
                    help="outside_mass at or above this counts as a non answer")
    ap.add_argument("--gen", default=None,
                    help="Folder with gen_*.csv from refusal_generate.py")
    ap.add_argument("--extra_words", default=None,
                    help="Text file with more refusal opening words, one per line")
    args = ap.parse_args()

    refusal_words = set(REFUSAL_WORDS)
    if args.extra_words:
        refusal_words |= load_words(args.extra_words)

    df = load_results(args.results, args.threshold, refusal_words)
    os.makedirs(args.out, exist_ok=True)

    summary = aggregate(df, ["model", "language"])
    summary.to_csv(os.path.join(args.out, "summary_model_language.csv"), index=False)
    aggregate(df, ["model", "language", "persona", "template_id"]).to_csv(
        os.path.join(args.out, "by_condition.csv"), index=False)
    aggregate(df, ["model", "language", "item_id"]).to_csv(
        os.path.join(args.out, "by_item.csv"), index=False)
    aggregate(df, ["model", "language", "order_id"]).to_csv(
        os.path.join(args.out, "by_order.csv"), index=False)

    paired = paired_language(df)
    paired.to_csv(os.path.join(args.out, "paired_language.csv"), index=False)

    nonletter = (
        df[df["top1_non_letter"]]
        .groupby(["model", "language", "top1_category", "top1_token"])
        .agg(n=("prompt_id", "count"), mean_prob=("top1_prob", "mean"))
        .reset_index()
        .sort_values("n", ascending=False)
        .round(4)
    )
    nonletter.to_csv(os.path.join(args.out, "nonletter_tokens.csv"), index=False)

    flagged = df[df["reason"] != ""][[
        "model", "prompt_id", "language", "persona", "item_id", "template_id",
        "order_id", "outside_mass", "reason", "top1_token", "top1_category",
        "top_nonletter_token", "top_nonletter_prob", "top_tokens",
    ]].sort_values("outside_mass", ascending=False)

    gen = None
    if args.gen:
        gen = load_generations(args.gen)
        flagged = attach_generation_labels(flagged, gen)
        rep = gen[gen["source"].isin(["sample", "both"])]
        gen_summary = label_shares(rep, ["model", "language", "mode"])
        gen_summary.to_csv(os.path.join(args.out, "generation_summary.csv"), index=False)
        label_shares(rep, ["model", "language", "persona", "mode"]).to_csv(
            os.path.join(args.out, "generation_by_persona.csv"), index=False)
    flagged.to_csv(os.path.join(args.out, "flagged_prompts.csv"), index=False)

    print(f"{len(df)} prompts from {df['model'].nunique()} model(s). "
          f"Threshold {args.threshold}.\n")
    print(summary.to_string(index=False))
    if not paired.empty:
        print("\nEN vs DE on matched prompts:")
        print(paired.to_string(index=False))
    print(f"\nFlagged prompts: {len(flagged)} of {len(df)}")
    print(f"  ambiguous I: {int(df['top1_ambiguous'].sum())}")
    if gen is not None:
        print("\nGenerated text, stratified sample only:")
        print(gen_summary.to_string(index=False))
        if "gen_label_prefill" in flagged.columns:
            amb = flagged[flagged["reason"].str.contains("ambiguous_I")]
            if len(amb):
                print("\nAmbiguous I resolved by generation (prefill mode):")
                print(amb["gen_label_prefill"].fillna("not generated").value_counts()
                      .to_string())
    print(f"\nTables written to {args.out}/")


if __name__ == "__main__":
    main()
