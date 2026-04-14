# Squaredle Hebrew Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Hebrew Squaredle clone as a static GitHub Pages site with 730 days of precomputed puzzles, backed by a Python build pipeline.

**Architecture:** Python build (`build/`) loads Hspell ∩ OpenSubtitles-he, generates 5x5 puzzles via anchor-planted + conditional-sampling grids, solves with a trie-pruned DFS, applies acceptance rules, and writes JSON per date. Frontend (`site/`) is vanilla JS ES modules, CSS RTL grid, Pointer Events + tap fallback, localStorage per-date.

**Tech Stack:** Python 3.12, pytest, uv for deps. Vanilla ES-module JS, CSS Grid, no bundler. GitHub Pages + `workflow_dispatch`-only Actions workflow. AGPL-compliant Hspell distribution.

**Spec:** `docs/superpowers/specs/2026-04-14-squaredle-hebrew-design.md`.

---

## File structure

```
build/
  pyproject.toml
  squaredle/
    __init__.py
    normalize.py      # strip niqqud, sofit-fold, filter, reject acronyms
    dictionary.py     # load Hspell, OpenSubtitles freq, intersect
    trie.py           # compact trie for DFS pruning
    grid.py           # anchor planting + conditional-freq fill + guardrails
    solver.py         # DFS 8-neighbor, no reuse, trie pruned
    acceptance.py     # puzzle acceptance rules (§5 of spec)
    difficulty.py     # Easy/Medium/Hard classifier
    display.py        # re-apply sofit at word end (for tests only; JS mirrors)
    cli.py            # `squaredle-gen --start YYYY-MM-DD --days N --seed S`
  data/
    hspell/           # AGPL, committed
    opensubtitles-he-freq.txt
    blacklist.txt
  tests/
    test_normalize.py
    test_dictionary.py
    test_trie.py
    test_grid.py
    test_solver.py
    test_acceptance.py
    test_difficulty.py
    test_display.py
    test_e2e.py
site/
  index.html
  styles.css
  js/
    main.js
    board.js
    input.js
    state.js
    display.js
    adjacency.js
  puzzles/YYYY-MM-DD.json
.github/workflows/generate.yml
LICENSES/HSPELL.txt
NOTICE
README.md
.gitignore
```

---

## Phase 0 — Project skeleton

### Task 0.1: Git init + baseline

**Files:**
- Create: `.gitignore`, `README.md`, `NOTICE`, `LICENSES/HSPELL.txt`

- [ ] **Step 1:** `cd /home/yonatan/Projects/personal/squaredle && git init -b main`
- [ ] **Step 2:** Write `.gitignore`:

```
__pycache__/
*.pyc
.venv/
.pytest_cache/
build/dist/
build/data/hspell/*.tmp
.DS_Store
```

- [ ] **Step 3:** Write `README.md` (one paragraph + how to run: `uv run squaredle-gen`, how to serve site: `python -m http.server -d site`).
- [ ] **Step 4:** Write `NOTICE`:

```
Squaredle Hebrew
This project includes:
- Hspell (AGPL-3.0). See LICENSES/HSPELL.txt. https://hspell.sourceforge.net/
- OpenSubtitles-he frequency list (CC BY-SA 4.0) via hermitdave/FrequencyWords.
```

- [ ] **Step 5:** Fetch Hspell license text (short; paste from the Hspell source into `LICENSES/HSPELL.txt`).
- [ ] **Step 6:** Commit: `git add -A && git commit -m "chore: project skeleton"`.

### Task 0.2: Python project

**Files:** Create `build/pyproject.toml`, `build/squaredle/__init__.py`, `build/tests/__init__.py`.

- [ ] **Step 1:** Write `build/pyproject.toml`:

```toml
[project]
name = "squaredle"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[project.scripts]
squaredle-gen = "squaredle.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["squaredle"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2:** Create empty `build/squaredle/__init__.py` and `build/tests/__init__.py`.
- [ ] **Step 3:** From `build/`, run `uv sync` and confirm no errors.
- [ ] **Step 4:** Commit: `git add build && git commit -m "chore: python project scaffold"`.

---

## Phase 1 — Normalization

### Task 1.1: strip_niqqud + fold_sofit

**Files:** Create `build/squaredle/normalize.py`, `build/tests/test_normalize.py`.

- [ ] **Step 1:** Write failing tests `test_normalize.py`:

```python
from squaredle.normalize import strip_niqqud, fold_sofit, normalize_word, is_acceptable

def test_strip_niqqud_removes_points():
    assert strip_niqqud("שָׁלוֹם") == "שלום"

def test_strip_niqqud_keeps_base():
    assert strip_niqqud("שלום") == "שלום"

def test_fold_sofit_maps_all_five():
    assert fold_sofit("ךםןףץ") == "כמנפצ"

def test_fold_sofit_midword():
    assert fold_sofit("שלום") == "שלומ"

def test_normalize_word_composes():
    assert normalize_word("שָׁלוֹם") == "שלומ"

def test_is_acceptable_rejects_gershayim():
    assert not is_acceptable('צה"ל')

def test_is_acceptable_rejects_geresh():
    assert not is_acceptable("ג'ינס")

def test_is_acceptable_rejects_hyphen():
    assert not is_acceptable("אי-שם")

def test_is_acceptable_rejects_short():
    assert not is_acceptable("שלו")  # len 3 after normalize

def test_is_acceptable_accepts_four():
    assert is_acceptable("שלומ")

def test_is_acceptable_rejects_non_hebrew():
    assert not is_acceptable("hello")
```

- [ ] **Step 2:** Run `uv run pytest build/tests/test_normalize.py -v`. Expect ImportError.
- [ ] **Step 3:** Implement `build/squaredle/normalize.py`:

```python
import unicodedata

NIQQUD_RANGE = (0x0591, 0x05C7)
SOFIT_MAP = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}
HEBREW_BASE = set("אבגדהוזחטיכלמנסעפצקרשת")
REJECT_CHARS = set('"\'־-\u05BE\u05F3\u05F4')

def strip_niqqud(s: str) -> str:
    return "".join(c for c in s if not (NIQQUD_RANGE[0] <= ord(c) <= NIQQUD_RANGE[1]))

def fold_sofit(s: str) -> str:
    return "".join(SOFIT_MAP.get(c, c) for c in s)

def normalize_word(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = strip_niqqud(s)
    s = fold_sofit(s)
    return s

def is_acceptable(raw: str) -> bool:
    if any(c in REJECT_CHARS for c in raw):
        return False
    norm = normalize_word(raw)
    if len(norm) < 4:
        return False
    return all(c in HEBREW_BASE for c in norm)
```

- [ ] **Step 4:** Run tests. All pass.
- [ ] **Step 5:** Commit: `git add build && git commit -m "feat(build): Hebrew normalization"`.

---

## Phase 2 — Dictionary loading

### Task 2.1: Stub loaders with fixtures

**Files:** Create `build/squaredle/dictionary.py`, `build/tests/test_dictionary.py`, `build/tests/fixtures/hspell_tiny.txt`, `build/tests/fixtures/freq_tiny.txt`, `build/tests/fixtures/blacklist_tiny.txt`.

- [ ] **Step 1:** Create fixtures.

`hspell_tiny.txt` (one word per line):
```
שלום
אמא
אבא
צהל
"צה"ל"
שלומי
אי-שם
ספר
מהר
```

`freq_tiny.txt` (word<space>count, high → low):
```
שלום 100
אמא 80
אבא 60
ספר 50
מהר 40
שלומי 20
```

`blacklist_tiny.txt`: empty.

- [ ] **Step 2:** Write failing tests:

```python
from pathlib import Path
from squaredle.dictionary import load_dictionary

FIX = Path(__file__).parent / "fixtures"

def test_load_dictionary_intersects_and_normalizes():
    words = load_dictionary(
        hspell_path=FIX / "hspell_tiny.txt",
        freq_path=FIX / "freq_tiny.txt",
        freq_top_n=40,
        blacklist_path=FIX / "blacklist_tiny.txt",
    )
    # "שלום" → "שלומ"; must be in Hspell AND in top-40 freq.
    assert "שלומ" in words
    assert "ספר" not in words  # len 3 after normalize
    assert 'צהל' not in words  # rejected by is_acceptable (quotes in raw)? Not in freq either.
    assert "שלומי" not in words  # freq rank 6 > 40? rank is rank; top_n is a count.

def test_top_n_cuts_freq():
    words = load_dictionary(
        hspell_path=FIX / "hspell_tiny.txt",
        freq_path=FIX / "freq_tiny.txt",
        freq_top_n=3,
        blacklist_path=FIX / "blacklist_tiny.txt",
    )
    assert "שלומ" in words
    assert "מהר" not in words  # normalized len 3, also outside top-3

def test_blacklist_removes(tmp_path):
    bl = tmp_path / "bl.txt"
    bl.write_text("שלומ\n", encoding="utf-8")
    words = load_dictionary(FIX / "hspell_tiny.txt", FIX / "freq_tiny.txt", 40, bl)
    assert "שלומ" not in words
```

- [ ] **Step 3:** Implement `dictionary.py`:

```python
from pathlib import Path
from .normalize import is_acceptable, normalize_word

def _read_lines(path: Path) -> list[str]:
    return [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

def load_dictionary(
    hspell_path: Path,
    freq_path: Path,
    freq_top_n: int,
    blacklist_path: Path,
) -> set[str]:
    # Top-N normalized freq words (preserve rank order).
    freq_norm: list[str] = []
    for line in _read_lines(freq_path):
        token = line.split()[0]
        if is_acceptable(token):
            freq_norm.append(normalize_word(token))
        if len(freq_norm) >= freq_top_n:
            break
    freq_set = set(freq_norm)
    # Hspell acceptable normalized forms.
    hspell_norm = {normalize_word(w) for w in _read_lines(hspell_path) if is_acceptable(w)}
    # Intersect.
    result = hspell_norm & freq_set
    # Blacklist.
    for bl in _read_lines(blacklist_path):
        result.discard(normalize_word(bl))
    return result
```

- [ ] **Step 4:** Run tests. Iterate until green. Commit: `feat(build): dictionary loader`.

### Task 2.2: Download real data

Not a code task — a data-provisioning step. Document in `build/data/README.md`:

```
Hspell: download `hebrew.wgz` from https://hspell.sourceforge.net/, extract to
  `build/data/hspell/words.txt`. Committed (AGPL; see NOTICE).
OpenSubtitles-he: https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/he/he_full.txt → save as `build/data/opensubtitles-he-freq.txt`.
```

- [ ] Place real files. Commit: `chore(data): hspell + opensubtitles-he frequency`.

---

## Phase 3 — Trie

### Task 3.1: Trie

**Files:** Create `build/squaredle/trie.py`, `build/tests/test_trie.py`.

- [ ] **Step 1:** Failing tests:

```python
from squaredle.trie import Trie

def test_insert_and_contains():
    t = Trie()
    t.insert("שלומ")
    assert t.contains("שלומ")
    assert not t.contains("שלו")

def test_has_prefix():
    t = Trie()
    t.insert("שלומ")
    assert t.has_prefix("של")
    assert t.has_prefix("שלומ")
    assert not t.has_prefix("מה")

def test_child_navigation():
    t = Trie()
    t.insert("שלומ")
    node = t.root.children["ש"].children["ל"]
    assert not node.is_word
    end = node.children["ו"].children["מ"]
    assert end.is_word
```

- [ ] **Step 2:** Implement:

```python
from dataclasses import dataclass, field

@dataclass
class Node:
    children: dict[str, "Node"] = field(default_factory=dict)
    is_word: bool = False

class Trie:
    def __init__(self) -> None:
        self.root = Node()

    def insert(self, word: str) -> None:
        n = self.root
        for ch in word:
            n = n.children.setdefault(ch, Node())
        n.is_word = True

    def contains(self, word: str) -> bool:
        n = self._walk(word)
        return bool(n and n.is_word)

    def has_prefix(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def _walk(self, s: str) -> Node | None:
        n = self.root
        for ch in s:
            nxt = n.children.get(ch)
            if nxt is None:
                return None
            n = nxt
        return n
```

- [ ] **Step 3:** Tests green. Commit: `feat(build): trie`.

---

## Phase 4 — Solver

### Task 4.1: DFS solver

**Files:** Create `build/squaredle/solver.py`, `build/tests/test_solver.py`.

- [ ] **Step 1:** Failing tests with a tiny 3x3 hand-crafted grid:

```python
from squaredle.trie import Trie
from squaredle.solver import solve

def _make_trie(words):
    t = Trie()
    for w in words:
        t.insert(w)
    return t

def test_solver_finds_simple_word():
    grid = [
        list("שלומ"),
        list("אבגד"),
        list("הוזח"),
        list("טיכל"),
    ]  # 4x4
    t = _make_trie(["שלומ"])
    found = solve(grid, t, min_len=4)
    assert "שלומ" in found

def test_solver_no_cell_reuse():
    grid = [
        list("שלש"),
        list("לומ"),
        list("אבג"),
    ]
    t = _make_trie(["שלושה"])  # path would require reusing cells
    found = solve(grid, t, min_len=4)
    assert "שלושה" not in found

def test_solver_diagonal_ok():
    grid = [list("שא"), list("בל"), list("גו"), list("דמ")]  # 4x2, diagonals link
    t = _make_trie(["שלומ"])
    found = solve(grid, t, min_len=4)
    # Verify diagonals are explored; at minimum the solver does not crash.
    assert isinstance(found, set)
```

- [ ] **Step 2:** Implement:

```python
from .trie import Trie, Node

NEIGHBORS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def solve(grid: list[list[str]], trie: Trie, min_len: int = 4) -> set[str]:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    found: set[str] = set()

    def dfs(r: int, c: int, node: Node, path: list[str], visited: set[tuple[int,int]]):
        ch = grid[r][c]
        nxt = node.children.get(ch)
        if nxt is None:
            return
        path.append(ch)
        visited.add((r, c))
        if nxt.is_word and len(path) >= min_len:
            found.add("".join(path))
        for dr, dc in NEIGHBORS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                dfs(nr, nc, nxt, path, visited)
        path.pop()
        visited.remove((r, c))

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie.root, [], set())
    return found
```

- [ ] **Step 3:** Tests green. Commit: `feat(build): DFS solver`.

---

## Phase 5 — Grid generation

### Task 5.1: Adjacency walk for anchor placement

**Files:** Create `build/squaredle/grid.py`, `build/tests/test_grid.py`.

- [ ] **Step 1:** Failing test:

```python
import random
from squaredle.grid import place_word

def test_place_word_returns_cell_path():
    rng = random.Random(0)
    path = place_word("שלומ", rows=5, cols=5, rng=rng)
    assert path is not None
    assert len(path) == 4
    # 8-adjacent and unique cells
    for (r1,c1),(r2,c2) in zip(path, path[1:]):
        assert max(abs(r1-r2), abs(c1-c2)) == 1
    assert len(set(path)) == 4

def test_place_word_fails_if_too_long():
    rng = random.Random(0)
    path = place_word("א"*30, rows=5, cols=5, rng=rng)
    assert path is None
```

- [ ] **Step 2:** Implement `place_word`:

```python
import random

NEIGHBORS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

def place_word(word: str, rows: int, cols: int, rng: random.Random, tries: int = 200):
    for _ in range(tries):
        start = (rng.randrange(rows), rng.randrange(cols))
        path = [start]
        visited = {start}
        ok = True
        for _ in word[1:]:
            r, c = path[-1]
            opts = [(r+dr, c+dc) for dr, dc in NEIGHBORS
                    if 0 <= r+dr < rows and 0 <= c+dc < cols and (r+dr, c+dc) not in visited]
            if not opts:
                ok = False
                break
            nxt = rng.choice(opts)
            path.append(nxt)
            visited.add(nxt)
        if ok:
            return path
    return None
```

- [ ] **Step 3:** Tests green. Commit: `feat(build): anchor placement walk`.

### Task 5.2: Conditional fill + guardrails

**Files:** Extend `grid.py`, `test_grid.py`.

- [ ] **Step 1:** Failing test for a full-grid generator:

```python
from squaredle.grid import generate_grid

def test_generate_grid_returns_5x5_with_anchor():
    import random
    rng = random.Random(42)
    words = {"שלומ", "אמא", "בית", "שלוש", "ספרים"}
    letter_weights = {c: 1.0 for c in "אבגדהוזחטיכלמנסעפצקרשת"}
    grid, anchor = generate_grid(
        answer_words=words,
        letter_weights=letter_weights,
        rng=rng,
        rows=5, cols=5,
        anchor_len_range=(4, 6),
    )
    assert len(grid) == 5 and all(len(r) == 5 for r in grid)
    # Anchor is placeable and chosen from the set.
    assert anchor in words

def test_generate_grid_respects_letter_caps():
    import random
    rng = random.Random(1)
    words = {"שלומ", "אבגד", "בגדמ"}
    letter_weights = {c: 1.0 for c in "אבגדהוזחטיכלמנסעפצקרשת"}
    grid, _ = generate_grid(words, letter_weights, rng, 5, 5, (4, 4))
    flat = [c for row in grid for c in row]
    # No single letter > 4 occurrences.
    from collections import Counter
    assert max(Counter(flat).values()) <= 4
```

- [ ] **Step 2:** Implement:

```python
import random
from collections import Counter

_VOWELY = set("והיא")

def _weighted_choice(rng: random.Random, weights: dict[str, float]) -> str:
    items = list(weights.items())
    total = sum(w for _, w in items)
    x = rng.random() * total
    acc = 0.0
    for k, w in items:
        acc += w
        if x <= acc:
            return k
    return items[-1][0]

def _passes_guardrails(grid: list[list[str]]) -> bool:
    flat = [c for row in grid for c in row]
    counts = Counter(flat)
    if sum(counts.get(c, 0) for c in _VOWELY) > 10:
        return False
    if len(counts) < 12:
        return False
    if max(counts.values()) > 4:
        return False
    return True

def generate_grid(
    answer_words,
    letter_weights,
    rng,
    rows: int,
    cols: int,
    anchor_len_range: tuple[int, int],
    max_attempts: int = 300,
):
    eligible = [w for w in answer_words if anchor_len_range[0] <= len(w) <= anchor_len_range[1]]
    if not eligible:
        raise ValueError("no anchor candidates")
    for _ in range(max_attempts):
        anchor = rng.choice(eligible)
        path = place_word(anchor, rows, cols, rng)
        if path is None:
            continue
        grid = [["" for _ in range(cols)] for _ in range(rows)]
        for (r, c), ch in zip(path, anchor):
            grid[r][c] = ch
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == "":
                    grid[r][c] = _weighted_choice(rng, letter_weights)
        if _passes_guardrails(grid):
            return grid, anchor
    raise RuntimeError("grid generation exceeded attempts")
```

- [ ] **Step 3:** Tests green. Commit: `feat(build): grid fill with guardrails`.

---

## Phase 6 — Acceptance + difficulty

### Task 6.1: Acceptance rules

**Files:** Create `build/squaredle/acceptance.py`, `build/tests/test_acceptance.py`.

- [ ] **Step 1:** Failing tests:

```python
from squaredle.acceptance import accept_puzzle

def _mk(words):
    return {"answers": set(words), "anchor": next(iter(words))}

def test_accept_rejects_too_few():
    assert not accept_puzzle(set(["שלומ"]*5), anchor="שלומ")

def test_accept_rejects_too_many():
    assert not accept_puzzle(set(f"אאא{i:03d}" for i in range(120)), anchor="אאא000")

def test_accept_rejects_too_many_shorts():
    words = {f"אבגד{i}" for i in range(25)}  # all len 5
    # dummy shorts to exceed 70%
    shorts = {f"אב{chr(0x05D0+i)}ד" for i in range(40)}  # len 4
    total = words | shorts
    assert not accept_puzzle(total, anchor=next(iter(total)))

def test_accept_passes_well_formed():
    # 30 words, mix of lengths, no plural dominance
    pool = {f"אבגד{chr(0x05D0+i)}" for i in range(10)}           # len 5 x 10
    pool |= {f"אבגדה{chr(0x05D0+i)}" for i in range(5)}          # len 6 x 5
    pool |= {f"אבגדהו{chr(0x05D0+i)}" for i in range(2)}         # len 7 x 2
    pool |= {f"אבגד{chr(0x05D0+i)}{chr(0x05D0+i)}" for i in range(13)}  # len 6 x 13
    assert accept_puzzle(pool, anchor=next(iter(pool)))

def test_accept_rejects_plural_domination():
    plurals = {f"אבגד{i}ים" for i in range(30)}
    others = {f"אבגדה{i}" for i in range(10)}
    assert not accept_puzzle(plurals | others, anchor=next(iter(plurals)))
```

- [ ] **Step 2:** Implement:

```python
def accept_puzzle(answers: set[str], anchor: str) -> bool:
    n = len(answers)
    if not (20 <= n <= 100):
        return False
    if anchor not in answers:
        return False
    four = sum(1 for w in answers if len(w) == 4)
    if four / n > 0.70:
        return False
    if sum(1 for w in answers if len(w) >= 5) < 6:
        return False
    if sum(1 for w in answers if len(w) >= 6) < 2:
        return False
    if max(len(w) for w in answers) < 6:
        return False
    plurals = sum(1 for w in answers if w.endswith("ים") or w.endswith("ות"))
    if plurals / n > 0.35:
        return False
    return True
```

- [ ] **Step 3:** Tests green. Commit: `feat(build): puzzle acceptance rules`.

### Task 6.2: Difficulty

**Files:** Create `build/squaredle/difficulty.py`, `build/tests/test_difficulty.py`.

- [ ] **Step 1:** Failing tests:

```python
from squaredle.difficulty import classify

def test_easy():
    answers = {f"אבגד{i}" for i in range(70)}
    assert classify(answers) in ("easy", "medium")  # count-driven

def test_hard():
    answers = {f"אבגד{i}" for i in range(22)}
    assert classify(answers) == "hard"

def test_medium():
    answers = {f"אבגד{i}" for i in range(40)}
    assert classify(answers) == "medium"
```

- [ ] **Step 2:** Implement:

```python
def classify(answers: set[str]) -> str:
    n = len(answers)
    if n >= 60:
        return "easy"
    if n >= 35:
        return "medium"
    return "hard"
```

- [ ] **Step 3:** Tests green. Commit: `feat(build): difficulty classification`.

---

## Phase 7 — Display helper

### Task 7.1: Python sofit re-application (for e2e tests & parity check)

**Files:** Create `build/squaredle/display.py`, `build/tests/test_display.py`.

- [ ] **Step 1:** Failing tests:

```python
from squaredle.display import to_display

def test_final_kaf():
    assert to_display("לכ") == "לך"

def test_no_change_midword():
    assert to_display("שלומ") == "שלום"  # final mem

def test_each_sofit():
    assert to_display("אצ") == "אץ"
    assert to_display("אן") == "אן"  # nun is already n→ן? input normalized has נ
    assert to_display("אנ") == "אן"
    assert to_display("אפ") == "אף"
```

- [ ] **Step 2:** Implement:

```python
FINAL_MAP = {"כ": "ך", "מ": "ם", "נ": "ן", "פ": "ף", "צ": "ץ"}

def to_display(word: str) -> str:
    if not word:
        return word
    last = word[-1]
    return word[:-1] + FINAL_MAP.get(last, last)
```

- [ ] **Step 3:** Tests green. Commit: `feat(build): sofit display`.

---

## Phase 8 — CLI + end-to-end

### Task 8.1: Orchestrator + CLI

**Files:** Create `build/squaredle/cli.py`, `build/tests/test_e2e.py`.

- [ ] **Step 1:** Failing e2e test (uses tiny fixtures, fixed seed, one day):

```python
from pathlib import Path
import json, subprocess, sys

def test_cli_generates_one_puzzle(tmp_path):
    out = tmp_path / "puzzles"
    cmd = [
        sys.executable, "-m", "squaredle.cli",
        "--start", "2026-04-14",
        "--days", "1",
        "--seed", "7",
        "--hspell", "tests/fixtures/hspell_large.txt",
        "--freq", "tests/fixtures/freq_large.txt",
        "--freq-top-n", "500",
        "--blacklist", "tests/fixtures/blacklist_tiny.txt",
        "--out", str(out),
    ]
    result = subprocess.run(cmd, cwd="build", capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    data = json.loads((out / "2026-04-14.json").read_text(encoding="utf-8"))
    assert data["date"] == "2026-04-14"
    assert data["version"] == 1
    assert len(data["grid"]) == 5
    assert all(len(row) == 5 for row in data["grid"])
    assert 20 <= data["counts"]["total"] <= 100
    assert data["difficulty"] in ("easy", "medium", "hard")
```

The `hspell_large.txt` / `freq_large.txt` fixtures need to be real-enough to produce an accepted puzzle; build them by sampling 500 frequent real Hebrew words as a one-time fixture. Commit the fixtures.

- [ ] **Step 2:** Implement `cli.py`:

```python
import argparse, json, random
from datetime import date, timedelta
from pathlib import Path
from collections import Counter

from .dictionary import load_dictionary
from .trie import Trie
from .grid import generate_grid
from .solver import solve
from .acceptance import accept_puzzle
from .difficulty import classify

def _letter_weights(words: set[str]) -> dict[str, float]:
    c = Counter(ch for w in words for ch in w)
    total = sum(c.values()) or 1
    return {ch: cnt / total for ch, cnt in c.items()}

def _try_generate(words, weights, trie, rng, max_outer=50):
    for _ in range(max_outer):
        grid, anchor = generate_grid(words, weights, rng, 5, 5, (5, 7))
        answers = solve(grid, trie, min_len=4)
        if accept_puzzle(answers, anchor):
            return grid, answers
    raise RuntimeError("no acceptable puzzle after outer attempts")

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--days", type=int, required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--hspell", required=True, type=Path)
    ap.add_argument("--freq", required=True, type=Path)
    ap.add_argument("--freq-top-n", type=int, default=40000)
    ap.add_argument("--blacklist", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)

    words = load_dictionary(args.hspell, args.freq, args.freq_top_n, args.blacklist)
    if len(words) < 1000:
        raise SystemExit(f"dictionary too small: {len(words)}")
    trie = Trie()
    for w in words:
        trie.insert(w)
    weights = _letter_weights(words)
    args.out.mkdir(parents=True, exist_ok=True)
    start = date.fromisoformat(args.start)
    for i in range(args.days):
        d = start + timedelta(days=i)
        rng = random.Random((args.seed, d.toordinal()))
        grid, answers = _try_generate(words, weights, trie, rng)
        by_len: dict[str, int] = {}
        for w in answers:
            by_len[str(len(w))] = by_len.get(str(len(w)), 0) + 1
        payload = {
            "date": d.isoformat(),
            "version": 1,
            "grid": ["".join(row) for row in grid],
            "answers": sorted(answers),
            "difficulty": classify(answers),
            "counts": {"total": len(answers), "by_length": by_len},
        }
        (args.out / f"{d.isoformat()}.json").write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )

if __name__ == "__main__":
    main()
```

- [ ] **Step 3:** Run e2e test. Iterate on fixture sizes / thresholds until accepted.
- [ ] **Step 4:** Commit: `feat(build): CLI orchestrator + e2e test`.

---

## Phase 9 — Frontend

### Task 9.1: Static HTML shell

**Files:** Create `site/index.html`, `site/styles.css`.

- [ ] **Step 1:** Write `site/index.html`:

```html
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <title>Squaredle עברי</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header>
    <h1>Squaredle</h1>
    <div id="meta"><span id="difficulty"></span> · <span id="progress">0 / 0</span></div>
  </header>
  <main>
    <div id="board" touch-action="none"></div>
    <div id="current"></div>
    <button id="reveal">גילוי תשובות</button>
    <section id="answers" hidden></section>
  </main>
  <script type="module" src="js/main.js"></script>
</body>
</html>
```

- [ ] **Step 2:** Write `site/styles.css`:

```css
:root { font-family: system-ui, sans-serif; }
body { margin: 0; background: #f7f7f7; color: #222; }
header { padding: 1rem; text-align: center; }
#board {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0;
  max-width: min(90vw, 420px);
  margin: 0 auto;
  aspect-ratio: 1 / 1;
  touch-action: none;
  user-select: none;
  direction: rtl;
}
.cell {
  display: flex; align-items: center; justify-content: center;
  font-size: 8vw; max-font-size: 2rem;
  background: white;
  border: 1px solid #ccc;
  box-shadow: inset 0 0 0 1px #ddd;
  aspect-ratio: 1 / 1;
  touch-action: none;
}
.cell.selected { background: #cde8ff; }
.cell.found-flash { background: #c8f2c8; }
#current { text-align: center; font-size: 1.5rem; min-height: 2rem; margin: 1rem; }
#answers { padding: 1rem; }
#answers .word { display: inline-block; margin: .2rem .4rem; }
button { display: block; margin: 1rem auto; padding: .6rem 1rem; }
```

- [ ] **Step 3:** Commit: `feat(site): html shell + styles`.

### Task 9.2: display.js (sofit re-application)

**Files:** Create `site/js/display.js`, `build/tests/test_display_js.py` (optional smoke).

- [ ] **Step 1:** Write:

```js
const FINAL = { "כ": "ך", "מ": "ם", "נ": "ן", "פ": "ף", "צ": "ץ" };
export function toDisplay(word) {
  if (!word) return word;
  const last = word[word.length - 1];
  return word.slice(0, -1) + (FINAL[last] ?? last);
}
```

- [ ] **Step 2:** Commit: `feat(site): sofit display helper`.

### Task 9.3: adjacency.js

**Files:** Create `site/js/adjacency.js`.

- [ ] **Step 1:** Write:

```js
export function isAdjacent(a, b) {
  if (!a || !b) return false;
  const dr = Math.abs(a.row - b.row);
  const dc = Math.abs(a.col - b.col);
  if (dr === 0 && dc === 0) return false;
  return dr <= 1 && dc <= 1;
}
```

- [ ] **Step 2:** Commit.

### Task 9.4: state.js (localStorage)

**Files:** Create `site/js/state.js`.

- [ ] **Step 1:** Write:

```js
const ns = "squaredle-he:v1";

export function load(dateKey) {
  try {
    const raw = localStorage.getItem(`${ns}:${dateKey}`);
    if (!raw) return { found: [], revealed: false, firstPlayedAt: null };
    return JSON.parse(raw);
  } catch {
    return { found: [], revealed: false, firstPlayedAt: null };
  }
}

export function save(dateKey, state) {
  try { localStorage.setItem(`${ns}:${dateKey}`, JSON.stringify(state)); }
  catch {}
}

export function todayKeyJerusalem() {
  const fmt = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jerusalem" });
  return fmt.format(new Date()); // YYYY-MM-DD
}
```

- [ ] **Step 2:** Commit.

### Task 9.5: board.js (render)

**Files:** Create `site/js/board.js`.

- [ ] **Step 1:** Write:

```js
export function renderBoard(boardEl, grid) {
  boardEl.innerHTML = "";
  for (let r = 0; r < grid.length; r++) {
    for (let c = 0; c < grid[r].length; c++) {
      const el = document.createElement("div");
      el.className = "cell";
      el.textContent = grid[r][c];
      el.dataset.row = String(r);
      el.dataset.col = String(c);
      boardEl.appendChild(el);
    }
  }
}

export function cellFromPoint(x, y) {
  const el = document.elementFromPoint(x, y);
  if (!el || !el.classList.contains("cell")) return null;
  return { row: +el.dataset.row, col: +el.dataset.col, el };
}
```

- [ ] **Step 2:** Commit.

### Task 9.6: input.js (pointer + tap)

**Files:** Create `site/js/input.js`.

- [ ] **Step 1:** Write:

```js
import { isAdjacent } from "./adjacency.js";
import { cellFromPoint } from "./board.js";

export function attachInput(boardEl, { onCommit, onSelectionChange }) {
  let path = [];
  let dragging = false;

  function reset() {
    for (const { el } of path) el.classList.remove("selected");
    path = [];
    onSelectionChange("");
  }

  function addCell(cell) {
    if (!cell) return;
    const last = path[path.length - 1];
    if (last && last.row === cell.row && last.col === cell.col) return;
    if (path.some(p => p.row === cell.row && p.col === cell.col)) return;
    if (last && !isAdjacent(last, cell)) return;
    path.push(cell);
    cell.el.classList.add("selected");
    onSelectionChange(path.map(p => p.el.textContent).join(""));
  }

  boardEl.addEventListener("pointerdown", (e) => {
    e.preventDefault();
    boardEl.setPointerCapture?.(e.pointerId);
    dragging = true;
    reset();
    const cell = cellFromPoint(e.clientX, e.clientY);
    addCell(cell);
  });

  boardEl.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const cell = cellFromPoint(e.clientX, e.clientY);
    addCell(cell);
  });

  function commit() {
    dragging = false;
    if (path.length >= 4) onCommit(path.map(p => p.el.textContent).join(""));
    reset();
  }

  boardEl.addEventListener("pointerup", commit);
  boardEl.addEventListener("pointercancel", () => { dragging = false; reset(); });
}
```

- [ ] **Step 2:** Commit.

### Task 9.7: main.js (wire up)

**Files:** Create `site/js/main.js`.

- [ ] **Step 1:** Write:

```js
import { renderBoard } from "./board.js";
import { attachInput } from "./input.js";
import { load, save, todayKeyJerusalem } from "./state.js";
import { toDisplay } from "./display.js";

const boardEl = document.getElementById("board");
const currentEl = document.getElementById("current");
const progressEl = document.getElementById("progress");
const difficultyEl = document.getElementById("difficulty");
const revealBtn = document.getElementById("reveal");
const answersEl = document.getElementById("answers");

const dateKey = todayKeyJerusalem();
let state = load(dateKey);
let puzzle = null;
let answerSet = new Set();

async function init() {
  const resp = await fetch(`puzzles/${dateKey}.json`);
  if (!resp.ok) { currentEl.textContent = "אין חידה להיום"; return; }
  puzzle = await resp.json();
  answerSet = new Set(puzzle.answers);
  const grid = puzzle.grid.map(row => [...row]);
  renderBoard(boardEl, grid);
  difficultyEl.textContent = { easy: "קל", medium: "בינוני", hard: "קשה" }[puzzle.difficulty];
  updateProgress();
  if (state.revealed) renderAnswers();

  attachInput(boardEl, {
    onSelectionChange: (s) => { currentEl.textContent = s; },  // normalized, matches grid
    onCommit: (word) => {
      if (answerSet.has(word) && !state.found.includes(word)) {
        state.found.push(word);
        state.firstPlayedAt ||= new Date().toISOString();
        save(dateKey, state);
        updateProgress();
        flashFound();
      }
    },
  });
  revealBtn.addEventListener("click", () => {
    if (!confirm("להיכנע ולראות תשובות?")) return;
    state.revealed = true;
    save(dateKey, state);
    renderAnswers();
  });
}

function updateProgress() {
  progressEl.textContent = `${state.found.length} / ${puzzle.counts.total}`;
}

function flashFound() {
  boardEl.querySelectorAll(".cell.selected").forEach(el => el.classList.add("found-flash"));
  setTimeout(() => boardEl.querySelectorAll(".found-flash").forEach(el => el.classList.remove("found-flash")), 300);
}

function renderAnswers() {
  answersEl.hidden = false;
  const byLen = {};
  for (const w of puzzle.answers) (byLen[w.length] ||= []).push(w);
  answersEl.innerHTML = Object.keys(byLen).sort((a,b)=>+a-+b).map(len =>
    `<div><h3>${len} אותיות</h3>${byLen[len].map(w => `<span class="word">${toDisplay(w)}</span>`).join("")}</div>`
  ).join("");
}

init();
```

- [ ] **Step 2:** Commit: `feat(site): gameplay wiring`.

### Task 9.8: Manual mobile test

- [ ] **Step 1:** `python -m http.server -d site 8000` and open on an iPhone (real device or BrowserStack / local Safari). Generate a test puzzle for today first via CLI.
- [ ] **Step 2:** Confirm: grid renders RTL, swipe selects cells, diagonal works, valid word commits and persists after reload, reveal button works.
- [ ] **Step 3:** Commit any fixes.

---

## Phase 10 — Batch generation + deploy

### Task 10.1: Generate 730 days

- [ ] **Step 1:** From `build/`:

```bash
uv run squaredle-gen \
  --start 2026-04-14 --days 730 --seed 20260414 \
  --hspell data/hspell/words.txt \
  --freq data/opensubtitles-he-freq.txt \
  --freq-top-n 40000 \
  --blacklist data/blacklist.txt \
  --out ../site/puzzles
```

- [ ] **Step 2:** Spot-check 3 random puzzles for sanity.
- [ ] **Step 3:** Commit: `feat(data): pregenerate 730 days starting 2026-04-14`.

### Task 10.2: GitHub Actions `workflow_dispatch`

**Files:** Create `.github/workflows/generate.yml`.

- [ ] **Step 1:** Write:

```yaml
name: generate
on:
  workflow_dispatch:
    inputs:
      start:
        description: "Start date YYYY-MM-DD"
        required: true
      days:
        description: "Days to generate"
        required: true
        default: "365"
jobs:
  gen:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install uv
      - run: cd build && uv sync
      - run: |
          cd build && uv run squaredle-gen \
            --start "${{ inputs.start }}" --days "${{ inputs.days }}" --seed 20260414 \
            --hspell data/hspell/words.txt \
            --freq data/opensubtitles-he-freq.txt \
            --freq-top-n 40000 \
            --blacklist data/blacklist.txt \
            --out ../site/puzzles
      - run: |
          git config user.name "github-actions"
          git config user.email "actions@users.noreply.github.com"
          git add site/puzzles
          git commit -m "data: extend puzzle horizon" || echo "nothing to commit"
          git push
```

- [ ] **Step 2:** Commit.

### Task 10.3: GitHub Pages

- [ ] **Step 1:** Enable Pages from `main` branch, `/site` folder, in repo settings.
- [ ] **Step 2:** Verify URL loads puzzle for today's Jerusalem date.

---

## Self-review

- **Spec coverage:** §1 features → Phase 9; §2.1 normalization → 1.1; §2.2 display → 7.1/9.2; §2.3 excluded tokens → 1.1 is_acceptable; §3 dictionary → 2.1/2.2; §4 generation → 5.1/5.2/8.1; §5 acceptance → 6.1; §5.1 difficulty → 6.2; §6 JSON schema → 8.1; §7 frontend → 9.1-9.8; §8 deploy → 10.1-10.3; §9 testing → threaded through. Covered.
- **Placeholders:** none.
- **Type consistency:** `generate_grid` signature used the same way in `cli.py`. `accept_puzzle(answers, anchor=...)` consistent. `toDisplay` / `to_display` named per language convention; both take a single word string. `cellFromPoint` returns `{row, col, el}` and is used consistently.
- **Gap spotted:** Acceptance rule "max length >= 6 (easy) or >= 7 (medium/hard)" from spec §5 was simplified in Task 6.1 to "max length >= 6" (single cut). Rationale: difficulty is classified *after* acceptance, so threshold can't depend on difficulty; the single-cut version is correct. Noted here to avoid later confusion.
- **Optional YAP lemma-family check:** spec §5 lists this as optional; I did not create a task for it. Deferred past v1 if the plural heuristic proves sufficient.
