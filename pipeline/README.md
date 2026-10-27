# LLM scoring pipeline

This folder turns the prompts in `Prompts/prompts.csv` into answer distributions for each model, and checks how often models fail to answer.

| Script | What it does |
|---|---|
| `score_prompts.py` | One forward pass per prompt. Reads the probability of every answer letter and writes one distribution per prompt. Main results. |
| `refusal_analysis.py` | Summarizes non-answers from the `score_prompts.py` output (probability outside the answer letters, top tokens). |
| `refusal_generate.py` | Lets the model generate a short answer for a sample of prompts, with and without the answer cue, to find refusals the cue could hide. |
| `refusal_common.py` | Shared word lists and classifiers for the two refusal scripts. |

## Models

All runs used the exact Hugging Face snapshots below. Scores were produced on bwUniCluster 3.0, one NVIDIA A100 80GB per model, in bfloat16.

| Model | Hugging Face ID | Snapshot (commit) | Developer | Training data cutoff |
|---|---|---|---|---|
| Llama 3.1 8B Instruct | `meta-llama/Llama-3.1-8B-Instruct` | `0e9e39f249a16976918f6564b8830bc894c89659` | Meta (US) | Dec 2023 (model card) |
| Llama 3.1 8B (base) | `meta-llama/Llama-3.1-8B` | `d04e592bb4f6aa9cfee91e2e20afa771667e1d4b` | Meta (US) | Dec 2023 (model card) |
| Qwen2.5 7B Instruct | `Qwen/Qwen2.5-7B-Instruct` | `a09a35458c702b33eeacc393d103063234e8bc28` | Alibaba (China) | see model card |
| Teuken 7B Instruct v0.6 | `openGPT-X/Teuken-7B-instruct-v0.6` | `eb3cb8fdd396037c7029ee3b2087f54c415086ac` | OpenGPT-X (Germany), 24 EU languages | Sep 2023 (model card) |
| EuroLLM 9B Instruct | `utter-project/EuroLLM-9B-Instruct` | `f7ae2bc3bcbb538c0b93fa6cfbf388d9898b1ace` | UTTER project (EU), 35 languages | see model card |

Mistral 7B Instruct was on the original shortlist but was replaced by EuroLLM 9B: Mistral's model card makes no claim about German, so weak German answers could not be separated from a language effect.

Licenses: Llama 3.1 Community License (gated), Teuken CC BY-NC 4.0 (non-commercial research use), Qwen2.5 and EuroLLM Apache 2.0 (EuroLLM gated).

The ISSP 2024 data were released in September 2026, after the training cutoffs of all models listed with a known cutoff, so the models cannot have seen the survey results.

## How scoring works

For each prompt:

1. **Input.** Chat models get the prompt as a user message through the model's own chat template, followed by the cue `Answer:` (English) or `Antwort:` (German) as the start of the assistant reply. Base models (`--base`) get the plain prompt text plus cue, preceded by the model's start-of-text token.
2. **One forward pass.** No text is generated. We take the softmax over the full vocabulary at the position right after the cue.
3. **Letter probabilities.** For each answer letter (A, B, ...) we add up the probability of every token that is exactly that letter, with or without a leading space (`B`, ` B`, `▁B`).
4. **Outside mass.** `outside_mass = 1 − sum of letter probabilities` is the probability the model puts on anything that is not a valid answer. It is our measure of non-answers.
5. **Distribution.** The letter probabilities are divided by their sum (renormalized) and mapped back to the official questionnaire order with `letter_to_original`, so shuffled and reversed option orders line up with the survey codes.

**Teuken** has a separate chat template per language. The script picks `DE` or `EN` from the prompt's `language` column, as the model card requires. Teuken's template includes a fixed system message that differs between the German and English template ("Ein Gespräch zwischen einem Menschen und einem Assistenten..." / "A chat between a human and an artificial intelligence assistant..."). This is a small extra difference between the language conditions for this model only.

## Output: `results/<model>.csv`

One row per prompt (1,008 per model).

| Column | Meaning |
|---|---|
| `prompt_id`, `condition_id`, `item_id`, `language`, `persona`, `template_id`, `n_options` | Copied from `prompts.csv`. The option order (official, `rev`, `rotK`) is the suffix of `prompt_id`. |
| `letter_probs` | Raw probability per letter, as shown in the prompt (JSON). |
| `outside_mass` | Probability not on a valid letter. |
| `dist_official_order` | Renormalized distribution in the **official** answer order (JSON list). Compare this with the survey's substantive-only shares. |
| `top_tokens` | The 10 most likely next tokens with probabilities, for debugging. |
| `input_text` | Exact text the model saw. |

For the analysis, average `dist_official_order` over option orders and templates per model × condition × item before comparing with the survey. Some items show position bias.

## Running it

### Local test (Mac, small model)

```bash
conda activate llm4ess
python pipeline/score_prompts.py --model Qwen/Qwen2.5-0.5B-Instruct --prompts Prompts/prompts.csv --out results --limit 10
```

### Cluster setup (bwUniCluster 3.0, once)

```bash
module load devel/python/3.12.3-gnu-14.2 devel/cuda/12.8
python -m venv ~/llm4ess-env
source ~/llm4ess-env/bin/activate
pip install torch transformers accelerate pandas sentencepiece protobuf huggingface_hub
echo 'export HF_HOME=$HOME/hf_cache' >> ~/.bashrc
hf auth login                      # read token; needed for the gated models
hf download <model-id>             # on the login node; GPU nodes may have no internet
```

### Job script `run_model.sh`

```bash
#!/bin/bash
#SBATCH --job-name=llm4ess
#SBATCH --partition=dev_gpu_a100_il
#SBATCH --gres=gpu:1
#SBATCH --time=00:30:00
#SBATCH --output=logs/%x_%j.out

module load devel/python/3.12.3-gnu-14.2 devel/cuda/12.8
source ~/llm4ess-env/bin/activate
export HF_HOME=$HOME/hf_cache
export HF_HUB_OFFLINE=1
cd ~/LLM-Project
nvidia-smi
python pipeline/score_prompts.py --model "$1" --prompts Prompts/prompts.csv --out results
```

```bash
sbatch run_model.sh Qwen/Qwen2.5-7B-Instruct
```

For the base model, use a copy of the script with `--base` added (`run_base.sh`). One model takes 1–4 minutes on one A100.

### Refusal checks

```bash
python pipeline/refusal_analysis.py --results results --out refusal_out
# GPU job per model (run_refusal.sh):
python pipeline/refusal_generate.py --model <model-id> --prompts Prompts/prompts.csv \
    --flagged refusal_out/flagged_prompts.csv --out refusal_gen
python pipeline/refusal_analysis.py --results results --out refusal_out --gen refusal_gen
```

## Results of the checks (27 Oct 2026)

**Instruct models, scoring with the cue (main setup).** No prompt has `outside_mass` ≥ 0.2, and for no prompt is the most likely next token anything other than an answer letter.

| Model | Mean outside, DE | Mean outside, EN |
|---|---|---|
| Qwen2.5 7B | 0.0001 | 0.0000 |
| Llama 3.1 8B Instruct | 0.0113 | 0.0151 |
| Teuken 7B | 0.0313 | 0.0289 |
| EuroLLM 9B | 0.0123 | 0.0064 |

German–English differences are below one percentage point. They are statistically significant for three models (Wilcoxon, 504 matched pairs) but negligible in size.

The 3 prompts where the top token was `I` on an item with an option I (Q36a) were confirmed as answers by generation.

**Generation check (stratified sample, 56 prompts per model and language).** With the cue, all four models answered 100% of the time. Without the cue (free mode), answer rates were: Qwen 100%; Llama 96–98% (3.6% refusals in English); Teuken 100% in German, 88% in English (11% refusals); EuroLLM 93% in English, 25% in German. Most of EuroLLM's German non-answers are valid answers in a full sentence ("Die Antwort ist B. ...") or an opinion in words without a letter, which the classifier does not count as answers. Real refusals ("Ich habe keine Meinung zu diesem Thema, da ich ein KI-Sprachmodell bin...") are rare.

**Base model (Llama 3.1 8B).** Mean `outside_mass` 0.59 in German and 0.39 in English. The non-letter top tokens are almost all formatting: a blank line (`\n\n`, mostly German) or end of text (`<|end_of_text|>`, mostly English), not other answers. Distributions are renormalized as for the other models. A sensitivity check restricted to prompts with `outside_mass` < 0.5 is recommended.
