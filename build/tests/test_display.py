from squaredle.display import to_display


def test_final_kaf() -> None:
    assert to_display("לכ") == "לך"


def test_no_change_midword() -> None:
    assert to_display("שלומ") == "שלום"


def test_each_sofit() -> None:
    assert to_display("אצ") == "אץ"
    assert to_display("אנ") == "אן"
    assert to_display("אפ") == "אף"
