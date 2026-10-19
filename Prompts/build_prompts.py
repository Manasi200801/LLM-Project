"""
Build base prompts from conditions.xlsx.

Reads two sheets:
  Conditions: Condition ID, Item ID, Language, Persona, Template ID
              (14 conditions: 2 languages x (no persona + 6 country personas))
  Items:      official wording per item and language (DE24 and US24)

Writes prompts.csv and prompts.jsonl (one row per condition x item x template x
option order).

Option orders (see ORDER_VARIANTS below):
  official  official order. prompt_id stays C2_Q17a_T1.
  rev       ordinal items, reversed order. prompt_id C2_Q17a_T1_rev.
  shufN     nominal items, fixed shuffled order. prompt_id C2_Q20_T1_shuf1.
Every variant has its own prompt_id, so results never overwrite each other.

Usage:
  python build_prompts.py conditions.xlsx
"""
import csv
import json
import math
import random
import re
import string
import sys

from openpyxl import load_workbook

# ---------------------------------------------------------------------------
# Settings the team can change
# ---------------------------------------------------------------------------

# Items where the country name in the official stem is replaced by the neutral
# stem from the Items sheet. Both Q34 and Q28a use the neutral stem.
NEUTRAL_ITEMS = {"Q34", "Q28a"}

# Nominal items can be shuffled later. Ordinal items only get reversed.
ITEM_TYPE = {
    "Q1": "ordinal", "Q10d": "ordinal", "Q17a": "ordinal", "Q20": "nominal",
    "Q23a": "nominal", "Q34": "nominal", "Q28a": "ordinal", "Q36a": "ordinal",
}

# Number of shuffled orders per nominal item. 1 means one extra order (shuf1).
N_SHUFFLES = 1

# Only the persona sentence and the instruction wording change between
# templates. Item text, stems and options never change. For paraphrases,
# add T2 and T3 here with the same keys.
#
# Persona keys must match the Persona column in conditions.xlsx. Every persona
# is written in both EN and DE, so each country can be asked in a matching and
# a non-matching language:
#   German speaking: Germany, Austria, Switzerland
#   English speaking: US, Australia, Canada
# Item wording stays DE24 for DE prompts and US24 for EN prompts for all
# countries. Only the persona sentence tells the model which country to answer
# for.
TEMPLATES = {
    "T1": {
        "EN": {
            "persona": {
                "Germany": "You are a person living in Germany.",
                "Austria": "You are a person living in Austria.",
                "Switzerland": "You are a person living in Switzerland.",
                "US": "You are a person living in the United States.",
                "Australia": "You are a person living in Australia.",
                "Canada": "You are a person living in Canada.",
                "none": "",
            },
            "instruction": "Answer with the letter of one option only.",
            "cue": "Answer:",
        },
        "DE": {
            "persona": {
                "Germany": "Sie sind eine Person, die in Deutschland lebt.",
                "Austria": "Sie sind eine Person, die in Österreich lebt.",
                "Switzerland": "Sie sind eine Person, die in der Schweiz lebt.",
                "US": "Sie sind eine Person, die in den USA lebt.",
                "Australia": "Sie sind eine Person, die in Australien lebt.",
                "Canada": "Sie sind eine Person, die in Kanada lebt.",
                "none": "",
            },
            "instruction": "Antworten Sie nur mit dem Buchstaben einer Antwortoption.",
            "cue": "Antwort:",
        },
    },
}

# Q10d is only asked of internet users, so the prompt says so.
FILTER_SENTENCE = {
    "Q10d": {
        "EN": "You have used the Internet in the last 12 months.",
        "DE": "Sie haben in den letzten 12 Monaten das Internet genutzt.",
    }
}

# The don't know option is never put into the prompt. The Items sheet keeps it
# in its own column only for documentation.

# ---------------------------------------------------------------------------
# Reading the workbook
# ---------------------------------------------------------------------------

def read_sheet(wb, name):
    ws = wb[name]
    rows = list(ws.iter_rows(values_only=True))
    header = [str(h).strip() for h in rows[0]]
    out = []
    for r in rows[1:]:
        if r is None or all(v is None for v in r):
            continue
        out.append({header[i]: ("" if v is None else str(v)) for i, v in enumerate(r)})
    return out


def parse_options(cell):
    """Return option labels in official order.

    Normal items are stored as '1 = label'. Scale items (Q36a) are stored as
    '0 = label', '1', '2', ..., '10 = label'. Those lines are kept as they are.
    """
    lines = [ln.strip() for ln in cell.split("\n") if ln.strip()]
    numbered = [re.match(r"^\d+ = (.*)$", ln) for ln in lines]
    if all(numbered):
        return [m.group(1) for m in numbered]
    return lines


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def order_variants(item_id, n):
    """Return a list of (order_id, order) for one item.

    official is always first. Ordinal items get one reversed order. Nominal
    items get N_SHUFFLES shuffled orders. The shuffle depends only on the item
    ID and the shuffle number, so every condition (all languages and personas)
    sees the same shuffled order for the same item. Shuffles are never the
    official order.
    """
    base = list(range(n))
    variants = [("official", base)]
    kind = ITEM_TYPE.get(item_id, "")
    if kind == "ordinal":
        variants.append(("rev", base[::-1]))
    elif kind == "nominal":
        for k in range(1, N_SHUFFLES + 1):
            rng = random.Random(f"{item_id}_shuf{k}")
            order = base[:]
            while order == base:
                rng.shuffle(order)
            variants.append((f"shuf{k}", order))
    return variants


def build_prompt(item, cond, template_id, order=None):
    """Build one prompt.

    order is an optional list of option indexes for later shuffling. Letters are
    assigned by position, and letter_to_original records the mapping so the
    analysis can map answers back to the official option order.
    """
    lang = cond["Language"]
    tpl = TEMPLATES[template_id][lang]

    labels = parse_options(item["Options (official order)"])
    n = len(labels)
    if n > len(string.ascii_uppercase):
        raise ValueError(f"Too many options for {item['Item ID']}")
    order = list(range(n)) if order is None else list(order)
    letters = list(string.ascii_uppercase[:n])
    shown = [labels[i] for i in order]
    letter_to_original = {letters[pos]: order[pos] for pos in range(n)}

    if any("don't know" in s.lower() or "can't choose" in s.lower()
           or "kann ich nicht sagen" in s.lower() for s in shown):
        raise ValueError(f"Don't know option found in {item['Item ID']} {lang}")

    parts = []

    persona = tpl["persona"][cond["Persona"]]
    if persona:
        parts.append(persona)

    filt = FILTER_SENTENCE.get(item["Item ID"], {}).get(lang)
    if filt:
        parts.append(filt)

    if item["Section intro"]:
        parts.append(item["Section intro"])

    neutral = item["Neutral stem for prompt"].replace("PROPOSAL: ", "").strip()
    if item["Item ID"] in NEUTRAL_ITEMS and neutral:
        stem = neutral
    else:
        stem = item["Question stem"]
    parts.append(stem)

    text = item["Item text"]
    if text and not (text.startswith("(") and text.endswith(")")):
        parts.append(text)

    parts.append("\n".join(f"{letters[i]}. {shown[i]}" for i in range(n)))
    parts.append(tpl["instruction"])

    user_text = "\n\n".join(parts)
    return {
        "user_text": user_text,
        "assistant_prefill": tpl["cue"],
        "prompt_text": user_text + "\n" + tpl["cue"],
        "letters": letters,
        "letter_to_original": letter_to_original,
        "n_options": n,
    }


def main(path):
    wb = load_workbook(path, data_only=True)
    conditions = read_sheet(wb, "Conditions")
    items = {(r["Item ID"], r["Language"]): r for r in read_sheet(wb, "Items")}

    rows = []
    for cond in conditions:
        key = (cond["Item ID"], cond["Language"])
        if key not in items:
            raise KeyError(f"No Items row for {key}")
        item = items[key]
        if cond["Persona"] not in TEMPLATES[cond["Template ID"]][cond["Language"]]["persona"]:
            raise KeyError(
                f"Persona '{cond['Persona']}' has no sentence for "
                f"{cond['Template ID']} {cond['Language']}. Add it to TEMPLATES.")
        n_opts = len(parse_options(item["Options (official order)"]))
        for order_id, order in order_variants(cond["Item ID"], n_opts):
            built = build_prompt(item, cond, cond["Template ID"], order)
            base_id = f"{cond['Condition ID']}_{cond['Item ID']}_{cond['Template ID']}"
            rows.append({
                "prompt_id": base_id if order_id == "official" else f"{base_id}_{order_id}",
                "condition_id": cond["Condition ID"],
                "item_id": cond["Item ID"],
                "language": cond["Language"],
                "persona": cond["Persona"],
                "template_id": cond["Template ID"],
                "scale_type": ITEM_TYPE.get(cond["Item ID"], ""),
                "n_options": built["n_options"],
                "letters": "".join(built["letters"]),
                "letter_to_original": json.dumps(built["letter_to_original"]),
                "user_text": built["user_text"],
                "assistant_prefill": built["assistant_prefill"],
                "prompt_text": built["prompt_text"],
                "order_id": order_id,
                "option_order": json.dumps(order),
            })

    ids = [r["prompt_id"] for r in rows]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise ValueError(f"Duplicate prompt_id values: {dupes[:5]}")

    with open("prompts.csv", "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open("prompts.jsonl", "w", encoding="utf8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"{len(rows)} prompts written")
    for oid in sorted({r["order_id"] for r in rows}):
        print(f"  {oid}: {sum(r['order_id'] == oid for r in rows)}")
    for lang in ("EN", "DE"):
        sample = next(r for r in rows if r["language"] == lang and r["persona"] == "Austria")
        print("\n" + "=" * 60)
        print(sample["prompt_id"])
        print(sample["prompt_text"])

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "conditions.xlsx")
