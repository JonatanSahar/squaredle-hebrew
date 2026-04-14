from squaredle.normalize import (
    fold_sofit,
    is_acceptable,
    normalize_word,
    strip_niqqud,
)


def test_strip_niqqud_removes_points() -> None:
    assert strip_niqqud("שָׁלוֹם") == "שלום"


def test_strip_niqqud_keeps_base() -> None:
    assert strip_niqqud("שלום") == "שלום"


def test_fold_sofit_maps_all_five() -> None:
    assert fold_sofit("ךםןףץ") == "כמנפצ"


def test_fold_sofit_midword() -> None:
    assert fold_sofit("שלום") == "שלומ"


def test_normalize_word_composes() -> None:
    assert normalize_word("שָׁלוֹם") == "שלומ"


def test_is_acceptable_rejects_gershayim() -> None:
    assert not is_acceptable('צה"ל')


def test_is_acceptable_rejects_geresh() -> None:
    assert not is_acceptable("ג'ינס")


def test_is_acceptable_rejects_hyphen() -> None:
    assert not is_acceptable("אי-שם")


def test_is_acceptable_rejects_short() -> None:
    assert not is_acceptable("שלו")


def test_is_acceptable_accepts_four() -> None:
    assert is_acceptable("שלומ")


def test_is_acceptable_rejects_non_hebrew() -> None:
    assert not is_acceptable("hello")
