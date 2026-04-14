# Squaredle Hebrew — Brainstorming Handoff

## Project goal
Build a Hebrew-language clone of Squaredle for the user's partner to play on her phone.

Squaredle: 5x5 letter grid; swipe to connect adjacent or diagonal cells (no cell reuse); words must be 4+ letters; UI shows found/total word count.

## Decisions made so far (with user)

1. **Deployment**: static web app on GitHub Pages (or similar). Playable on mobile browser; no install, no backend.
2. **Puzzle source**: precomputed daily puzzles. One JSON per date, built offline by a Python script.
3. **Sofit letters** (ך/ם/ן/ף/ץ): normalized to regular forms EVERYWHERE — grid, dictionary, matching, AND display. Display never shows sofit forms. (User explicitly chose option A1.)
4. **Niqqud**: stripped; dictionary is unvocalized ktiv male.
5. **Dictionary source**: TBD — Codex to research/recommend.
6. **Word count target**: 20–100 per puzzle, bucketed into difficulty tiers (e.g., Easy/Medium/Hard), labeled on the puzzle.
7. **v1 features**: core gameplay + "reveal answers after giving up" + localStorage progress persistence. NO hints, NO sharing, NO bonus words, NO pangram.

## Current stack hypothesis (not yet validated with Codex)

- **Python build script**: load dictionary → normalize (strip niqqud, normalize sofit, filter len>=4) → build trie → generate candidate 5x5 grid → DFS solver (8-neighbor, no cell reuse, trie-pruned) → accept if 20<=count<=100 → classify difficulty → write JSON.
- **Grid letter sampling**: weighted by dictionary-letter-frequency (hypothesis).
- **Frontend**: vanilla JS, RTL CSS grid, Pointer Events API for swipe, localStorage per-date progress.
- **Repo layout**: `build/` (Python) + `site/` (static). GitHub Action pregenerates next N days and commits `site/puzzles/YYYY-MM-DD.json`. GitHub Pages serves `site/`.

## Next step: consult Codex

The user asked to "think this through with codex" before writing the spec. Use `codex:rescue` skill with `--wait --fresh`. Open questions to ask Codex:

- **Q1 dictionary**: Best open Hebrew word list (Hspell, MILA, Hebrew Wiktionary, other)? How to filter to "words a casual player recognizes" vs every inflected rare-verb form? Need a frequency list — which?
- **Q2 grid sampling**: Dictionary-letter-frequency vs seed-word-planting vs bigram-aware? Best approach for Hebrew specifically given root morphology and dominant letters (ה/י/ו/א/ת)?
- **Q3 puzzle acceptance**: Beyond 20–100 count — min word-length distribution? Cap share-of-words from one root? Require >=1 long (6+) word? Avoid puzzles dominated by one noun's plurals?
- **Q4 mobile swipe UX**: Pointer Events + pointermove + elementFromPoint vs a library vs tap-tap-tap? iOS Safari + RTL + diagonal-connection gotchas?
- **Q5 build/deploy**: Pregenerate a year in one commit vs daily GitHub Action cron? Which is less fragile for a small personal project?

Also ask Codex to flag any flaw in the overall approach — especially Hebrew-specific issues.

## After Codex consultation

1. Synthesize Codex recommendations + user decisions into a design doc at `docs/superpowers/specs/YYYY-MM-DD-squaredle-hebrew-design.md`.
2. Per `superpowers:brainstorming` skill: spec self-review (placeholders, consistency, scope, ambiguity) → user review → invoke `superpowers:writing-plans` for implementation plan.
3. User is in `/use-codex` routing mode — prefer Codex for substantial implementation work once planning is done.

## Context notes
- Project dir: `/home/yonatan/Projects/personal/squaredle/` (empty except `.claude/`).
- Not a git repo yet.
- User profile (from CLAUDE.md): computational immunologist, Python-first, prefers concise direct answers, commits before/after changes.
- Tool issue hit in previous session: old `mcp__codex-cli__*` tools were removed; user installed fresh `codex@openai-codex` plugin and `/reload-plugins`. `codex:rescue` skill should now be available. If it isn't, check `/home/yonatan/.claude/plugins/` and ask user to verify plugin state.
