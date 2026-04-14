import json
import subprocess
import sys
from pathlib import Path


def test_cli_generates_one_puzzle(tmp_path: Path) -> None:
    out = tmp_path / "puzzles"
    cmd = [
        sys.executable,
        "-m",
        "squaredle.cli",
        "--start",
        "2026-04-14",
        "--days",
        "1",
        "--seed",
        "7",
        "--hspell",
        "tests/fixtures/hspell_large.txt",
        "--freq",
        "tests/fixtures/freq_large.txt",
        "--freq-top-n",
        "500",
        "--blacklist",
        "tests/fixtures/blacklist_tiny.txt",
        "--out",
        str(out),
    ]

    result = subprocess.run(cmd, cwd=".", capture_output=True, text=True)

    assert result.returncode == 0, result.stderr

    data = json.loads((out / "2026-04-14.json").read_text(encoding="utf-8"))
    assert data["date"] == "2026-04-14"
    assert data["version"] == 1
    assert len(data["grid"]) == 5
    assert all(len(row) == 5 for row in data["grid"])
    assert 20 <= data["counts"]["total"] <= 100
    assert data["difficulty"] in ("easy", "medium", "hard")
