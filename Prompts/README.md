# Prompt Design Notes

Notes for the team and draft text for the report. The prompts are built by `build_prompts.py` from `conditions.xlsx` and written to `prompts.csv`.

## Messages to the team

### To Person 4 (pipeline)

Answer options in the prompts use letters, not numbers. `Q36a` is an 11 point scale, so it uses A to K.

We use letters because "10" can start with the same token as "1", which would mix up the logprobs. Letters are single tokens and work the same for every item.

For chat models, use the `assistant_prefill` column ("Answer:" or "Antwort:") as the start of the assistant reply. Then the next token is the answer letter.

Read the logprob for each letter both with and without a leading space. The function `letter_probabilities` in `build_prompts.py` does this.

### To Person 5 (analysis)

Two points about the benchmark.

1. **No "Don't know" option.** We do not offer "Don't know" in the prompts. Please remove it from the survey data and renormalize the remaining shares. In the survey it is stored as a missing value, so the model and the survey would otherwise have different answer sets and the Jensen Shannon divergence would not be comparable. The German `Q1` also has no such box, so removing it keeps both languages equal.
2. **Internet users only for `Q10d`.** This item is asked only of people who used the internet in the last 12 months. Please filter the survey data the same way (exclude `Q1` = Never). Our prompt adds a sentence saying the persona has used the internet.

## Report text: deviations from the pitch

The project pitch served as our preregistration. We changed the following points after the instructor feedback.

### 1. Data source

We replaced WVS wave 7 with ISSP 2024 Digital Societies I (GESIS, ZA10020, released in September 2026). The instructor considered WVS wave 7 too old. To our knowledge, WVS wave 8 data for Germany was not available when we started.

The ESS has no US data, so it cannot support a Germany and US comparison. ISSP 2024 includes Germany, the US, and other German and English speaking countries.

Because the data appeared in 2026, it is also less likely to be part of the training data of our models. We cannot verify this, so we list it as a limitation.

### 2. Items

We use 8 items instead of the planned 10 to 15, one from each topic block:

* Technology attitudes (`Q17a`)
* Internet use (`Q1`)
* Digital skills (`Q10d`)
* Political news source (`Q20`)
* Civic engagement (`Q23a`)
* Perceived benefits for rich and poor (`Q34`)
* Government surveillance (`Q28a`)
* Robots and AI (`Q36a`)

A small set keeps every item documented and checked in both languages.

### 3. Wording

We use the official German (DE24) and US English (US24) questionnaire wording and do not translate items ourselves. This reduces translation error, which the instructor pointed out (Behr et al.).

### 4. Persona

We use one persona wording per country: "a person living in Germany" and "a person living in the United States". The pitch used "Leipzig resident" and "German persona" inconsistently.

### 5. Country neutral wording

`Q34` and `Q28a` name a country in the official text ("in Germany", "in America", "the German state", "the American government"). This would mix prompt language with the country named in the question.

We replaced these phrases with "in your country". In the no persona condition this phrase has no clear referent, which we list as a limitation.

### 6. Answer format and missing answers

Options are shown as letters, and the answer is read from the next token probabilities. The "Don't know" option is not shown, and the survey shares are renormalized without it. `Q10d` is restricted to internet users in both the prompt and the survey benchmark.

### 7. Design size

Six conditions (2 languages by 3 personas) and 8 items give 48 base prompts per model, before paraphrases and option order variations.

### 8. Known limitations to add

The US survey was fielded in 2024 and the German survey in 2025. Real respondents could answer "Don't know" while our models could not.