---
name: review
description: Brief, give and act on reviews that converge. Load before you brief a reviewer, review work, act on review findings, or return delegated work that changed files.
---

# Review

A review earns its cost when its findings can be checked and its verdict can pass. Keep what
can be verified apart from opinion, and let only the verified part block.

## Briefing a reviewer

Give the reviewer what it can't find alone:

* **The spec.** The task's requirements, the project rules that apply, and every claim the
  work makes: its behavior, its tests and what each one catches, its contract, its prose.
  The reviewer judges against all three, so the work can't narrow its own spec.
* **Correct alternatives that must pass.** Search the project for its own solutions to the
  same problem, and list those the task still supports. A test or rule that rejects one of
  them is a bug. Give the same list to a worker who adds or changes a test or rule.
* **Settled findings.** List the findings that earlier review rounds rejected, each with its
  reason, so they don't come back. Don't list what a worker rejected from its own cheap
  reviews; the reviewer judges those afresh.
* **Scope.** A first review covers the whole change. A re-check after fixes judges only the
  new diff and whether the earlier findings are fixed, and reruns everything mechanical:
  every test, every known failure case and every correct alternative.
* **Reviewer.** A different model family than the author's. Send a re-check to the reviewer
  that raised the findings, as long as its family still differs from the fix's author.
* **Permissions.** Say whether it's read-only and what it may run. A reviewer never
  delegates, because the caller needs that reviewer's own judgment.

## Giving a review

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
* **Impact.** One sentence: "A user who ___ will ___." The user is whoever the work serves
  or maintains it, such as a reader, a caller or a maintainer. Drop a finding that can't
  fill this honestly; don't downgrade it.
* **Source.** The requirement, rule or claim it breaks. For a suggestion, or a failure case
  the spec doesn't name: the project names or warns about it, the project solves it
  elsewhere, or it's a known common mistake or practice, which you name. Drop an invented
  case with no source.
* **Fix.** The smallest fix, and its size: a line, small or large.

Severity, taking the highest that applies:

* **Blocker.** Shipped as it is, the work does serious harm, such as lost data, a security
  hole or lost money, or its central claim is false.
* **Major.** A user who follows the work gets a wrong outcome, a stated behavior fails, or a
  correct alternative fails.
* **Minor.** Any other real defect: confusing, imprecise, or a broken rule with no wrong
  outcome.

The verdict is PASS when sections 2 and 3 hold no blocker or major. Suggestions never block.

## Acting on a review

* Judge severity yourself; reviewers rate high. When a finding is reasoned only and a run is
  cheap, run it.
* Fix every real blocker and major, the minors you agree with, and the suggestions you
  accept. An accepted suggestion joins the spec.
* After fixing a blocker, a major or an accepted suggestion, get a re-check. Fixes to minors
  alone need none.
* Once a review or re-check leaves no real blocker or major, the change is ready: merge it
  where you're authorized to, or hand it to the user.

## Cheap reviews of delegated work

A worker whose task changed files gets up to two reviews before it returns, from low-cost
models in the model table whose family differs from its own. Run them on the worker's own
checkout, or after a commit, so they see the exact diff. Brief them as this skill
describes. They catch mechanical slips: house rules, a sentence the change made false, a
deleted comment, edits beyond the task, a test that rejects the project's own pattern.
They are a first filter, not a gate.
