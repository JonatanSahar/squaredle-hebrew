import argparse
import json
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from .acceptance import accept_puzzle
from .dictionary import load_dictionary
from .difficulty import classify
from .grid import generate_grid
from .solver import solve
from .trie import Trie


def _letter_weights(words: set[str]) -> dict[str, float]:
    counts = Counter(char for word in words for char in word)
    total = sum(counts.values()) or 1
    return {char: count / total for char, count in counts.items()}


def _try_generate(
    words: set[str],
    weights: dict[str, float],
    trie: Trie,
    rng: random.Random,
    max_outer: int = 500,
) -> tuple[list[list[str]], set[str]]:
    for _ in range(max_outer):
        grid, anchor = generate_grid(words, weights, rng, 5, 5, (4, 7))
        answers = solve(grid, trie, min_len=4)
        if accept_puzzle(answers, anchor):
            return grid, answers
    raise RuntimeError("no acceptable puzzle after outer attempts")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--days", type=int, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--hspell", required=True, type=Path)
    parser.add_argument("--freq", required=True, type=Path)
    parser.add_argument("--freq-top-n", type=int, default=40000)
    parser.add_argument("--blacklist", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    words = load_dictionary(args.hspell, args.freq, args.freq_top_n, args.blacklist)
    if len(words) < 200:
        raise SystemExit(f"dictionary too small: {len(words)}")

    trie = Trie()
    for word in words:
        trie.insert(word)

    weights = _letter_weights(words)
    args.out.mkdir(parents=True, exist_ok=True)
    start = date.fromisoformat(args.start)

    for offset in range(args.days):
        current = start + timedelta(days=offset)
        rng = random.Random(f"{args.seed}:{current.toordinal()}")
        grid, answers = _try_generate(words, weights, trie, rng)

        by_length: dict[str, int] = {}
        for word in answers:
            length = str(len(word))
            by_length[length] = by_length.get(length, 0) + 1

        payload = {
            "date": current.isoformat(),
            "version": 1,
            "grid": ["".join(row) for row in grid],
            "answers": sorted(answers),
            "difficulty": classify(answers),
            "counts": {"total": len(answers), "by_length": by_length},
        }
        (args.out / f"{current.isoformat()}.json").write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
