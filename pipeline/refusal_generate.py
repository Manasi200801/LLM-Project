"""
Generate short answers to check for real refusals.

score_prompts.py only reads the next token after the prefill "Answer:". A model
that wants to refuse can hide this, and for items with 9 or more options the
token "I" is both answer letter I and the start of "I cannot". This script
generates a few tokens for a sample of prompts and labels what comes out.

Two modes per prompt:
  prefill  the same input as score_prompts.py (chat template plus "Answer:"),
           then generate. Resolves the ambiguous "I" and shows what follows
           the cue.
  free     the chat template only, no prefill. Shows whether the model refuses
           when it is not pushed into the answer format. Skipped for base models.

Which prompts:
  sample   stratified random sample, --per_group prompts for every language and
           persona. Use only these for rates. They are representative.
  flagged  prompts from refusal_out/flagged_prompts.csv (written by
           refusal_analysis.py), so every ambiguous or suspicious case gets
           checked. These are NOT representative. refusal_analysis.py keeps
           them out of the rates.

Usage (small test on a Mac):
  python refusal_generate.py --model Qwen/Qwen2.5-0.5B-Instruct --prompts prompts.csv --per_group 2

Usage (cluster):
  python refusal_generate.py --model meta-llama/Llama-3.1-8B-Instruct --prompts prompts.csv \
      --flagged refusal_out/flagged_prompts.csv --out refusal_gen

Needs score_prompts.py in the same folder. Output: refusal_gen/gen_<model>.csv
"""
import argparse
import csv
import os
import re
import string
import time

from refusal_common import classify_generation

FIELDS = [
    "model", "prompt_id", "language", "persona", "item_id", "template_id",
    "order_id", "source", "mode", "n_options", "generated_text", "label",
]


def order_id_of(prompt_id):
    m = re.search(r"_(rev|rot\d+|shuf\d+)$", prompt_id)
    return m.group(1) if m else "official"


def read_flagged_ids(path, model, max_flagged):
    """Prompt ids to check. Ambiguous cases are always kept, the rest is capped."""
    with open(path, encoding="utf8") as f:
        rows = [r for r in csv.DictReader(f) if r["model"] == model]
    ambiguous = [r for r in rows if "ambiguous_I" in r["reason"]]
    others = sorted((r for r in rows if "ambiguous_I" not in r["reason"]),
                    key=lambda r: -float(r["outside_mass"]))[:max_flagged]
    return [r["prompt_id"] for r in ambiguous + others]


def select_prompts(rows, per_group, seed, flagged_ids):
    """Return a list of (row, source). Deterministic for a given seed."""
    import random
    rng = random.Random(seed)
    by_id = {r["prompt_id"]: r for r in rows}
    groups = {}
    for r in rows:
        groups.setdefault((r["language"], r["persona"]), []).append(r)
    picked = {}
    for key in sorted(groups):
        group = sorted(groups[key], key=lambda r: r["prompt_id"])
        rng.shuffle(group)
        for r in group[:per_group]:
            picked[r["prompt_id"]] = "sample"
    for pid in flagged_ids:
        if pid in by_id:
            picked[pid] = "both" if pid in picked else "flagged"
    return [(by_id[pid], src) for pid, src in picked.items()]


def feed_text(tok, row, use_chat, mode):
    """The exact text fed to the model. 'prefill' matches score_prompts.py."""
    if not use_chat:
        return row["prompt_text"] if mode == "prefill" else None
    from score_prompts import chat_prefix  # same template handling as scoring
    text = chat_prefix(tok, row)
    return text + row["assistant_prefill"] if mode == "prefill" else text


def run(rows_with_source, tok, use_chat, modes, model_name, gen_fn, writer, log=print):
    """Generate and label. gen_fn(text) returns the generated string."""
    t0 = time.time()
    n_done = 0
    total = len(rows_with_source) * len(modes)
    for row, source in rows_with_source:
        letters = set(string.ascii_uppercase[: int(row["n_options"])])
        for mode in modes:
            text = feed_text(tok, row, use_chat, mode)
            if text is None:
                continue
            generated = gen_fn(text)
            writer.writerow({
                "model": model_name,
                "prompt_id": row["prompt_id"],
                "language": row["language"],
                "persona": row["persona"],
                "item_id": row["item_id"],
                "template_id": row["template_id"],
                "order_id": order_id_of(row["prompt_id"]),
                "source": source,
                "mode": mode,
                "n_options": row["n_options"],
                "generated_text": generated,
                "label": classify_generation(generated, letters),
            })
            n_done += 1
            if n_done % 20 == 0 or n_done == total:
                log(f"[{n_done}/{total}] {time.time() - t0:.0f}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompts", default="prompts.csv")
    ap.add_argument("--out", default="refusal_gen")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--base", action="store_true",
                    help="Base (non chat) model: no chat template, only prefill mode")
    ap.add_argument("--per_group", type=int, default=8,
                    help="Sample size per language x persona (14 groups)")
    ap.add_argument("--flagged", default=None,
                    help="flagged_prompts.csv from refusal_analysis.py")
    ap.add_argument("--max_flagged", type=int, default=200)
    ap.add_argument("--max_new_tokens", type=int, default=40)
    ap.add_argument("--modes", default="prefill,free")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    # Imported here so the helpers above can be used and tested without torch.
    import torch
    from score_prompts import load_model, pick_device

    device = pick_device(args.device)
    print(f"Loading {args.model} on {device} ...")
    tok, model = load_model(args.model, device)
    use_chat = (not args.base) and tok.chat_template is not None
    modes = [m for m in args.modes.split(",") if m]
    if not use_chat and "free" in modes:
        print("No chat template: skipping free mode.")
        modes = [m for m in modes if m != "free"]

    with open(args.prompts, encoding="utf8") as f:
        rows = list(csv.DictReader(f))
    flagged_ids = []
    if args.flagged:
        flagged_ids = read_flagged_ids(args.flagged, args.model, args.max_flagged)
    selected = select_prompts(rows, args.per_group, args.seed, flagged_ids)
    n_sample = sum(src in ("sample", "both") for _, src in selected)
    print(f"{len(selected)} prompts ({n_sample} sample, {len(flagged_ids)} flagged), "
          f"modes: {modes}")

    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    @torch.no_grad()
    def gen_fn(text):
        enc = tok(text, return_tensors="pt", add_special_tokens=False).to(device)
        out = model.generate(**enc, max_new_tokens=args.max_new_tokens,
                             do_sample=False, pad_token_id=pad_id)
        return tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)

    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, f"gen_{args.model.replace('/', '__')}.csv")
    with open(out_path, "w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        run(selected, tok, use_chat, modes, args.model, gen_fn, writer)
    print(f"Done -> {out_path}")


if __name__ == "__main__":
    main()
