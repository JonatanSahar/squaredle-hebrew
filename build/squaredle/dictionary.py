from pathlib import Path

from .normalize import is_acceptable, normalize_word


def _read_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_dictionary(
    hspell_path: Path,
    freq_path: Path,
    freq_top_n: int,
    blacklist_path: Path,
) -> set[str]:
    freq_norm: list[str] = []
    for line in _read_lines(freq_path):
        token = line.split()[0]
        if is_acceptable(token):
            freq_norm.append(normalize_word(token))
        if len(freq_norm) >= freq_top_n:
            break

    freq_set = set(freq_norm)
    hspell_norm = {
        normalize_word(word) for word in _read_lines(hspell_path) if is_acceptable(word)
    }

    result = hspell_norm & freq_set

    for blocked in _read_lines(blacklist_path):
        result.discard(normalize_word(blocked))

    return result
