import random

from squaredle.grid import place_word


def test_place_word_returns_cell_path() -> None:
    rng = random.Random(0)

    path = place_word("שלומ", rows=5, cols=5, rng=rng)

    assert path is not None
    assert len(path) == 4
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        assert max(abs(r1 - r2), abs(c1 - c2)) == 1
    assert len(set(path)) == 4


def test_place_word_fails_if_too_long() -> None:
    rng = random.Random(0)

    path = place_word("א" * 30, rows=5, cols=5, rng=rng)

    assert path is None
