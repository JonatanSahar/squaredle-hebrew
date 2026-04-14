import random


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
