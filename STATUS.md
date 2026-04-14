# Squaredle Hebrew — Status

Last updated: 2026-04-14

## Done

- Brainstorming complete (see prior `HANDOFF.md`).
- Codex consulted (one-shot — see caveat below).
- **Spec** written and self-reviewed: `docs/superpowers/specs/2026-04-14-squaredle-hebrew-design.md`.
- **Implementation plan** written (10 phases, ~30 tasks, TDD, bite-sized): `docs/superpowers/plans/2026-04-14-squaredle-hebrew.md`.
- Sofit display decision finalized: grid shows normalized letters only; sofit re-applied only on revealed/found-word display. (Spec §2.2 and plan Task 9.7.)
- `collaborate-with-codex` skill hardened with a pre-synthesis weakness-audit forcing function and skeptical-review framing (local skill: `.claude/skills/collaborate-with-codex/SKILL.md`).

## Not done

- Repo is not yet a git repo. Plan Task 0.1 initializes it.
- No code written. No data downloaded.
- Codex was only consulted once (single rescue dispatch, five questions, no follow-up). Two items in the Codex reply are known-underspecified and should be tightened before Phase 2/5 start:
  - **Dictionary size unverified.** Hspell ∩ OpenSubtitles-top-40k may produce too few or too many words. Plan assumes tunable (`--freq-top-n`) but needs a sanity check after Task 2.2 downloads the real data; may require widening to 60k or unioning with Wikipedia top-20k.
  - **Grid fill formula vague.** Plan Task 5.2 uses unigram-frequency fill with guardrails. Spec §4.2 described "conditional letter distribution P(letter | already-placed)"; I fell back to unigram. If generated boards feel samey, revisit.

## Pick up here

1. Start a fresh session. Re-invoke `superpowers:using-superpowers`.
2. Read the spec (`docs/superpowers/specs/2026-04-14-squaredle-hebrew-design.md`) and plan (`docs/superpowers/plans/2026-04-14-squaredle-hebrew.md`).
3. Decide execution mode:
   - **Subagent-driven** (recommended): `superpowers:subagent-driven-development` — fresh subagent per task, two-stage review. Best if tokens allow.
   - **Inline**: `superpowers:executing-plans` — batch with checkpoints.
4. Before Phase 2 (dictionary), briefly collaborate with Codex again to tighten the two open items above. Use the **updated** `collaborate-with-codex` skill — the pre-synthesis weakness audit is now required.
5. Begin with Phase 0 (project skeleton, git init).

## Open questions for user (non-blocking)

- Horizon size: plan pregenerates 730 days. Confirm you're OK with ~730 JSON files committed to the repo, or prefer 365.
- Blacklist seed: starts empty. Any words you already know should be blacklisted (slang, profanity, in-jokes to avoid)?
- Difficulty labels: spec uses Easy/Medium/Hard. Hebrew labels currently hard-coded in `main.js` as קל/בינוני/קשה. Confirm or supply alternatives.

## Key decisions locked

- Hebrew text: strip niqqud, fold sofit everywhere in pipeline; re-sofit only on revealed/found-word display.
- Dictionary: Hspell ∩ OpenSubtitles-he top-40k, AGPL compliance via NOTICE + LICENSES/.
- Acceptance: 20–100 answers, 4-letter ≤70%, ≥6 words len ≥5, ≥2 words len ≥6, max len ≥6, plural-ending (ים/ות) ≤35%.
- Grid: anchor-planted (len 5–7) + frequency fill + guardrails (ו/י/ה/א ≤10, ≥12 distinct, ≤4 of any letter).
- Deploy: pregenerate 730 days in one commit; GH Actions `workflow_dispatch`-only (no cron).
- Date: Asia/Jerusalem client-side via `Intl.DateTimeFormat`.
- Frontend: vanilla ES modules, CSS RTL grid, Pointer Events + tap fallback, localStorage per-date.

## Caveat on this session's Codex consultation

I ran Codex once with five questions in one prompt, received a long detailed reply, and went straight to synthesis. The `collaborate-with-codex` skill says to treat the first answer as a draft and iterate 1–3 times; I skipped that. Consequences baked into the current spec/plan:
- Sofit handling needed user correction twice (once to restore grid-side sofit, then back to normalized-only). A single follow-up round would have surfaced that the standard Hebrew word-game compromise doesn't apply here.
- Dictionary size and fill-formula items above are unverified.

The skill was updated this session to prevent this failure mode (mandatory pre-synthesis weakness audit + skeptical framing). Future Codex consultations on this project should use the updated version.
