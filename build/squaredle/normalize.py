import unicodedata


NIQQUD_RANGE = (0x0591, 0x05C7)
SOFIT_MAP = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}
HEBREW_BASE = set("אבגדהוזחטיכלמנסעפצקרשת")
REJECT_CHARS = set('"\'־-\u05BE\u05F3\u05F4')


def strip_niqqud(s: str) -> str:
    return "".join(
        c for c in s if not (NIQQUD_RANGE[0] <= ord(c) <= NIQQUD_RANGE[1])
    )


def fold_sofit(s: str) -> str:
    return "".join(SOFIT_MAP.get(c, c) for c in s)


def normalize_word(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = strip_niqqud(s)
    s = fold_sofit(s)
    return s


def is_acceptable(raw: str) -> bool:
    if any(c in REJECT_CHARS for c in raw):
        return False

    norm = normalize_word(raw)
    if len(norm) < 4:
        return False

    return all(c in HEBREW_BASE for c in norm)
