---
name: review
description: How to give a review that converges. Load before you review work, or when a brief asks for a review.
---

# Review

Every finding should be signal: verifiable, sourced and worth acting on. Cut the noise, and
let only verified findings block.

Judge the work against the spec in your brief: the task's requirements, the project rules,
and every claim the work makes. A correct alternative the brief lists must pass. Don't
raise a finding the brief lists as settled. Don't delegate, because the caller needs your
own judgment.

A re-check after fixes judges only the new diff and whether the earlier findings are fixed,
and reruns everything mechanical: every test, every known failure case and every correct
alternative.

## Report

Number the findings consecutively, and report in this order:

1. **Header.** PASS or FAIL, and "Most important: #N", or "Most important: none" for a
   clean review.
2. **Facts against the spec.** A requirement the work misses, a rule it breaks, a claim a run
   contradicts, a correct alternative it rejects, or another defect.
3. **Suggestions.** Anything beyond the spec: a new test case, a known pitfall, an
   improvement.
4. **Checked and sound.** One line on what you checked and found right, so silence reads as
   checked rather than skipped.

Open each finding with one line: its number, its severity (facts only) and the
claim. Then fill these fields:

* **Evidence.** Ran it (the command and its output) or reasoned (the exact reasoning). Run
  it when you can.
* **Impact.** One sentence: "A user who ___ will ___." The user is whoever uses or
  maintains the work. Drop a finding that can't fill this honestly; don't downgrade it.
* **Source.** The requirement, rule or claim it breaks. For a suggestion, or a failure case
  the spec doesn't name: the project names or warns about it, the project solves it
  elsewhere, or it's a known common mistake or practice, which you name. Drop an invented
  case with no source.
* **Fix.** The smallest fix.

## Severity

Take the highest that applies:

* **Blocker.** Shipped as it is, the work does serious harm, such as lost data, a security
  hole or lost money, or its central claim is false.
* **Major.** A user who follows the work gets a wrong outcome, a stated behavior fails, or a
  correct alternative fails.
* **Minor.** Any other real defect: confusing, imprecise, or a broken rule with no wrong
  outcome.

The verdict is PASS when the facts hold no blocker or major. Suggestions never block.
