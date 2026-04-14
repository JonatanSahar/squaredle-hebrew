from squaredle.acceptance import accept_puzzle


def test_accept_rejects_too_few() -> None:
    assert not accept_puzzle({"שלומ"}, anchor="שלומ")


def test_accept_rejects_too_many() -> None:
    answers = {f"אאא{i:03d}" for i in range(120)}
    assert not accept_puzzle(answers, anchor="אאא000")


def test_accept_rejects_too_many_shorts() -> None:
    longer = {f"אבגד{i:02d}" for i in range(15)}
    shorts = {
        f"אב{first}{second}"
        for first in "אבגדהוזח"
        for second in "טיכלמ"
    }
    total = longer | shorts

    assert not accept_puzzle(total, anchor=next(iter(total)))


def test_accept_passes_well_formed() -> None:
    pool = {f"אבגד{chr(0x05D0 + i)}" for i in range(10)}
    pool |= {f"אבגדה{chr(0x05D0 + i)}" for i in range(5)}
    pool |= {f"אבגדהו{chr(0x05D0 + i)}" for i in range(2)}
    pool |= {
        f"אבגד{chr(0x05D0 + i)}{chr(0x05D0 + i)}"
        for i in range(13)
    }

    assert accept_puzzle(pool, anchor=next(iter(pool)))


def test_accept_rejects_plural_domination() -> None:
    plurals = {f"אבגד{i:02d}ים" for i in range(30)}
    others = {f"אבגדה{i:02d}" for i in range(10)}

    assert not accept_puzzle(plurals | others, anchor=next(iter(plurals)))
