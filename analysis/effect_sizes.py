"""Continuous effect sizes for H1 and H2.

Reads the "JSD Summary" sheet of LLM_Survey_Comparison_with_JSD.xlsx and turns
the TRUE/FALSE hypothesis columns into signed differences (Δ), so that the size
and direction of each effect can be compared.

    Δ1 (H1) = JSD(non-matching prompt language) - JSD(matching prompt language)
              matching = DE for Germany/Austria/Switzerland, EN for USA/Australia/Canada
              Δ1 > 0 means the matching language is closer to the survey (supports H1)

    Δ2 (H2) = DE-EN JSD without persona (C1 vs C4) - DE-EN JSD with country persona
              Δ2 > 0 means the persona brings DE and EN answers closer (supports H2)

Usage (from the repository root):
    python analysis/effect_sizes.py
    python analysis/effect_sizes.py --xlsx LLM_Survey_Comparison_with_JSD.xlsx --out analysis/effect_sizes_out
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

GERMAN_SPEAKING = {"Germany", "Austria", "Switzerland"}
SMALL = 0.01  # |Δ| below this is counted as "negligible"

COLUMNS = [
    "item", "country", "model", "template",
    "jsd_de_persona", "jsd_en_persona", "delta_en_minus_de_persona", "better_persona", "h1_supported",
    "_blank",
    "jsd_de_no_persona", "jsd_en_no_persona", "delta_en_minus_de_no_persona", "better_no_persona",
    "lang_jsd_no_persona", "lang_jsd_persona", "h2_difference", "h2_supported",
]


def load(xlsx: Path) -> pd.DataFrame:
    df = pd.read_excel(xlsx, sheet_name="JSD Summary")
    df = df[df.iloc[:, 0].notna() & df.iloc[:, 2].notna()].copy()  # drop footer rows
    if df.shape[1] != len(COLUMNS):
        raise ValueError(f"Expected {len(COLUMNS)} columns in 'JSD Summary', found {df.shape[1]}")
    df.columns = COLUMNS
    df = df.drop(columns="_blank")
    num = ["jsd_de_persona", "jsd_en_persona", "lang_jsd_no_persona", "lang_jsd_persona"]
    df[num] = df[num].apply(pd.to_numeric)

    german = df["country"].isin(GERMAN_SPEAKING)
    df["country_language"] = np.where(german, "DE", "EN")
    df["jsd_matching"] = np.where(german, df["jsd_de_persona"], df["jsd_en_persona"])
    df["jsd_non_matching"] = np.where(german, df["jsd_en_persona"], df["jsd_de_persona"])
    df["delta1_h1"] = df["jsd_non_matching"] - df["jsd_matching"]
    df["delta2_h2"] = df["lang_jsd_no_persona"] - df["lang_jsd_persona"]
    return df


def summarize(series: pd.Series) -> pd.Series:
    return pd.Series({
        "n": len(series),
        "mean": series.mean(),
        "median": series.median(),
        "sd": series.std(),
        "n_positive": int((series > 0).sum()),
        "n_negligible_abs_lt_0.01": int((series.abs() < SMALL).sum()),
        "min": series.min(),
        "max": series.max(),
    })


def table(df: pd.DataFrame, col: str, by=None) -> pd.DataFrame:
    if by is None:
        return summarize(df[col]).to_frame("all").T
    return df.groupby(by)[col].apply(summarize).unstack()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--xlsx", default="LLM_Survey_Comparison_with_JSD.xlsx")
    ap.add_argument("--out", default="analysis/effect_sizes_out")
    args = ap.parse_args()

    df = load(Path(args.xlsx))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    keep = ["item", "country", "country_language", "model",
            "jsd_matching", "jsd_non_matching", "delta1_h1", "h1_supported",
            "lang_jsd_no_persona", "lang_jsd_persona", "delta2_h2", "h2_supported"]
    df[keep].to_csv(out / "deltas_long.csv", index=False)

    outputs = {
        "h1_overall.csv": table(df, "delta1_h1"),
        "h1_by_model.csv": table(df, "delta1_h1", "model"),
        "h1_by_item.csv": table(df, "delta1_h1", "item"),
        "h1_by_country_language.csv": table(df, "delta1_h1", "country_language"),
        "h1_by_model_x_country_language.csv": table(df, "delta1_h1", ["model", "country_language"]),
        "h2_overall.csv": table(df, "delta2_h2"),
        "h2_by_model.csv": table(df, "delta2_h2", "model"),
        "h2_by_item.csv": table(df, "delta2_h2", "item"),
    }
    for name, t in outputs.items():
        t.round(4).to_csv(out / name)

    pd.set_option("display.width", 200)
    for name in ["h1_overall.csv", "h1_by_model_x_country_language.csv", "h2_overall.csv", "h2_by_item.csv"]:
        print(f"\n== {name}")
        print(outputs[name].round(3).to_string())
    print(f"\nWrote {len(outputs) + 1} files to {out}/")


if __name__ == "__main__":
    main()
