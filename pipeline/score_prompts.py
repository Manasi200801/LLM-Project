"""
Score survey prompts with an open-weights LLM and save answer distributions.

For every prompt in prompts.csv this script:
  1. builds the chat input (user message + assistant prefill "Answer:"/"Antwort:"),
  2. runs one forward pass,
  3. takes the softmax over the FULL vocabulary at the next position,
  4. sums the probability of each answer letter ("A", " A", "▁A", ...),
  5. maps letters back to the official option order (letter_to_original),
  6. writes one row per prompt with raw probs, outside mass and renormalized probs.

Usage (Mac, small test model):
  python score_prompts.py --model Qwen/Qwen2.5-0.5B-Instruct --prompts prompts.csv --out results --limit 6

Usage (cluster, full run):
  python score_prompts.py --model meta-llama/Llama-3.1-8B-Instruct --prompts prompts.csv --out results
"""
import argparse
import csv
import json
import os
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def pick_device(requested):
    if requested != "auto":
        return requested
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model(name, device):
    # Teuken's model card asks for the slow (sentencepiece) tokenizer.
    use_fast = "teuken" not in name.lower()
    tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True, use_fast=use_fast)
    if device == "cuda":
        dtype = torch.bfloat16
    elif device == "mps":
        dtype = torch.float16
    else:
        dtype = torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        name, torch_dtype=dtype, trust_remote_code=True
    ).to(device)
    model.eval()
    return tok, model


def letter_token_ids(tok, letters):
    """Find every vocabulary token that is exactly one answer letter.

    Covers 'A', ' A' (GPT-style tokenizers) and '▁A' (sentencepiece). A token
    only counts if it decodes to the letter after stripping whitespace, so
    multi-letter tokens like 'An' are never counted as 'A'.
    """
    ids = {}
    for letter in letters:
        found = set()
        for variant in (letter, " " + letter):
            enc = tok.encode(variant, add_special_tokens=False)
            if len(enc) == 1 and tok.decode(enc).strip() == letter:
                found.add(enc[0])
        for piece in (letter, "▁" + letter, "Ġ" + letter):
            tid = tok.convert_tokens_to_ids(piece)
            if isinstance(tid, int) and tid != tok.unk_token_id and tok.decode([tid]).strip() == letter:
                found.add(tid)
        if not found:
            raise ValueError(f"No single token found for letter {letter!r}")
        ids[letter] = sorted(found)
    return ids


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def build_input(tok, row, use_chat):
    """Return the exact text fed to the model.

    Chat models: apply the model's chat template to the user message, then
    append the prefill as the start of the assistant reply. Base models: use
    the plain prompt_text (user text + newline + cue).
    """
    if not use_chat:
        return row["prompt_text"]
    return chat_prefix(tok, row) + row["assistant_prefill"]


def chat_prefix(tok, row):
    """Chat template applied to the user message, ending where the assistant
    reply starts (no prefill yet).

    Most models have one chat template. Teuken has one template per language
    ("DE", "EN") and uses capitalized role names, as its model card shows:
    tokenizer.apply_chat_template(messages, chat_template="DE"). For such
    models we pick the template that matches the prompt language.
    """
    lang = row["language"]
    named = isinstance(tok.chat_template, dict)
    if named and lang not in tok.chat_template:
        raise ValueError(f"No chat template named {lang!r}; "
                         f"available: {list(tok.chat_template)}")
    role = "User" if "teuken" in (tok.name_or_path or "").lower() else "user"
    messages = [{"role": role, "content": row["user_text"]}]
    kwargs = {"chat_template": lang} if named else {}
    return tok.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True, **kwargs)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

@torch.no_grad()
def score_one(tok, model, device, text, letter_ids, top_k=10):
    enc = tok(text, return_tensors="pt", add_special_tokens=False).to(device)
    logits = model(**enc).logits[0, -1].float()
    probs = torch.softmax(logits, dim=-1)

    letter_probs = {
        letter: float(probs[ids].sum()) for letter, ids in letter_ids.items()
    }
    top = torch.topk(probs, top_k)
    top_tokens = [
        [tok.decode([i]), round(float(p), 4)]
        for i, p in zip(top.indices.tolist(), top.values.tolist())
    ]
    return letter_probs, top_tokens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompts", default="prompts.csv")
    ap.add_argument("--out", default="results")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--base", action="store_true",
                    help="Base (non-chat) model: skip the chat template")
    ap.add_argument("--limit", type=int, default=0,
                    help="Only score the first N prompts (for testing)")
    args = ap.parse_args()

    device = pick_device(args.device)
    print(f"Loading {args.model} on {device} ...")
    tok, model = load_model(args.model, device)
    use_chat = (not args.base) and tok.chat_template is not None
    if not args.base and not use_chat:
        print("Warning: tokenizer has no chat template, using plain prompt_text")

    with open(args.prompts, encoding="utf8") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[: args.limit]

    os.makedirs(args.out, exist_ok=True)
    safe_name = args.model.replace("/", "__")
    out_path = os.path.join(args.out, f"{safe_name}.csv")

    id_cache = {}
    fields = [
        "model", "prompt_id", "condition_id", "item_id", "language", "persona",
        "template_id", "n_options", "letter_probs", "outside_mass",
        "dist_official_order", "top_tokens", "input_text",
    ]
    t0 = time.time()
    with open(out_path, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, row in enumerate(rows, 1):
            letters = list(row["letters"])
            key = row["letters"]
            if key not in id_cache:
                id_cache[key] = letter_token_ids(tok, letters)
            text = build_input(tok, row, use_chat)
            letter_probs, top_tokens = score_one(tok, model, device, text, id_cache[key])

            total = sum(letter_probs.values())
            outside = max(0.0, 1.0 - total)
            # Renormalize over valid letters, then put into official option order.
            l2o = json.loads(row["letter_to_original"])
            dist = [0.0] * int(row["n_options"])
            for letter, p in letter_probs.items():
                dist[l2o[letter]] = p / total if total > 0 else 0.0

            w.writerow({
                "model": args.model,
                "prompt_id": row["prompt_id"],
                "condition_id": row["condition_id"],
                "item_id": row["item_id"],
                "language": row["language"],
                "persona": row["persona"],
                "template_id": row["template_id"],
                "n_options": row["n_options"],
                "letter_probs": json.dumps({k: round(v, 6) for k, v in letter_probs.items()}),
                "outside_mass": round(outside, 6),
                "dist_official_order": json.dumps([round(p, 6) for p in dist]),
                "top_tokens": json.dumps(top_tokens, ensure_ascii=False),
                "input_text": text,
            })
            print(f"[{i}/{len(rows)}] {row['prompt_id']}: outside={outside:.3f} "
                  f"top={top_tokens[0][0]!r} ({top_tokens[0][1]})")

    print(f"Done in {time.time() - t0:.1f}s -> {out_path}")


if __name__ == "__main__":
    main()
