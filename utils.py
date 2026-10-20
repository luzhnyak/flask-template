import re

_TRANSLITERATION = str.maketrans(
    {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "h",
        "ґ": "g",
        "д": "d",
        "е": "e",
        "є": "ie",
        "ж": "zh",
        "з": "z",
        "и": "y",
        "і": "i",
        "ї": "i",
        "й": "i",
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
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ь": "",
        "ю": "iu",
        "я": "ia",
        "ё": "e",
        "ъ": "",
        "ы": "y",
        "э": "e",
        "'": "",
        "’": "",
    }
)


def transliterate(text):
    """Create a URL-safe slug from a Ukrainian title or an existing alias."""
    text = (text or "").lower().translate(_TRANSLITERATION)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")
