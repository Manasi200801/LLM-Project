# H1 / H2 as effect sizes

`LLM_Survey_Comparison_with_JSD.xlsx` tests H1 and H2 by counting TRUE/FALSE cases (H1: 115 support vs 125 against; H2: 97 vs 143). A count treats a difference of 0.001 the same as one of 0.4. This folder replaces each TRUE/FALSE with the signed difference behind it, so we can see how large each effect is and which way it goes.

This is step 1 only: descriptive effect sizes, with no confidence intervals or p-values yet (see [Limitations](#limitations)).

## Definitions

All JSD values are Jensen–Shannon divergences (log base 2, range 0–1), taken from the `JSD Summary` sheet and averaged over templates and option orders.

| | Definition | > 0 means |
|---|---|---|
| **Δ1 (H1)** | JSD(prompt in the other language) − JSD(prompt in the country's language). The country's language is DE for Germany, Austria and Switzerland and EN for the USA, Australia and Canada. Uses the country-persona conditions. | The country's language is closer to the survey (supports H1) |
| **Δ2 (H2)** | DE–EN JSD without persona (C1 vs C4) − DE–EN JSD with the country persona | The persona makes DE and EN answers more similar (supports H2) |

A row counts as "negligible" when |Δ| < 0.01. For scale, model-to-survey JSDs are mostly between 0.1 and 0.25.

## Results

### H1: no language-matching effect, but a fixed language preference per model

Mean Δ1 across all 240 comparisons is **+0.001** (median −0.002, SD 0.108). On average, asking in the country's language does not bring the answers closer to the survey.

Single cases still range from −0.36 to +0.47. Splitting by the country's language shows why these large effects cancel out:

| Model | Mean Δ1, German-speaking countries | Mean Δ1, English-speaking countries |
|---|---|---|
| Llama 3.1 8B Instruct | **+0.084** | **−0.080** |
| Qwen2.5 7B Instruct | +0.031 | −0.024 |
| Llama 3.1 8B Base | −0.022 | +0.019 |
| EuroLLM 9B Instruct | −0.009 | +0.010 |
| Teuken 7B | −0.001 | −0.000 |

The signs flip between the two groups. Llama Instruct and Qwen are closer to the survey with German prompts **for every country**. Llama Base and EuroLLM are closer with English prompts for every country. What we see is a fixed language preference in each model, not an alignment between prompt language and country. Teuken is the only model with almost no language effect.

### H2: no persona effect overall; Q36a is the exception

Mean Δ2 is **−0.003** (median −0.002). In 103 of 240 comparisons |Δ2| < 0.01, so the persona changes almost nothing.

| Item | Mean Δ2 | Median Δ2 | Δ2 > 0 (of 30) |
|---|---|---|---|
| **Q36a** | **+0.029** | **+0.024** | **24** |
| Q34 | +0.011 | +0.003 | 17 |
| Q28a | +0.006 | −0.006 | 12 |
| Q17a | −0.003 | −0.000 | 15 |
| Q1 | −0.005 | −0.006 | 6 |
| Q20 | −0.006 | −0.005 | 12 |
| Q10d | −0.011 | −0.006 | 3 |
| Q23a | −0.043 | −0.003 | 8 |

Q36a (robots and AI) is the only item where the persona narrows the DE–EN gap consistently, in 24 of 30 cases. On Q23a, adding a persona widens the gap.

## Files

Running `python analysis/effect_sizes.py` from the repository root (needs `pandas` and `openpyxl`) rebuilds everything in `effect_sizes_out/`:

| File | Content |
|---|---|
| `deltas_long.csv` | One row per item × country × model, with Δ1, Δ2 and the original TRUE/FALSE columns |
| `h1_overall.csv`, `h1_by_model.csv`, `h1_by_item.csv`, `h1_by_country_language.csv`, `h1_by_model_x_country_language.csv` | Δ1 summaries |
| `h2_overall.csv`, `h2_by_model.csv`, `h2_by_item.csv` | Δ2 summaries |

Each summary gives n, mean, median, SD, the number of rows with Δ > 0 (this matches the TRUE count in the workbook), the number of negligible rows, min and max.

## Limitations

- **No uncertainty yet.** Δ1 values vary a lot (SD 0.108), so a mean of +0.001 alone does not show the true effect is near zero. Confidence intervals need a bootstrap that resamples items, prompt variants and survey respondents. That is the planned next step.
- **Rows are not independent.** Countries that share a language have similar survey distributions. For H2, the no-persona DE–EN JSD does not depend on the country, yet it appears in all six country rows of each model × item. The 240 rows therefore hold less information than their number suggests.
- **Inputs are averaged.** All values come from distributions averaged over templates and option orders. Models with strong position bias (Qwen) look more spread out after averaging than any single prompt is.
