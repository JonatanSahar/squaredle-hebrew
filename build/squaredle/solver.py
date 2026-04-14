from .trie import Node, Trie


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


def solve(grid: list[list[str]], trie: Trie, min_len: int = 4) -> set[str]:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    found: set[str] = set()

    def dfs(
        row: int,
        col: int,
        node: Node,
        path: list[str],
        visited: set[tuple[int, int]],
    ) -> None:
        char = grid[row][col]
        next_node = node.children.get(char)
        if next_node is None:
            return

        path.append(char)
        visited.add((row, col))

        if next_node.is_word and len(path) >= min_len:
            found.add("".join(path))

        for d_row, d_col in NEIGHBORS:
            next_row, next_col = row + d_row, col + d_col
            if (
                0 <= next_row < rows
                and 0 <= next_col < cols
                and (next_row, next_col) not in visited
            ):
                dfs(next_row, next_col, next_node, path, visited)

        path.pop()
        visited.remove((row, col))

    for row in range(rows):
        for col in range(cols):
            dfs(row, col, trie.root, [], set())

    return found
