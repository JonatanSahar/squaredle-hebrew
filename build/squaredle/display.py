FINAL_MAP = {"כ": "ך", "מ": "ם", "נ": "ן", "פ": "ף", "צ": "ץ"}


def to_display(word: str) -> str:
    if not word:
        return word

    last = word[-1]
    return word[:-1] + FINAL_MAP.get(last, last)
