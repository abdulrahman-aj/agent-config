---
name: review
description: How to give a review that converges. Load before you review work, or when a brief asks for a review.
---

# Review

Every finding must be signal: verifiable, sourced and worth acting on. Cut noise, and let
only verified findings block.

* Judge the work against the brief's spec: task requirements, project rules and every claim
  the work makes.
* Any correct alternative the brief lists must pass.
* Skip findings the brief lists as settled.
* Don't delegate. The caller needs your own judgment.
* On a re-check, judge only the new diff and whether it fixes earlier findings. Still rerun
  every mechanical check: tests, known failure cases and correct alternatives.

## Report

Number findings consecutively across sections 2 and 3, and report in this order:

1. **Header.** PASS or FAIL, and "Most important: #N" (or "Most important: none" for a
   clean review).
2. **Facts against the spec.** A missed requirement, a broken rule, a claim a run
   contradicts, a rejected correct alternative or another defect.
3. **Suggestions.** Anything beyond the spec: a new test case, a known pitfall or an
   improvement.
4. **Checked and sound.** One line on what you checked and found right, so silence reads as
   checked rather than skipped.

Open each finding with one line: its number, its severity (facts only) and the claim. Then
fill these fields:

* **Evidence.** Run it when you can and show the command and output. Otherwise give the
  exact reasoning.
* **Impact.** One sentence: "A user who ___ will ___." Here "user" means anyone who uses or
  maintains the work. Drop any finding that can't fill this honestly; don't downgrade it.
* **Source.** For a fact, name the requirement, rule or claim it breaks. For a suggestion or
  an unnamed failure case, cite a real basis: the project names or warns about it, the
  project solves it elsewhere, or you name a known common mistake or practice. Drop any
  invented case with no source.
* **Fix.** The smallest fix.

## Severity

Take the highest that applies:

* **Blocker.** The work causes serious harm if shipped (lost data, a security hole or lost
  money), or its central claim is false.
* **Major.** A user who follows the work gets a wrong outcome, a stated behavior fails or a
  correct alternative fails.
* **Minor.** Any other real defect: confusing, imprecise or a broken rule with no wrong
  outcome.

The verdict is PASS when facts hold no blocker or major. Suggestions never block.
