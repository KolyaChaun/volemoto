import unicodedata

_CHAR_MAP: dict[str, str] = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "ґ": "g",
    "д": "d",
    "е": "e",
    "є": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "і": "i",
    "ї": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "sh",
    "ь": "",
    "ю": "yu",
    "я": "ya",
    # Russian-only
    "ё": "yo",
    "э": "e",
    "ъ": "",
    "ы": "i",
}


def has_cyrillic(text: str) -> bool:
    return any(unicodedata.name(ch, "").startswith("CYRILLIC") for ch in text)


def _transliterate(text: str) -> str:
    return "".join(_CHAR_MAP.get(ch.lower(), ch) for ch in text)


def normalize_query(query: str) -> list[str]:
    base = query.strip().lower()
    if not base:
        return []

    if not has_cyrillic(base):
        return [base]

    transliterated = _transliterate(base)
    if transliterated == base:
        return [base]

    return [base, transliterated]
