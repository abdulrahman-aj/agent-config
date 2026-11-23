---
name: review
description: Give a review that converges. Load before you review work, or when a brief asks for a review.
---

# Review

* Judge the work against the brief's spec, the project's rules and every claim the work
  makes. Correct alternatives the brief lists must pass. Skip settled findings. Never
  delegate.
* On a re-check, judge only the new diff and whether it fixes the earlier findings. Still
  rerun every mechanical check: tests, known failure cases and correct alternatives.

## Report

Start with PASS or FAIL. List facts against the spec, each with its severity, apart from
suggestions. Suggestions never block. PASS means no fact is a blocker or major.

Give each finding these fields. Drop a finding that can't fill one honestly; don't
downgrade it.

* **Evidence.** The command and its output when you can run it, otherwise the exact
  reasoning.
* **Impact.** One sentence on who gets hurt, a user or a maintainer, and how.
* **Source.** The requirement, rule or claim it breaks. For a suggestion or a failure case the spec doesn't name, cite where the
  project names, warns about or solves the problem, or name a known common mistake.

Severity for facts:

* **Blocker.** It causes serious harm if shipped, or the work's central claim is false.
* **Major.** A user who follows the work gets a wrong outcome, a stated behavior fails or a
  correct alternative fails.
* **Minor.** Any other real defect.
