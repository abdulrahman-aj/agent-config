---
name: review
description: How to give a review that converges. Load before you review work, or when a brief asks for a review.
---

# Review

Keep what you can verify apart from opinion, and let only the verified part block.

Judge the work against the spec in your brief: the task's requirements, the project rules,
and every claim the work makes. A correct alternative the brief lists must pass. Don't
raise a finding the brief lists as settled. Don't delegate, because the caller needs your
own judgment.

## Report

Number the findings consecutively across sections, and report in this order:

1. **Header.** PASS or FAIL; the count in each section, with how many are blocker or major;
   and "Most important: #N", or "Most important: none" for a clean review.
2. **Facts against the spec.** A requirement the work misses, a rule it breaks, a claim a run
   contradicts, or another defect.
3. **False fails.** A correct alternative that the work rejects.
4. **Suggestions.** Anything beyond the spec: a new test case, a known pitfall, an
   improvement.
5. **Checked and sound.** One line on what you checked and found right, so silence reads as
   checked rather than skipped.

Open each finding with one line: its number, its severity (sections 2 and 3 only) and the
claim. Then fill these fields:

* **Evidence.** Ran it (the command and its output) or reasoned (the exact reasoning). Run
  it when you can.
* **Impact.** One sentence: "A user who ___ will ___." The user is whoever uses or
  maintains the work. Drop a finding that can't fill this honestly; don't downgrade it.
* **Source.** The requirement, rule or claim it breaks. For a suggestion, or a failure case
  the spec doesn't name: the project names or warns about it, the project solves it
  elsewhere, or it's a known common mistake or practice, which you name. Drop an invented
  case with no source.
* **Fix.** The smallest fix, and its size: a line, small or large.

## Severity

Take the highest that applies:

* **Blocker.** Shipped as it is, the work does serious harm, such as lost data, a security
  hole or lost money, or its central claim is false.
* **Major.** A user who follows the work gets a wrong outcome, a stated behavior fails, or a
  correct alternative fails.
* **Minor.** Any other real defect: confusing, imprecise, or a broken rule with no wrong
  outcome.

The verdict is PASS when sections 2 and 3 hold no blocker or major. Suggestions never block.
