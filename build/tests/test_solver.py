from squaredle.solver import solve
from squaredle.trie import Trie


def _make_trie(words: list[str]) -> Trie:
    trie = Trie()
    for word in words:
        trie.insert(word)
    return trie


def test_solver_finds_simple_word() -> None:
    grid = [
        list("שלומ"),
        list("אבגד"),
        list("הוזח"),
        list("טיכל"),
    ]
    trie = _make_trie(["שלומ"])

    found = solve(grid, trie, min_len=4)

    assert "שלומ" in found


def test_solver_no_cell_reuse() -> None:
    grid = [
        list("אב"),
        list("גד"),
    ]
    trie = _make_trie(["אבא"])

    found = solve(grid, trie, min_len=3)

    assert "אבא" not in found


def test_solver_diagonal_ok() -> None:
    grid = [list("שא"), list("בל"), list("גו"), list("דמ")]
    trie = _make_trie(["שלומ"])

    found = solve(grid, trie, min_len=4)

    assert "שלומ" in found
