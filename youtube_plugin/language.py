"""Lightweight language identification for filtering a VOC corpus.

Why a heuristic rather than a library: the core is stdlib-only, and the job here is
narrow. We are not translating or doing linguistics, we are answering "is this comment
plausibly in a language the researcher reads". A stopword-and-script heuristic does
that well enough, and its mistakes are visible because every drop is audited with the
language it thought it saw.

The governing rule is DO NOT DROP ON WEAK EVIDENCE. A short comment carries too little
signal to classify, so it is returned as "unknown" and kept. Losing a real customer
line to an over-eager filter is a worse outcome than keeping a stray foreign one,
because the drop is invisible at the point where it matters.
"""

from __future__ import annotations

import re
import unicodedata

MIN_WORDS_FOR_CONFIDENCE = 6

# Non-Latin scripts are unambiguous, so a run of them settles the question.
SCRIPT_RANGES = {
    "zh": [(0x4E00, 0x9FFF), (0x3400, 0x4DBF)],
    "ja": [(0x3040, 0x309F), (0x30A0, 0x30FF)],
    "ko": [(0xAC00, 0xD7AF), (0x1100, 0x11FF)],
    "ar": [(0x0600, 0x06FF), (0x0750, 0x077F)],
    "ru": [(0x0400, 0x04FF)],
    "he": [(0x0590, 0x05FF)],
    "th": [(0x0E00, 0x0E7F)],
    "hi": [(0x0900, 0x097F)],
    "el": [(0x0370, 0x03FF)],
}

# Function words. Deliberately common and short: they appear in almost any real
# sentence, which is what makes them discriminating on comment-length text.
STOPWORDS = {
    "en": {"the", "and", "is", "to", "of", "it", "you", "that", "for", "have", "with",
           "this", "but", "not", "are", "was", "my", "on", "in", "we", "they", "would"},
    "de": {"und", "der", "die", "das", "ich", "nicht", "mit", "ein", "eine", "auch",
           "habe", "war", "zu", "von", "ist", "sich", "dem", "den", "aber", "wie"},
    "es": {"el", "la", "de", "que", "los", "las", "por", "para", "con", "una", "es",
           "en", "un", "se", "no", "muy", "pero", "como", "mas", "hay"},
    "fr": {"le", "la", "les", "de", "des", "et", "est", "pour", "avec", "une", "un",
           "que", "qui", "dans", "pas", "sur", "vous", "nous", "mais", "plus"},
    "pt": {"o", "a", "os", "as", "de", "que", "para", "com", "uma", "um", "nao",
           "por", "mais", "como", "mas", "muito", "eu", "voce", "isso", "esta"},
    "it": {"il", "la", "di", "che", "per", "con", "una", "un", "non", "sono", "come",
           "piu", "ma", "anche", "questo", "sono", "hanno", "molto", "delle", "nel"},
    "nl": {"de", "het", "een", "en", "van", "is", "dat", "op", "te", "voor", "met",
           "niet", "aan", "die", "maar", "ook", "als", "zijn", "heb", "wat"},
}

WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def _strip_mentions(text: str) -> str:
    """Drop @handles and URLs, which are language-neutral noise that skews scoring."""
    text = re.sub(r"@[\w.\-]+", " ", text)
    return re.sub(r"https?://\S+", " ", text)


def _dominant_script(text: str) -> str | None:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return None
    counts: dict[str, int] = {}
    for char in letters:
        point = ord(char)
        for lang, ranges in SCRIPT_RANGES.items():
            if any(lo <= point <= hi for lo, hi in ranges):
                counts[lang] = counts.get(lang, 0) + 1
                break
    if not counts:
        return None
    lang, hits = max(counts.items(), key=lambda kv: kv[1])
    return lang if hits / len(letters) >= 0.30 else None


def detect(text: str) -> tuple[str, float]:
    """Return (language_code, confidence 0..1). 'unknown' means keep it.

    Confidence is the winning language's share of matched stopwords, which is a
    rough but honest signal: 1.0 means every function word matched one language.
    """
    cleaned = _strip_mentions(text)

    script = _dominant_script(cleaned)
    if script:
        return script, 0.95

    words = [w.lower() for w in WORD_RE.findall(unicodedata.normalize("NFKD", cleaned))]
    words = ["".join(c for c in w if not unicodedata.combining(c)) for w in words]
    if len(words) < MIN_WORDS_FOR_CONFIDENCE:
        return "unknown", 0.0

    scores = {lang: sum(w in stops for w in words) for lang, stops in STOPWORDS.items()}
    total = sum(scores.values())
    if total == 0:
        return "unknown", 0.0

    best, hits = max(scores.items(), key=lambda kv: kv[1])
    confidence = hits / total

    # A near-tie is not evidence. English shares function words with several
    # neighbours, so demand a clear win before calling it anything.
    ranked = sorted(scores.values(), reverse=True)
    if len(ranked) > 1 and ranked[0] - ranked[1] < 2:
        return "unknown", 0.0
    return best, round(confidence, 2)


def matches(text: str, wanted: list[str]) -> tuple[bool, str, float]:
    """Should this text be kept for the requested languages?

    Returns (keep, detected, confidence). 'unknown' always keeps, by design.
    """
    detected, confidence = detect(text)
    if detected == "unknown":
        return True, detected, confidence
    return detected in wanted, detected, confidence
