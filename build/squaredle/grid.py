import random
from collections import Counter


NEIGHBORS = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]
_VOWELY = set("והיא")


def place_word(
    word: str,
    rows: int,
    cols: int,
    rng: random.Random,
    tries: int = 200,
) -> list[tuple[int, int]] | None:
    if len(word) > rows * cols:
        return None

    for _ in range(tries):
        start = (rng.randrange(rows), rng.randrange(cols))
        path = [start]
        visited = {start}
        ok = True

        for _ in word[1:]:
            row, col = path[-1]
            options = [
                (row + d_row, col + d_col)
                for d_row, d_col in NEIGHBORS
                if 0 <= row + d_row < rows
                and 0 <= col + d_col < cols
                and (row + d_row, col + d_col) not in visited
            ]
            if not options:
                ok = False
                break

            next_cell = rng.choice(options)
            path.append(next_cell)
            visited.add(next_cell)

        if ok:
            return path

    return None


def _weighted_choice(rng: random.Random, weights: dict[str, float]) -> str:
    items = sorted(weights.items())
    total = sum(weight for _, weight in items)
    target = rng.random() * total
    running = 0.0

    for char, weight in items:
        running += weight
        if target <= running:
            return char

    return items[-1][0]


def _passes_guardrails(grid: list[list[str]]) -> bool:
    flat = [char for row in grid for char in row]
    counts = Counter(flat)

    if sum(counts.get(char, 0) for char in _VOWELY) > 10:
        return False
    if len(counts) < 12:
        return False
    if max(counts.values()) > 4:
        return False

    return True


def generate_grid(
    answer_words: set[str],
    letter_weights: dict[str, float],
    rng: random.Random,
    rows: int,
    cols: int,
    anchor_len_range: tuple[int, int],
    max_attempts: int = 300,
) -> tuple[list[list[str]], str]:
    eligible = [
        word
        for word in answer_words
        if anchor_len_range[0] <= len(word) <= anchor_len_range[1]
    ]
    eligible.sort()
    if not eligible:
        raise ValueError("no anchor candidates")

    for _ in range(max_attempts):
        anchor = rng.choice(eligible)
        path = place_word(anchor, rows, cols, rng)
        if path is None:
            continue

        grid = [["" for _ in range(cols)] for _ in range(rows)]
        for (row, col), char in zip(path, anchor):
            grid[row][col] = char

        for row in range(rows):
            for col in range(cols):
                if grid[row][col] == "":
                    grid[row][col] = _weighted_choice(rng, letter_weights)

        if _passes_guardrails(grid):
            return grid, anchor

    raise RuntimeError("grid generation exceeded attempts")
