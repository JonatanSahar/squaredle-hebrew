# Squaredle Hebrew — Design Spec

Date: 2026-04-14
Status: Draft → self-reviewed, ready for user review

## 1. Product summary

A Hebrew-language Squaredle clone deployed as a static site on GitHub Pages, playable on mobile browsers. Single-user audience (the user's partner). One daily puzzle. v1 scope:

- 5x5 letter grid
- Swipe (or tap-tap-tap) to connect 8-neighbor cells, no cell reuse
- Valid words are length >= 4 and appear in the puzzle's precomputed answer set
- Found/total word count + difficulty label
- "Reveal answers" after giving up
- localStorage progress per date
- Out of scope for v1: hints, sharing, bonus words, pangram, streaks, accounts

## 2. Hebrew text handling

### 2.1 Internal normalization (locked)
Applied everywhere in the pipeline: dictionary ingest, grid cells, matching:
1. Strip niqqud (Unicode range U+0591–U+05C7 except base letters).
2. Normalize sofit ך→כ, ם→מ, ן→נ, ף→פ, ץ→צ.
3. Remove maqaf (U+05BE), geresh (U+05F3), gershayim (U+05F4), punctuation.
4. Keep only words consisting entirely of Hebrew base letters א–ת post-normalization.
5. Filter to length >= 4.

### 2.2 Display
**Grid**: always renders the normalized (non-sofit) letter. Any cell can serve as either a middle letter or a word-final letter — no information leak about where words end.

**Revealed answers and found-word log**: re-apply sofit at word-final positions via `display(word) = word with final char mapped via {כ→ך, מ→ם, נ→ן, פ→ף, צ→ץ}`, so Hebrew readers see standard orthography.

**Current-selection readout** (the word being traced): renders normalized letters (matches grid). Only "committed" words (in the found list or revealed list) get sofit-ified.

Rationale: one canonical form in grid and pipeline, orthographic correctness on revealed/found words, no positional clues from sofit placement.

### 2.3 Excluded tokens
Reject from the dictionary and from puzzle answers:
- Acronyms containing gershayim (צה"ל, דו"ח).
- Hyphenated compounds (אי-שם).
- Proper nouns (best-effort via frequency/POS filter — see §3).
- Loanwords flagged with geresh (ג'ינס' → rejected if the geresh form is what's attested; the normalized form without geresh is kept only if it independently appears in a non-geresh source).

## 3. Dictionary

### 3.1 Sources
- **Primary lexical superset**: Hspell 1.4 word list (AGPL).
- **Casual-usage filter**: OpenSubtitles Hebrew frequency list from `hermitdave/FrequencyWords` (CC BY-SA 4.0), top 30k–40k surface forms.
- **Acceptance rule**: a word enters the answer dictionary iff (normalized form is in Hspell) AND (normalized form appears in top-40k OpenSubtitles-he). Threshold tunable; start at 40k.
- **Optional secondary filter** (if dictionary feels sparse): union with top-20k Hebrew Wikipedia word frequencies built from a dump.

License note: Hspell is AGPL. Include `LICENSES/HSPELL.txt` and a NOTICE in the repo crediting Hspell and OpenSubtitles/OPUS. Personal GitHub Pages deployment is compatible.

### 3.2 Blacklist
Manual blacklist file `build/blacklist.txt` for garbage that slips through (slurs, stems that only appear as partial OCR, etc.). Empty at start; grow as needed.

### 3.3 No lemmatization at runtime
Lemmatization (YAP/HebPipe) is **optional, build-time only**, used as a puzzle acceptance filter (see §5), not to compress the dictionary. The dictionary is surface forms.

## 4. Puzzle generation

### 4.1 Pipeline
```
load dict → normalize → build trie →
  loop:
    plant anchor word(s) into 5x5 grid
    fill remaining cells with conditional sampling
    DFS solve with trie pruning (8-neighbor, no reuse, len>=4)
    apply acceptance checks (§5)
  until accepted
→ classify difficulty → write JSON
```

### 4.2 Grid generation (hybrid)
1. Pick a hidden **anchor word**, length 5–7, from the dictionary weighted by length (prefer 6).
2. Place it via a random self-avoiding 8-neighbor walk on the 5x5 grid. Retry on dead-end.
3. Optionally plant a **second word**, length 4–6, overlapping the anchor by 1–2 cells. Skip if it doesn't fit in 20 tries.
4. Fill remaining cells by sampling from a **conditional letter distribution** learned from the accepted answer dictionary: P(letter | set of already-placed letters). Fallback to unigram if sparse. Letters learned from the answer dictionary, not raw Hspell.
5. **Guardrails** (reject board and retry before even solving):
   - Combined count of {ו, י, ה, א} on the board <= 10 (of 25).
   - At least 12 distinct letters on the board.
   - No single letter appears more than 4 times.

### 4.3 Solver
Standard DFS from every cell, pruned against the trie. Output: set of all valid dictionary words reachable under rules. Expected runtime per board: <1s in Python.

## 5. Puzzle acceptance

A solved board is accepted only if all of:
- 20 <= |answers| <= 100.
- 4-letter words <= 70% of answers.
- count(length >= 5) >= 6.
- count(length >= 6) >= 2.
- max length >= 6 (easy) or >= 7 (medium/hard).
- **Lemma-family dominance** (if YAP available at build): no lemma family contributes more than max(15% of answers, 3 words).
- **Plural-domination heuristic** (no lemma step): words ending in ים or ות are <= 35% of answers.
- **Anchor found**: the planted anchor word is in the answer set (sanity).

### 5.1 Difficulty classification
After acceptance:
- **Easy**: 60 <= |answers| <= 100, max length 6–7.
- **Medium**: 35 <= |answers| < 60, max length >= 7.
- **Hard**: 20 <= |answers| < 35.
Label stored in the puzzle JSON.

## 6. Puzzle JSON schema

Path: `site/puzzles/YYYY-MM-DD.json`.

```json
{
  "date": "2026-04-14",
  "version": 1,
  "grid": ["אבגדה", "וזחטי", "כלמנס", "עפצקר", "שתאבג"],
  "answers": ["שלום", "אמא", "..."],
  "difficulty": "medium",
  "counts": {"total": 47, "by_length": {"4": 22, "5": 15, "6": 8, "7": 2}}
}
```

- `grid`: 5 strings of 5 normalized (non-sofit) letters each, row-major, logical order (row 0 = top, col 0 = leftmost visually in RTL = rightmost in the string's logical order? **Spec**: strings are logical-order arrays. The frontend maps logical col to visual position via RTL CSS, not by reversing the string. Tests verify a known puzzle renders correctly on iOS Safari.)
- `answers`: normalized forms. Frontend re-sofit-ifies on display.

## 7. Frontend

### 7.1 Stack
- Vanilla JS (ES modules), no framework.
- CSS Grid with `direction: rtl` for the board.
- Pointer Events API.
- No build step; ship source as-is.

### 7.2 Swipe interaction
- On `pointerdown` on a cell: `setPointerCapture`, start selection with that cell.
- On `pointermove`: `document.elementFromPoint(e.clientX, e.clientY)`; if the element is a cell AND adjacent (by stored row,col) to the last selected cell AND not already in the path, append it.
- On `pointerup` / `pointercancel`: check the formed word (normalized) against the answer set; on match, mark found; clear selection.
- Highlight/trace overlay uses `pointer-events: none`.
- Board container has `touch-action: none`.
- Cells have no real CSS gap; spacing is via inset borders/shadows.
- Adjacency is computed from the `(row, col)` model attached to each cell, **never** from DOM order.

### 7.3 Tap-tap-tap fallback
First-class, not optional. Single taps add cells; double-tap or a "submit" button confirms the word. Available regardless of swipe support.

### 7.4 State & persistence
- `localStorage` key: `squaredle-he:v1:YYYY-MM-DD`.
- Value: `{ found: [normalized words], revealed: bool, firstPlayedAt: iso }`.
- On load for a given date: hydrate found set; if `revealed`, show full answer list.
- Caveat documented in-app: localStorage may be cleared by mobile Safari under storage pressure or private browsing. Acceptable for v1.

### 7.5 Date boundary
Puzzle date = **Asia/Jerusalem local date**, computed client-side from `Intl.DateTimeFormat('en-CA', {timeZone: 'Asia/Jerusalem'})`. Documented: playing outside Israel surfaces Israeli-local date, which is intended.

### 7.6 "Reveal answers"
Button behind a confirmation ("Give up and reveal?"). Sets `revealed: true`, shows full answer list with sofit-applied display, groups by length.

## 8. Build & deploy

### 8.1 Pregeneration strategy
Pregenerate **730 days** (two years) of puzzles in one batch and commit to `site/puzzles/`. Rationale: removes GitHub Actions cron fragility (auto-disable after 60d inactivity, scheduled-workflow backlogs, puzzle availability coupled to Actions uptime).

### 8.2 GitHub Actions
Only `workflow_dispatch` (manual) workflow to rerun generation and commit. No cron. User runs it locally or via dispatch when the pregenerated horizon is < 60 days out.

### 8.3 Repo layout
```
/
├── build/
│   ├── pyproject.toml
│   ├── squaredle/
│   │   ├── normalize.py        # sofit, niqqud, filtering
│   │   ├── dictionary.py       # load Hspell ∩ OpenSubtitles
│   │   ├── trie.py
│   │   ├── grid.py             # sampling + anchor planting
│   │   ├── solver.py           # DFS
│   │   ├── acceptance.py       # §5 checks
│   │   ├── difficulty.py
│   │   └── cli.py              # generate --start YYYY-MM-DD --days N
│   ├── data/
│   │   ├── hspell/             # committed (AGPL notice)
│   │   ├── opensubtitles-he-freq.txt
│   │   └── blacklist.txt
│   └── tests/
├── site/
│   ├── index.html
│   ├── styles.css
│   ├── js/
│   │   ├── main.js
│   │   ├── board.js
│   │   ├── input.js            # pointer + tap fallback
│   │   ├── state.js            # localStorage
│   │   └── display.js          # sofit re-application
│   └── puzzles/
│       └── YYYY-MM-DD.json
├── .github/workflows/generate.yml  # workflow_dispatch only
├── LICENSES/
│   └── HSPELL.txt
└── NOTICE
```

## 9. Testing

### 9.1 Build-side (pytest)
- Normalization unit tests: sofit, niqqud, rejection of acronyms/geresh.
- Dictionary load: deterministic size given fixed inputs.
- Trie: membership, prefix.
- Solver: hand-crafted tiny board → known answer set.
- Acceptance: edge cases for each rule.
- Difficulty classification boundaries.
- End-to-end: generate 10 puzzles with fixed seed, snapshot their `counts` and difficulty labels.

### 9.2 Frontend
- Manual test matrix: iOS Safari (primary target), Chrome mobile, Firefox desktop.
- Scripted: a Node-based test that loads `site/js/display.js` and verifies sofit re-application for a battery of words.
- Adjacency unit tests (pure JS, no DOM).

## 10. Open items deferred past v1

- Sharing / streaks.
- Hints.
- Pangram / bonus word highlighting.
- Multi-lingual switch.
- PWA install.

## 11. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Hspell orthography feels too formal | OpenSubtitles intersection; manual blacklist; threshold tuning |
| Dictionary still surfaces archaic inflections | Optional YAP lemma-family acceptance filter (§5) |
| Swipe unreliable on iOS Safari | Tap-tap-tap as first-class fallback |
| localStorage eviction | Documented caveat; acceptable for single-user gift |
| AGPL compliance | LICENSES/ + NOTICE; personal static deploy compatible |
| Pregeneration horizon runs out | Lightweight manual workflow_dispatch; check horizon on each visit (frontend logs a console warning if fewer than 30 days remain) |

## 12. Self-review

- **Placeholders**: none left.
- **Consistency**: sofit decision is overridden once in §2.2 and referenced consistently elsewhere (§6 answers stored normalized, §7.6 display re-sofits). JSON schema matches frontend expectations. Adjacency model single-sourced to (row,col).
- **Scope**: v1 list in §1 is mirrored in §10 deferred list — no feature double-listed.
- **Ambiguity**: "top 30k–40k" left as a tunable; stated default 40k. Anchor-word length range specified. Difficulty thresholds concrete.
- **Untested assumptions**: (a) Hspell ∩ OpenSubtitles-40k is large enough to generate boards with 20+ answers — to be validated in the first build iteration; if too sparse, widen to 60k or union with Wikipedia top-20k. (b) conditional-letter-frequency fill produces varied boards — fallback is simple unigram with guardrails.
