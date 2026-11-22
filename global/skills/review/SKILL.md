---
name: review
description: Brief, give and act on reviews that converge. Load before you brief a reviewer, review work, act on review findings, or return delegated implementation work.
---

# Review

A review earns its cost when its findings can be checked and its verdict can pass. Keep what
can be verified apart from opinion, and let only the verified part block.

## Briefing a reviewer

Give the reviewer what it can't find alone:

* **The spec.** What the work claims: its behavior, its tests or checks and what each one
  catches, its stated contract, and every claim its prose makes. The reviewer judges against
  this.
* **Correct alternatives that must pass.** Search the project for its own solutions to the
  same problem and list them. A test or rule that rejects the project's own pattern is a bug.
* **Settled findings.** List the findings already rejected, each with its reason, so they
  don't come back.
* **Scope.** A first review covers the whole change. A re-check after fixes judges only the new
  diff and whether the earlier findings are fixed, but reruns everything mechanical: every
  test, every known wrong variant and every correct alternative.
* **Permissions.** Say whether it's read-only and what it may run. A reviewer never delegates,
  because the caller needs that reviewer's own judgment.
* **Family.** The reviewer comes from a different model family than the author.

## Giving a review

Report in this order:

1. **Header.** PASS or FAIL, the count in each section, and "Most important: #N".
2. **Facts against the spec.** A claim of the spec that a run contradicts, or a defect in the
   work.
3. **False fails.** A correct alternative that the work rejects.
4. **Suggestions.** Anything beyond the spec: a new test case, a trap, an improvement.
5. **Checked and sound.** One line on what you checked and found right, so silence reads as
   checked rather than skipped.

Open each finding with one line, then fill these fields:

* **Evidence.** Ran it (the command and its output) or reasoned (the exact reasoning). Run it
  when you can.
* **Impact.** One sentence: "A user who ___ will ___." Name the user the work serves, such as a
  reader or a caller. Drop a finding that can't fill this honestly; don't downgrade it.
* **Source.** For suggestions and for wrong inputs the spec doesn't name: where the mistake
  comes from. Keep it if the project names or warns about it, or solves it elsewhere. Keep it
  if it's a known common mistake, and name it. Drop an invented variant with no source.
* **Fix.** The smallest fix, and its size: a line, small or large.

Severity applies to sections 2 and 3 only:

* **Blocker.** The work does real harm, or teaches or documents something false.
* **Major.** A user following the work ships a bug, or a correct alternative fails.
* **Minor.** Confusing or imprecise, with no wrong outcome.

The verdict is PASS when sections 2 and 3 hold no blocker or major. Suggestions never block.

## Acting on a review

* Judge severity yourself. Reviewers rate high.
* Fix every real blocker and major. Fix the minors you agree with in the same change, without
  another review round.
* Merge when a re-check finds no blocker or major.
* An accepted suggestion joins the spec for the next round.

## Before returning delegated work

When your task produced work rather than a review, have two cheaper models from the model table
review your diff in parallel. Brief them with this skill, apply what you agree with, and list
what you rejected and why in your report. They catch mechanical slips: house rules, a sentence
your change made false, a deleted comment, edits beyond the task. They are a first filter,
not a gate. Skip this when your task is itself a review.
