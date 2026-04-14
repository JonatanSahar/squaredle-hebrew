import random

from squaredle.grid import generate_grid, place_word


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


def test_generate_grid_returns_5x5_with_anchor() -> None:
    rng = random.Random(42)
    words = {"שלומ", "אמא", "בית", "שלוש", "ספרימ"}
    letter_weights = {c: 1.0 for c in "אבגדהוזחטיכלמנסעפצקרשת"}

    grid, anchor = generate_grid(
        answer_words=words,
        letter_weights=letter_weights,
        rng=rng,
        rows=5,
        cols=5,
        anchor_len_range=(4, 6),
    )

    assert len(grid) == 5
    assert all(len(row) == 5 for row in grid)
    assert anchor in words


def test_generate_grid_respects_letter_caps() -> None:
    rng = random.Random(1)
    words = {"שלומ", "אבגד", "בגדמ"}
    letter_weights = {c: 1.0 for c in "אבגדהוזחטיכלמנסעפצקרשת"}

    grid, _ = generate_grid(words, letter_weights, rng, 5, 5, (4, 4))
    flat = [char for row in grid for char in row]

    from collections import Counter

    assert max(Counter(flat).values()) <= 4
