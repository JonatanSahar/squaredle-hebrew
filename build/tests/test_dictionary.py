from pathlib import Path

from squaredle.dictionary import load_dictionary


FIX = Path(__file__).parent / "fixtures"


def test_load_dictionary_intersects_and_normalizes() -> None:
    words = load_dictionary(
        hspell_path=FIX / "hspell_tiny.txt",
        freq_path=FIX / "freq_tiny.txt",
        freq_top_n=40,
        blacklist_path=FIX / "blacklist_tiny.txt",
    )

    assert words == {"שלומ", "שלומי"}
    assert "ספר" not in words
    assert "אמא" not in words
    assert "אבא" not in words
    assert "צהל" not in words


def test_top_n_cuts_freq() -> None:
    words = load_dictionary(
        hspell_path=FIX / "hspell_tiny.txt",
        freq_path=FIX / "freq_tiny.txt",
        freq_top_n=1,
        blacklist_path=FIX / "blacklist_tiny.txt",
    )

    assert words == {"שלומ"}
    assert "שלומי" not in words


def test_blacklist_removes(tmp_path: Path) -> None:
    blacklist = tmp_path / "bl.txt"
    blacklist.write_text("שלומ\n", encoding="utf-8")

    words = load_dictionary(
        FIX / "hspell_tiny.txt",
        FIX / "freq_tiny.txt",
        40,
        blacklist,
    )

    assert "שלומ" not in words
