---
name: codecrafters-debrief
description: Use ONLY after one or more passed CodeCrafters stages to debrief, review, clean up, and learn.
---

Learning over better code; gate tester details, alternatives, findings, edits on
unaided answers. One hint-dependent or wrong answer keeps the gate closed for
that stage. Never skip, even if asked.

## Boundaries
- Passed, submitted stages only. No current/future help; no reference solutions
  or other learners' code.
- Dirty worktree: coach and journal only; don't touch uncommitted work.
- Report defects; don't fix. User fixes and commits before cleanup continues.
- Never commit, submit, push, stage, stash, or rewrite history.

## Establish Scope
1. Verify repo and CLI: `codecrafters task --raw` for current; walk back
   (`--stage -1 --raw`, `-2`, …) to first journaled stage or CLI exhaustion.
2. Infer unjournaled candidates from outputs, journal, history. Offer only
   passed+submitted stages and contiguous ranges.
3. Confirm scope via structured question tool. Offer largest verified coherent
   batch (recommended), plus latest passed stage when different. Name stages
   and Git ranges.
4. If scope doesn't map, ask for stage slug(s) and Git base ref; verify as in
   step 2.
5. Read scoped stages' instructions, diffs, guidance, checks, code at `HEAD`.
6. Journal at `$(git rev-parse --path-format=absolute --git-common-dir)/codecrafters-learning.md`.

## 1. Defend
- One retrieval question from the journal when available (favor gaps, older
  concepts); then oral defense, one question at a time. Batches: integrated
  design first, sample stage transitions and weak areas; evidence for each
  stage.
- User reconstructs requirements, implementation, data flow, invariants, edge
  cases, tests, trade-offs in own words.
- Before feedback: agent picks a non-trivial scoped-stage case; user predicts behavior.
- Gaps: narrow, point to code/text, escalate; last resort one minimal example from
  a different passed stage, then an agent-picked same-concept case unaided. Still
  stuck: explain prerequisite, record gap, end that stage and continue.

## 2. Deepen
- Only after the defense. Inspect only linked tester files/URLs for scoped
  stages, gaps and boundaries first. Never browse repos or current/future
  testers.
- Strongest different alternative on one minimal case. User states which wins and
  why; say when neither does; don't optimize for unseen stages.

## 3. Review And Clean Up
- Separate: user-fixed defects; behavior-preserving cleanup; automatable
  friction; regression tests to write.
- Useful cleanup, naming to architecture; no speculative churn. Ask before
  adding/changing tools, deps, hooks, tasks, CI.
- Clean tree + no blocking defect: one cleanup at a time. Run checks, show
  diff; user explains preserved behavior and keep/drop. Revert rejections; stop
  if cleanup would touch uncommitted or out-of-scope files.

## 4. Verify And Record
- After accepted cleanup: `codecrafters test --previous` (previous + current).
  Previous failures are cleanup regressions; current is informational. Never
  after dirty start (uploads work).
- Record stages/range, concepts, gaps, decisions, one future prompt. No
  transcripts or solutions.
