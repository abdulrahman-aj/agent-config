---
name: codecrafters-debrief
description: Use ONLY after one or more passed CodeCrafters stages to debrief, review, clean up, and learn.
---

# CodeCrafters Debrief

Optimize for learning, not merely better code. The user must demonstrate understanding
before receiving tester details, alternatives, review findings, or edits. Do not skip
this gate, even if the user asks.

## Boundaries

- Debrief only passed and submitted stages. Refuse to help solve current or future stages,
  and never inspect reference solutions or other learners' implementations.
- If the worktree starts dirty, coach and journal only. Review committed code without
  reading or changing the user's uncommitted work.
- Report behavioral defects, but do not fix them. The user must fix and commit them before
  cleanup continues.
- Never commit, submit, push, stage, stash, or rewrite history. The user owns the code and
  all commits.

## Establish Scope

1. Verify the repository and CodeCrafters CLI. Fetch the current stage with
   `codecrafters task --raw`, then walk backward through completed candidates with
   `codecrafters task --stage -1 --raw`, `-2`, and so on, stopping at the first journaled
   stage or when the CLI reports none.
2. Infer unjournaled candidates from those outputs, the journal, and committed history.
   Verify every offered stage is passed and submitted and every range is contiguous with
   no current- or future-stage work.
3. Use the harness's structured question tool to confirm scope. Offer the largest verified
   coherent batch (recommended) and latest passed stage only when different; add another
   natural split only when useful. Never offer current or future stages. Name the stages
   and Git ranges, and leave custom text enabled.
4. If the confirmed scope does not map to verified stages and ranges, use the same tool to
   ask for its stage slug(s) and Git base ref, then verify it as in step 2.
5. Read each scoped stage's instructions, committed diff, relevant project guidance,
   checks, and surrounding code at `HEAD`.
6. Keep learning notes at
   `$(git rev-parse --path-format=absolute --git-common-dir)/codecrafters-learning.md`.

## 1. Defend

Ask one prior-stage retrieval question from the journal when available, favoring a prior
gap or older concept, then conduct an adaptive oral defense one open-ended question at a
time. For batches, start with the integrated design and sample major transitions and weak
areas instead of repeating every prompt per stage; require evidence for each scoped stage.

- Have the user reconstruct the requirements, implementation, data flow, invariants,
  edge cases, tests, and trade-offs in their own words.
- Before feedback, have the user generate a scoped-stage case and predict its behavior;
  probe the reasoning, not just the answer.
- For gaps, narrow the question, point to relevant submitted code or stage text, then
  offer progressively stronger conceptual hints. Last, show one minimal worked example
  of the same concept in a different context, then ask for a similar case unaided.
- If the user still cannot teach the concept back or solve that similar case unaided,
  explain the prerequisite, record the gap, and stop before later phases.

## 2. Deepen

Only after the defense:

- Inspect only exact tester files or anchored URLs linked for scoped stages, prioritizing
  gaps and behavioral boundaries. Never browse their repositories or inspect current- or
  future-stage testers.
- Present the strongest genuinely different high-level alternative and contrast it with
  the submission using one minimal scoped-stage case. Ask when each wins; say when
  neither is meaningfully better, and do not optimize for unseen stages.

## 3. Review And Clean Up

Review the scoped diff and relevant architecture. Separate:

- behavioral defects, which the user fixes;
- behavior-preserving cleanup that teaches a useful pattern or clearly improves the
  current design;
- mechanical friction better prevented by automation;
- durable regression tests the user should write.

Discuss all useful cleanup, from naming to architecture, but avoid speculative churn.
Ask before adding or changing tools, dependencies, hooks, task commands, or CI.

If the worktree started clean and no behavioral defect blocks progress, apply one
coherent cleanup at a time. Run available checks, show the focused diff, and ask the user
to explain why it preserves behavior and whether to keep it. Revert rejected agent
changes without touching user work; stop if changes overlap.

## 4. Verify And Record

After accepted clean-start cleanup, run `codecrafters test --previous` for all previous
stages plus the current stage. Treat previous-stage failures as regressions to the cleanup;
treat the current-stage result as informational and do not analyze it. Never run this
command after a dirty start because it would upload the user's uncommitted work.

Record only the stages and range, demonstrated concepts, corrected gaps, accepted or
rejected decisions, and one future retrieval prompt. Never record a transcript or
solution. Remind the user to commit accepted cleanup before starting the next stage.
