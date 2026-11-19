#!/usr/bin/env python3
"""Generate human-human split-half and uniform-response JSD references.

Run from any directory with:
  python3 P2_Human_Benchmark_Reference.py --data /path/to/ZA10020_v2-0-0.dta

Requires Python 3, pandas, and numpy. Outputs are additive and the script
refuses to overwrite either destination.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = ROOT / "P2_Human_Benchmark_Reference.csv"
DEFAULT_QA = ROOT / "P2_Human_Benchmark_Reference_QA.md"
COUNTRIES = [
    {"name": "Germany", "code": 276, "language": None, "expected_n": 1399, "q10_main": 1252, "q10_robust": 1289},
    {"name": "Austria", "code": 40, "language": None, "expected_n": 1546, "q10_main": 1429, "q10_robust": 1436},
    {"name": "Switzerland", "code": 756, "language": "deu (German)", "expected_n": 2129, "q10_main": 2039, "q10_robust": 2041},
    {"name": "USA", "code": 840, "language": "eng (English)", "expected_n": 1534, "q10_main": 1467, "q10_robust": 1469},
    {"name": "Australia", "code": 36, "language": None, "expected_n": 1015, "q10_main": 911, "q10_robust": 917},
    {"name": "Canada", "code": 124, "language": "eng (English)", "expected_n": 1342, "q10_main": 1338, "q10_robust": 1338},
]
ITEMS = [
    {"id": "Q1", "variable": "v1", "topic": "Internet use frequency", "codes": list(range(1, 8))},
    {"id": "Q10d", "variable": "v26", "topic": "Ability to learn new software/apps", "codes": list(range(1, 6))},
    {"id": "Q17a", "variable": "v42", "topic": "Technology makes life easier", "codes": list(range(1, 6))},
    {"id": "Q20", "variable": "v47", "topic": "Most important source of political news", "codes": list(range(1, 7))},
    {"id": "Q23a", "variable": "v54", "topic": "Signed a petition in the last 12 months", "codes": list(range(1, 5))},
    {"id": "Q28a", "variable": "v64", "topic": "Government right to use video surveillance in public areas", "codes": list(range(1, 5))},
    {"id": "Q34", "variable": "v72", "topic": "Who benefits more from digital technology", "codes": list(range(1, 5))},
    {"id": "Q36a", "variable": "v74", "topic": "Comfort with a robot performing a medical operation", "codes": list(range(0, 11))},
]
WEIGHT_VARS = ["DWEIGHT_HH", "DWEIGHT_TS", "DWEIGHT_COM", "PSWEIGHT", "WEIGHT_COM"]
EXPECTED_Q10D_DIAGNOSTICS = {
    "Germany": {"q1_7": 67, "v26_-4": 56, "v26_3_among_q1_7": 3, "v26_4_among_q1_7": 2, "v26_5_among_q1_7": 6},
}
WEIGHT_DOCS = {
    "Germany": "ZA10020_backgroundvar_de.pdf, p. 62: weighting/construction statements conflict.",
    "Austria": "ZA10020_backgroundvar_at.pdf, p. 51: PSWEIGHT listed, but construction note says no weighting.",
    "Switzerland": "ZA10020_backgroundvar_ch.pdf, pp. 87–88: equal selection probability/no weighting; this does not validate the German-interview restriction as representative.",
    "USA": "ZA10020_backgroundvar_us.pdf, pp. 63–64: design/post-stratification material conflicts with construction statements; English-subset suitability is unresolved.",
    "Australia": "ZA10020_backgroundvar_au.pdf, pp. 60–61: PSWEIGHT listed, but construction note says no weighting.",
    "Canada": "ZA10020_backgroundvar_ca.pdf, pp. 61–62: PSWEIGHT for ten-province adult population estimates; English-interview-subset calibration is not established.",
}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def jensen_shannon(p: np.ndarray, q: np.ndarray) -> float:
    """Jensen-Shannon divergence in bits (logarithm base 2)."""
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    if p.shape != q.shape or p.ndim != 1:
        raise ValueError("JSD vectors must be same-length one-dimensional arrays")
    if np.any(p < 0) or np.any(q < 0) or not np.isclose(p.sum(), 1) or not np.isclose(q.sum(), 1):
        raise ValueError("JSD inputs must be probability vectors")
    m = (p + q) / 2
    p_mask, q_mask = p > 0, q > 0
    return float(0.5 * np.sum(p[p_mask] * np.log2(p[p_mask] / m[p_mask]))
                 + 0.5 * np.sum(q[q_mask] * np.log2(q[q_mask] / m[q_mask])))


def code_key(value) -> str:
    if pd.isna(value):
        return "SYSMIS"
    n = int(value)
    return str(n) if float(value) == n else str(value)


def code_counts(series: pd.Series, included: set[int]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value, count in series.value_counts(dropna=False).items():
        key = code_key(value)
        if key == "SYSMIS" or not (key.lstrip("-").isdigit() and int(key) in included):
            counts[key] = int(count)
    return dict(sorted(counts.items(), key=lambda kv: (kv[0] == "SYSMIS", kv[0])))


def make_rng(seed: int, country_i: int, item_i: int, view_i: int) -> np.random.Generator:
    # Independent deterministic streams keep results stable if other cells are added.
    return np.random.default_rng(np.random.SeedSequence([seed, country_i, item_i, view_i]))


def split_half_jsds(values: np.ndarray, categories: list[int], iterations: int,
                    rng: np.random.Generator) -> tuple[np.ndarray, int, int]:
    n = len(values)
    half = n // 2
    if half == 0:
        return np.array([], dtype=float), 0, n
    out = np.empty(iterations, dtype=float)
    used_n = 2 * half
    for i in range(iterations):
        selected = values[rng.permutation(n)[:used_n]]
        left, right = selected[:half], selected[half:]
        p = np.array([(left == code).sum() / half for code in categories], dtype=float)
        q = np.array([(right == code).sum() / half for code in categories], dtype=float)
        out[i] = jensen_shannon(p, q)
    return out, half, n - used_n


def distribution(values: np.ndarray, categories: list[int]) -> tuple[np.ndarray, np.ndarray]:
    counts = np.array([(values == code).sum() for code in categories], dtype=int)
    n = int(counts.sum())
    if n == 0:
        return counts, np.zeros(len(categories), dtype=float)
    return counts, counts / n


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, help="Path to the pooled ISSP 2024 Release 2.0.0 DTA file")
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV, help=f"New CSV output (default: {DEFAULT_CSV})")
    parser.add_argument("--qa-output", type=Path, default=DEFAULT_QA, help=f"New QA Markdown output (default: {DEFAULT_QA})")
    parser.add_argument("--seed", type=int, default=20261117, help="Base seed for per-country/item/view split streams")
    parser.add_argument("--iterations", type=int, default=1000, help="Split-half repetitions (default: 1000)")
    parser.add_argument("--expected-version", default="2.0.0 (2026-10-16)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_path = Path(args.data).expanduser().resolve()
    csv_path = args.csv_output.expanduser().resolve()
    qa_path = args.qa_output.expanduser().resolve()
    if args.iterations < 1:
        raise ValueError("--iterations must be at least 1")
    if not data_path.is_file():
        raise FileNotFoundError(f"DTA file not found: {data_path}")
    if csv_path == qa_path or csv_path == data_path or qa_path == data_path:
        raise ValueError("Input DTA and the two output paths must be distinct")
    existing = [str(p) for p in (csv_path, qa_path) if p.exists()]
    if existing:
        raise FileExistsError("Refusing to overwrite existing output(s): " + ", ".join(existing))

    reader = pd.io.stata.StataReader(str(data_path), convert_categoricals=False)
    value_labels = reader.value_labels()
    variable_labels = reader.variable_labels()
    required = {"version", "country", "INTLANG", "v1", "v26", *(i["variable"] for i in ITEMS)}
    for item in ITEMS:
        label_key = item["variable"].upper()
        if label_key not in value_labels:
            raise ValueError(f"No Stata value-label map found for {item['variable']}")
        available_codes = {int(k) for k in value_labels[label_key]}
        if not set(item["codes"]).issubset(available_codes):
            raise ValueError(f"Declared substantive code missing from DTA label map for {item['variable']}")
    df = pd.read_stata(str(data_path), convert_categoricals=False)
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError("DTA is missing required variables: " + ", ".join(missing))
    versions = df["version"].dropna().astype(str).unique().tolist()
    if versions != [args.expected_version]:
        raise ValueError(f"Unexpected DTA version value(s): {versions}; expected {args.expected_version!r}")
    source_hash = file_sha256(data_path)

    selected: dict[str, pd.DataFrame] = {}
    observed_language: dict[str, dict[str, int]] = {}
    for country in COUNTRIES:
        all_country = df.loc[df["country"] == country["code"]]
        observed_language[country["name"]] = {
            str(k): int(v) for k, v in all_country["INTLANG"].value_counts(dropna=False).items()
        }
        sample = all_country if country["language"] is None else all_country.loc[all_country["INTLANG"] == country["language"]]
        if len(sample) != country["expected_n"]:
            raise ValueError(f"{country['name']} selected N={len(sample)}, expected {country['expected_n']}; stopping without outputs")
        selected[country["name"]] = sample.reset_index(drop=True)

    rows: list[dict[str, object]] = []
    validations: list[tuple[str, bool, str]] = []
    split_cache: dict[tuple[str, str, str], np.ndarray] = {}
    for ci, country in enumerate(COUNTRIES):
        sample = selected[country["name"]]
        for ii, item in enumerate(ITEMS):
            variable = item["variable"]
            codes = item["codes"]
            labels_map = value_labels[variable.upper()]
            labels = [str(labels_map[code]) for code in codes]
            raw = sample[variable]
            selected_code_counts = code_counts(raw, set(codes))
            views: list[tuple[str, pd.Series, int]]
            if item["id"] == "Q10d":
                main_mask = sample["v1"].between(1, 6, inclusive="both") & raw.isin(codes)
                robust_mask = raw.isin(codes)
                views = [("main_q1_1_6_and_q10d_1_5", raw.loc[main_mask], 0),
                         ("robustness_all_substantive_q10d", raw.loc[robust_mask], 1)]
            else:
                series = raw.loc[raw.isin(codes)]
                views = [("substantive_responses", series, 0)]
            for view, response_series, vi in views:
                values = response_series.to_numpy(dtype=int)
                counts, survey_p = distribution(values, codes)
                n = int(counts.sum())
                non_sub = code_counts(raw, set(codes))
                uniform = np.full(len(codes), 1 / len(codes), dtype=float)
                random_jsd = jensen_shannon(survey_p, uniform) if n else float("nan")
                h_rng = make_rng(args.seed, ci, ii, vi)
                h_jsds, half_n, odd_omitted = split_half_jsds(values, codes, args.iterations, h_rng)
                if h_jsds.size:
                    h_stats = {
                        "mean_jsd": float(h_jsds.mean()),
                        "median_jsd": float(np.median(h_jsds)),
                        "sd_jsd": float(h_jsds.std(ddof=1)) if len(h_jsds) > 1 else 0.0,
                        "p2_5_jsd": float(np.quantile(h_jsds, 0.025)),
                        "p97_5_jsd": float(np.quantile(h_jsds, 0.975)),
                    }
                else:
                    h_stats = {k: float("nan") for k in ("mean_jsd", "median_jsd", "sd_jsd", "p2_5_jsd", "p97_5_jsd")}
                q1_eligible_n = int(sample["v1"].between(1, 6, inclusive="both").sum()) if item["id"] == "Q10d" else ""
                robustness_n = int(raw.isin(codes).sum()) if item["id"] == "Q10d" else ""
                main_n = int((sample["v1"].between(1, 6, inclusive="both") & raw.isin(codes)).sum()) if item["id"] == "Q10d" else ""
                q1_counts = code_counts(sample["v1"], set(range(1, 7))) if item["id"] == "Q10d" else {}
                row_common = {
                    "country": country["name"], "item_id": item["id"], "variable": variable,
                    "topic": item["topic"], "denominator_view": view,
                    "selected_sample_n": len(sample), "analysis_denominator_n": n,
                    "substantive_n_in_selected_sample": int(raw.isin(codes).sum()),
                    "q1_codes_1_6_screen_n": q1_eligible_n,
                    "q10d_main_denominator_n": main_n, "q10d_robustness_denominator_n": robustness_n,
                    "substantive_category_codes_json": json.dumps(codes),
                    "substantive_category_labels_json": json.dumps(labels, ensure_ascii=False),
                    "survey_counts_by_category_json": json.dumps(counts.tolist()),
                    "survey_probabilities_by_category_json": json.dumps(survey_p.tolist()),
                    "uniform_probabilities_by_category_json": json.dumps(uniform.tolist()),
                    "selected_sample_non_substantive_code_counts_json": json.dumps(non_sub, ensure_ascii=False, sort_keys=True),
                    "selected_sample_q1_screen_code_counts_json": json.dumps(q1_counts, ensure_ascii=False, sort_keys=True),
                    "source_variable_label": variable_labels.get(variable, ""),
                    "source_release": args.expected_version, "source_sha256": source_hash,
                    "jsd_log_base": 2,
                }
                rows.append({**row_common, "benchmark_type": "human_human_split_half", **h_stats,
                             "split_half_group_n": half_n,
                             "respondents_randomly_omitted_per_split_if_odd": odd_omitted,
                             "base_seed": args.seed, "iterations": args.iterations,
                             "reference_probability_vector_json": "", "n_substantive_categories": len(codes),
                             "random_baseline_jsd_exact": "", "statistic_note": "Repeated equal-sized respondent splits; empirical reference, not a theoretical bound."})
                rows.append({**row_common, "benchmark_type": "uniform_random_vs_survey", "mean_jsd": random_jsd,
                             "median_jsd": random_jsd, "sd_jsd": 0.0 if n else float("nan"),
                             "p2_5_jsd": random_jsd, "p97_5_jsd": random_jsd,
                             "split_half_group_n": "",
                             "respondents_randomly_omitted_per_split_if_odd": "",
                             "base_seed": "", "iterations": "",
                             "reference_probability_vector_json": json.dumps(uniform.tolist()),
                             "n_substantive_categories": len(codes), "random_baseline_jsd_exact": random_jsd,
                             "statistic_note": "Deterministic JSD of the observed survey distribution and a uniform vector; not a mathematical lower bound."})
                count_ok = int(counts.sum()) == n
                prob_ok = (n == 0 and len(survey_p) == len(codes)) or (n > 0 and math.isclose(float(survey_p.sum()), 1.0, abs_tol=1e-12))
                jsd_ok = (not h_jsds.size or (np.all(h_jsds >= -1e-12) and np.all(h_jsds <= 1 + 1e-12))) and (not n or -1e-12 <= random_jsd <= 1 + 1e-12)
                validations.extend([
                    (f"{country['name']} {item['id']} {view}: response counts sum to denominator", count_ok, f"count sum={int(counts.sum())}; denominator={n}"),
                    (f"{country['name']} {item['id']} {view}: survey probabilities sum to one", prob_ok, f"sum={survey_p.sum():.15g}"),
                    (f"{country['name']} {item['id']} {view}: JSD values within [0,1] bits", bool(jsd_ok), f"uniform={random_jsd:.9g}; split-half range=" + (f"{h_jsds.min():.9g}–{h_jsds.max():.9g}" if h_jsds.size else "not calculable")),
                ])
                uniform_row = rows[-1]
                split_metadata_blank = all(uniform_row[k] == "" for k in (
                    "split_half_group_n", "respondents_randomly_omitted_per_split_if_odd",
                    "base_seed", "iterations"))
                validations.append((f"{country['name']} {item['id']} {view}: deterministic uniform row has no split metadata",
                                    split_metadata_blank, "Split-only metadata fields are blank on deterministic uniform row."))
                if item["id"] == "Q10d":
                    expected_n = country["q10_main"] if view.startswith("main_") else country["q10_robust"]
                    validations.append((f"{country['name']} Q10d {view}: expected denominator", n == expected_n, f"observed={n}; expected={expected_n}"))

    # Reconfirm the documented German discrepancy without recoding or excluding records.
    de = selected["Germany"]
    q7 = de.loc[de.v1 == 7, "v26"]
    de_expected = EXPECTED_Q10D_DIAGNOSTICS["Germany"]
    checks = {
        "q1_7": int((de.v1 == 7).sum()),
        "v26_-4": int((de.v26 == -4).sum()),
        "v26_3_among_q1_7": int((q7 == 3).sum()),
        "v26_4_among_q1_7": int((q7 == 4).sum()),
        "v26_5_among_q1_7": int((q7 == 5).sum()),
    }
    validations.append(("Germany Q10d routing discrepancy preserved", checks == de_expected, f"observed={checks}; expected={de_expected}"))
    expected_rows = sum(6 * (2 if i["id"] == "Q10d" else 1) * 2 for i in ITEMS)
    validations.append(("Output row count", len(rows) == expected_rows, f"observed={len(rows)}; expected={expected_rows}"))
    keys = [(r["country"], r["item_id"], r["denominator_view"], r["benchmark_type"]) for r in rows]
    validations.append(("Output keys unique", len(keys) == len(set(keys)), f"rows={len(keys)}; unique={len(set(keys))}"))
    if any(not ok for _, ok, _ in validations):
        failed = [f"{name}: {detail}" for name, ok, detail in validations if not ok]
        raise RuntimeError("Validation failed; no outputs written:\n" + "\n".join(failed))

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    qa_path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with csv_path.open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    qa_lines = [
        "# P2 Human Benchmark Reference — QA", "",
        f"Generated from ISSP 2024 Digital Societies Release {args.expected_version}.",
        f"Source DTA filename: `{data_path.name}` (SHA-256 `{source_hash}`).", "",
        f"Seed: `{args.seed}`; split-half repetitions per country × item × view: `{args.iterations}`; output rows: `{len(rows)}`.",
        "No weights were applied. The source data and existing workbooks were read only.", "",
        "## Selected sample and Q10d denominators", "",
        "| Country | Selected N | Q10d main N | Q10d robustness N | Observed interview-language values in full country sample |",
        "|---|---:|---:|---:|---|",
    ]
    for c in COUNTRIES:
        langs = "; ".join(f"{k}: {v}" for k, v in observed_language[c["name"]].items())
        qa_lines.append(f"| {c['name']} | {c['expected_n']:,} | {c['q10_main']:,} | {c['q10_robust']:,} | {langs} |")
    qa_lines += ["", "## Germany routing discrepancy", "",
                 f"Observed in the selected source sample: Q1=7 N={checks['q1_7']}; Q10d=-4 N={checks['v26_-4']}; among Q1=7, Q10d codes 3/4/5 = {checks['v26_3_among_q1_7']}/{checks['v26_4_among_q1_7']}/{checks['v26_5_among_q1_7']}. These records are retained in the source-based audit; the common main Q10d view excludes Q1=7, while the all-substantive robustness view includes its substantive Q10d answers.", "",
                 "## Weight documentation and data-field audit", "",
                 "| Country | Available fields / selected-sample distinct values | Q10d main field completeness | Documentation summary | Decision |",
                 "|---|---|---:|---|---|"]
    for c in COUNTRIES:
        sample = selected[c["name"]]
        weight_summary = []
        for var in WEIGHT_VARS:
            if var in sample:
                weight_summary.append(f"{var}: {sample[var].nunique(dropna=True)} distinct, {sample[var].notna().sum()}/{len(sample)} nonmissing")
        main_mask = sample.v1.between(1, 6, inclusive="both") & sample.v26.isin(range(1, 6))
        main = sample.loc[main_mask]
        main_complete = all(var in main and main[var].notna().all() for var in WEIGHT_VARS)
        qa_lines.append(f"| {c['name']} | {'; '.join(weight_summary)} | {'all five complete' if main_complete else 'one or more incomplete'} | {WEIGHT_DOCS[c['name']]} | No weight applied; no consistent subset-specific choice established. |")
    qa_lines += ["", "The six official background-variable documents are: `ZA10020_backgroundvar_de.pdf`, `_at.pdf`, `_ch.pdf`, `_us.pdf`, `_au.pdf`, and `_ca.pdf` (filenames as present in the local documentation/download folders). The field audit establishes availability/completeness, not that a weight is valid for these estimands. Canada’s `PSWEIGHT` recommendation applies to the documented ten-province adult population; its validity for the English-interview subset is not established. The German-interview Swiss and English-interview US/Canadian subset weight suitability likewise remains unresolved.", "",
                 "## Validation checks", "", "| Check | Result | Evidence |", "|---|---|---|"]
    qa_lines += [f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |" for name, ok, detail in validations]
    qa_lines += ["", "## Limitations and interpretation", "",
                 "- Human-human split-half JSD is a within-survey sampling variability reference, not a theoretical upper bound. Each repetition independently permutes the substantive respondent records; when N is odd, one randomly selected record is omitted from that repetition so group sizes are exactly equal.",
                 "- JSD uses base-2 logarithms. The inspected repository contains no implemented main-analysis JSD function or documented logarithm base, so base 2 is an explicit conventional choice for these new references and needs team confirmation before cross-project metric comparisons.",
                 "- The uniform baseline assigns probability `1/k` to each declared substantive response category, including categories with zero observed frequency. It is a descriptive reference, not a mathematical lower bound.",
                 "- The source samples and current unweighted benchmark definitions are preserved. No weighted estimates, LLM inference, or model-output comparisons were produced.",
                 "- Q10d compares a human denominator defined by observed Q1 codes 1–6 and substantive Q10d codes 1–5 with an LLM prompt condition that states recent internet use (`You have used the Internet in the last 12 months.` / `Sie haben in den letzten 12 Monaten das Internet genutzt.`). The prompt does not operationalize the respondent-level Q1 code filter; this is an interpretation limitation, not changed here.",
                 "- An optional empirical resampling sensitivity analysis could repeatedly draw `n` responses from the observed country-item empirical probabilities and compare each draw with the original distribution. It is not included in the uniform baseline or this CSV.", ""]
    with qa_path.open("x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(qa_lines))

    # Read-back verification of the CSV's row count and one-to-one keys.
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        exported = list(csv.DictReader(f))
    if len(exported) != len(rows):
        raise RuntimeError(f"CSV read-back row count mismatch: {len(exported)} != {len(rows)}")
    exported_keys = [(r["country"], r["item_id"], r["denominator_view"], r["benchmark_type"]) for r in exported]
    if exported_keys != keys:
        raise RuntimeError("CSV read-back keys do not match calculated records")
    print(f"Wrote {csv_path} ({len(rows)} rows)")
    print(f"Wrote {qa_path}")
    print(f"All {len(validations)} validation checks passed; DTA SHA-256 {source_hash}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
