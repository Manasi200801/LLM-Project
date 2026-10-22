"""
Shared word lists and classifiers for refusal_analysis.py and refusal_generate.py.

Pure Python, no dependencies, so both scripts can import it anywhere.

Everything here is a heuristic. Extend the lists after reading
nonletter_tokens.csv and the generated texts. refusal_analysis.py also accepts
--extra_words with a text file (one word per line) to add words without
editing this file.
"""
import re

# First words of typical refusals. Lowercase. Used for the first next token.
REFUSAL_WORDS = {
    # English
    "i", "i'm", "i’m", "sorry", "as", "unfortunately", "apologies", "apologize",
    "cannot", "can't", "can’t", "unable", "no", "none", "neither",
    # German
    "ich", "leider", "entschuldigung", "tut", "als", "bedauerlicherweise",
    "entschuldigen", "keine", "kein", "nein",
}

# Hedging openers. Not a refusal, but also not an answer letter.
HEDGE_WORDS = {
    "it", "this", "that", "however", "depends", "well", "hmm", "perhaps",
    "es", "das", "dies", "diese", "kommt", "vielleicht", "hmm", "also",
}

# Phrases that mark a refusal in generated text. Lowercase, straight apostrophes.
REFUSAL_PHRASES = [
    # English
    "i cannot", "i can't", "i can not", "i'm sorry", "i am sorry", "i'm unable",
    "i am unable", "i won't", "i do not have personal", "i don't have personal",
    "i do not have opinions", "i don't have opinions", "as an ai", "as a language model",
    "as an artificial", "not able to", "not appropriate", "i'm not able",
    "i am not able", "i do not feel comfortable", "i don't feel comfortable",
    "i must decline", "i refuse", "no personal opinion",
    # German
    "ich kann nicht", "ich kann keine", "ich kann diese", "ich darf nicht",
    "es tut mir leid", "tut mir leid", "leider kann", "leider nicht",
    "als ki", "als sprachmodell", "als künstliche", "ich habe keine persönliche",
    "ich habe keine meinung", "ich bin nicht in der lage", "ich möchte nicht",
]


def load_words(path):
    """Read extra words, one per line. Empty lines and lines starting with # are skipped."""
    words = set()
    with open(path, encoding="utf8") as f:
        for line in f:
            line = line.strip().lower()
            if line and not line.startswith("#"):
                words.add(line)
    return words


def classify_token(token, letters, refusal_words=REFUSAL_WORDS):
    """Put one next token into a coarse category.

    letters is the set of valid answer letters for this prompt.
    """
    t = token.strip()
    if not t:
        return "whitespace"
    if t in letters:
        return "answer_letter"
    if len(t) == 1 and t.upper() in letters:
        return "lowercase_letter"
    if t.isdigit():
        return "number"
    word = t.strip("*_\"'`„“”«»()[].,:;!?").lower()
    if word in refusal_words:
        return "refusal_like"
    if word in HEDGE_WORDS:
        return "hedge_like"
    if not any(c.isalnum() for c in t):
        return "formatting"
    return "other_word"


# An answer starts with one letter that stands alone: "A", "A.", "(A)", "**A**",
# "A:" or "A" followed by a line break. A letter followed by a space is not
# accepted, because "I cannot" and "A person" start the same way.
_ANSWER_RE = re.compile(r"^[\W_]*([A-Za-z])(?=$|\n|[.)\]:*])")


def classify_generation(text, letters):
    """Label a generated text.

    answer            starts with a valid answer letter
    answer_lowercase  starts with a lowercase version of a valid letter
    invalid_letter    starts with a letter that is not an option for this item
    refusal           contains a refusal phrase in its first 200 characters
    empty             nothing generated
    other             anything else, for example the option text without a letter
    """
    t = text.strip()
    if not t:
        return "empty"
    m = _ANSWER_RE.match(t)
    if m:
        ch = m.group(1)
        if ch in letters:
            return "answer"
        if ch.isupper():
            return "invalid_letter"
        if ch.upper() in letters:
            return "answer_lowercase"
    head = t.lower().replace("’", "'")[:200]
    if any(p in head for p in REFUSAL_PHRASES):
        return "refusal"
    return "other"
