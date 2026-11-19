# P2 Human Benchmark Reference Methods

## Purpose and scope

This note defines two unweighted empirical reference calculations for the six current ISSP 2024 Digital Societies benchmark samples and eight project items. The calculations are references for interpreting later LLM-to-survey distances. They do not alter the current survey benchmark, country filters, response categories, Q10d denominator policy, or prompt conditions. No model inference or weighting is used.

The source is the pooled respondent-level Stata file `ZA10020_v2-0-0.dta`, Release 2.0.0 (`2.0.0 (2026-10-16)`), DOI `10.4232/5.ZA10020.2.0.0`. The production script requires the file path at runtime and records its SHA-256 in the QA report and CSV.

## Country samples and language interpretation

The following filters are the existing approved benchmark definitions, not new decisions. A benchmark's respondent interview language is distinct from LLM prompt language. The research design compares German- and English-language prompts for a fixed country persona against the same country benchmark; this does not make a restricted interview-language subset representative of all residents.

| Country | Selected respondent sample | N | Full sample or restriction | Prompt languages compared against this fixed benchmark | Limitation |
|---|---|---:|---|---|---|
| Germany | Full country sample; observed `INTLANG` is `deu (German)` | 1,399 | Full country sample | German and English | German-only interview mode; no multilingual subgroup comparison. |
| Austria | Full country sample; observed `INTLANG` is `deu (German)` | 1,546 | Full country sample | German and English | German-only interview mode; no multilingual subgroup comparison. |
| Switzerland | `INTLANG == "deu (German)"` | 2,129 | Language-restricted | German and English, with the same fixed German-interview benchmark | Not the full multilingual Swiss sample (N=3,028) and not an English-interview estimate. Representativeness of this subset is not established. |
| USA | `INTLANG == "eng (English)"` | 1,534 | Language-restricted | German and English | Excludes 56 Spanish-interview respondents; the English subset is not shown by the available materials to represent all US residents. |
| Australia | Full country sample; observed `INTLANG` is `eng (English)` | 1,015 | Full country sample | German and English | English-only interview mode; no multilingual subgroup comparison. |
| Canada | `INTLANG == "eng (English)"` | 1,342 | Language-restricted | German and English | Excludes 273 French-interview respondents; representativeness of English-interview subset is not established. |

The values above were re-read from the actual pooled DTA. For the restricted samples, filters use the complete observed label, including the parenthetical language name; in particular Canada is not filtered by a literal `"eng"`.

## Items and response categories

The variables, project topic labels, and substantive codes match `prepare_language_matched_multicountry_workbook.mjs` and the `Item Crosswalk` / item sheets in `SurveyData_MultiCountry_LanguageMatched.xlsx`:

| Project item | DTA variable | Topic | Substantive codes |
|---|---|---|---|
| Q1 | `v1` | Internet use frequency | 1–7 |
| Q10d | `v26` | Ability to learn new software/apps | 1–5 |
| Q17a | `v42` | Technology makes life easier | 1–5 |
| Q20 | `v47` | Most important source of political news | 1–6 |
| Q23a | `v54` | Signed a petition in the last 12 months | 1–4 |
| Q28a | `v64` | Government right to use video surveillance in public areas | 1–4 |
| Q34 | `v72` | Who benefits more from digital technology | 1–4 |
| Q36a | `v74` | Comfort with a robot performing a medical operation | 0–10 |

The script obtains category labels from the DTA value-label metadata and checks that the declared substantive codes exist there. It retains the original category order above, including declared categories that have zero observations.

## Human-human split-half JSD

For every country × item, use the selected sample and retain records whose item response is in the declared substantive category set. Q10d is produced in two separately identified views:

1. **Main:** `v1`/Q1 is 1–6 **and** `v26`/Q10d is substantive 1–5. The denominator is the intersection N.
2. **Robustness:** `v26`/Q10d is substantive 1–5, regardless of `v1`. The denominator is all selected respondents with a substantive Q10d response.

For each view, each repetition randomly permutes the eligible substantive respondent records and separates them into two equal groups. For an odd N, one respondent is randomly left out for that repetition, so each half has `floor(N/2)` records; the omitted respondent can differ across repetitions. Empty declared categories remain as zero cells in each probability vector. If a future item/view has fewer than two substantive records, the split-half statistic is missing and the reason should be reported rather than calculated from empty groups.

The script computes JSD between the two empirical half-sample vectors for 1,000 repetitions by default and summarizes the replicate values with mean, median, sample standard deviation, 2.5th percentile, and 97.5th percentile. The seed defaults to `20261117`; independent deterministic random streams are derived from the seed and country/item/view index. The CSV records the seed and iteration count.

JSD is calculated as `0.5 KL(P || M) + 0.5 KL(Q || M)`, where `M=(P+Q)/2`, using base-2 logarithms. Results are in bits and lie between 0 and 1 for these distributions. **No JSD implementation or logarithm-base convention for the project's main LLM comparison was found in the inspected pipeline.** Base 2 is therefore an explicit conventional choice for this reference script and should be confirmed before direct numerical comparison to later LLM JSD values. The split-half distribution is a human-human variability reference; it is not a theoretical upper bound, not a human ceiling, and not an inferential confidence interval for a population parameter.

## Uniform random-response baseline

For each country × item × denominator view, define a uniform vector over the declared substantive categories: every category receives probability `1/k`, where `k` is the number of substantive categories. This includes categories with zero observed survey frequency. Compute one deterministic JSD between this vector and the corresponding unweighted empirical survey distribution. The CSV records the exact ordered category list, the survey count/probability vectors, the uniform probability vector, `k`, and the exact JSD. The summary columns for this deterministic calculation repeat that exact value; its standard deviation is zero because no random simulation is involved.

This is a descriptive “uniform answers” reference, not a mathematical lower bound: the uniform vector need not be maximally distant from the observed survey distribution, and other candidate distributions may have smaller or larger JSD. An optional, separate empirical-resampling sensitivity analysis could repeatedly draw `n` substantive responses from the observed country-item empirical probabilities and compare each resampled distribution with the original. That would characterize finite-sample resampling variation; it is not calculated here and must not be mixed with the uniform baseline.

## Missing values, special codes, and Q10d routing

The JSD calculations use substantive responses only. The CSV separately records the selected-sample counts for non-substantive original codes and system missing (`SYSMIS`), as well as the Q1 screen-code counts for Q10d. These values are not recoded into substantive categories. Special codes remain distinct in the source/workbook and in the diagnostic JSON fields: `-4` not applicable/filter, `-8` can’t choose, `-9` no answer, and any system missing. For Q20, any other declared special code (including the pooled Poland-specific `-6` label) is also kept outside the substantive vector and visible in diagnostics.

The Q10d main and robustness denominators remain those in the current workbook and methods note:

| Country | Main: Q1 1–6 and Q10d 1–5 | Robustness: all selected Q10d 1–5 |
|---|---:|---:|
| Germany | 1,252 | 1,289 |
| Austria | 1,429 | 1,436 |
| Switzerland | 2,039 | 2,041 |
| USA | 1,467 | 1,469 |
| Australia | 911 | 917 |
| Canada | 1,338 | 1,338 |

The common analytic Q1 rule is not identical to each country's actual questionnaire routing. The Austria form routes a missing Q1 response onward to Q10d (ZA10020_q_at.pdf, Q10, p. 8); the Canada Group A form routes a missing Q6 response onward to the skills battery (ZA10020_q_ca-en.pdf, Q15, p. 14). The common main denominator excludes those missing-screen cases, while observed substantive answers remain in the robustness view and routing audit. Other country-specific routes are recorded in the workbook `Item Crosswalk` and the methods QA note.

Germany's discrepancy remains untouched: Q1=7 N=67; Q10d `-4` N=56; among the 11 remaining Q1=7 cases, substantive Q10d codes 3/4/5 occur 3/2/6 times. Those substantive responses are excluded from the common main view because Q1 is 7 and are included in the all-substantive robustness view. This workflow reports the impact through separate denominators; it does not recode or delete the cases.

The LLM Q10d filter text currently states “You have used the Internet in the last 12 months.” / “Sie haben in den letzten 12 Monaten das Internet genutzt.” (`Prompts/build_prompts.py`, `FILTER_SENTENCE`). This gives the model recent-use context but does not operationalize an observed Q1/v1 code or reproduce the human respondent routing process. The human main benchmark is an observed respondent-level intersection; do not claim these populations are perfectly identical.

## Weight documentation and decision

The pooled DTA contains `DWEIGHT_HH`, `DWEIGHT_TS`, `DWEIGHT_COM`, `PSWEIGHT`, and `WEIGHT_COM`. Direct inspection found the fields nonmissing in each selected country sample and in each Q10d main denominator, but field availability does not establish estimand-specific suitability. Distinct-value counts by selected sample were:

| Country | DWEIGHT_HH | DWEIGHT_TS | DWEIGHT_COM | PSWEIGHT | WEIGHT_COM | Official background-variable documentation |
|---|---:|---:|---:|---:|---:|---|
| Germany | 1 | 2 | 2 | 1 | 2 | `ZA10020_backgroundvar_de.pdf`, p. 62: eastern-state weighting note conflicts with “No weighting” construction text. |
| Austria | 1 | 1 | 1 | 680 | 680 | `ZA10020_backgroundvar_at.pdf`, p. 51: `PSWEIGHT` is listed, but construction note says “No weighting.” |
| Switzerland | 1 | 1 | 1 | 1 | 1 | `ZA10020_backgroundvar_ch.pdf`, pp. 87–88: equal selection probability and weights of 1; no subset-specific representativeness evidence. |
| USA (English interviews) | 6 | 4 | 16 | 987 | 1,126 | `ZA10020_backgroundvar_us.pdf`, pp. 63–64: design/post-stratification material conflicts with construction text; English-subset suitability unresolved. |
| Australia | 1 | 1 | 1 | 56 | 56 | `ZA10020_backgroundvar_au.pdf`, pp. 60–61: `PSWEIGHT` is listed, but construction note says “No weighting.” |
| Canada (English interviews) | 1 | 1 | 1 | 266 | 266 | `ZA10020_backgroundvar_ca.pdf`, pp. 61–62: `PSWEIGHT` is recommended for adult population point estimates in the ten provinces; English-subset calibration is not established. |

The five pooled weight fields were complete for all selected respondents and for the Q10d main cases in the direct data check. This only establishes calculability, not validity. The current benchmark remains unweighted by project decision. Given documentary conflicts and missing evidence for the language-restricted estimands, no weighted sensitivity result is recommended at this stage. No weight is chosen or applied by the script.

## Reproduction and output schema

From the project root (or any working directory, since the script resolves its own default output paths), run with unused output filenames:

```sh
python3 P2_Human_Benchmark_Reference.py \
  --data /path/to/ZA10020_v2-0-0.dta \
  --csv-output /path/to/new/P2_Human_Benchmark_Reference.csv \
  --qa-output /path/to/new/P2_Human_Benchmark_Reference_QA.md \
  --seed 20261117 --iterations 1000
```

Requires Python 3, pandas, and numpy; no packages are installed by the script. It refuses to overwrite existing outputs. It produces two rows for each country × item × denominator view: `human_human_split_half` and `uniform_random_vs_survey`. For Q10d there are two views; for the other seven items there is one, giving 108 rows in total. Key columns include denominator/sample Ns; ordered category code/label, count, survey probability, and uniform probability vectors; selected-sample special/missing counts; Q10d screen diagnostics; split-half summary statistics; exact uniform-reference JSD; source release and hash. Seed, repetitions, half size, and odd-N omission metadata are populated only for split-half rows; they are blank for the deterministic uniform rows. See the generated QA report for validation results.

The corrected output set currently has filenames `P2_Human_Benchmark_Reference_Corrected.csv` and `P2_Human_Benchmark_Reference_QA_Corrected.md`. The earlier same-basename CSV and QA file are retained as pre-correction copies; their deterministic uniform rows still carry split-only metadata and should not be treated as current outputs.
