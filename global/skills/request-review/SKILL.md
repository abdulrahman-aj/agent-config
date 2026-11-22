---
name: request-review
description: Brief a reviewer and act on its findings. Load before you ask for a review, act on review findings, or run cheap reviews of your own delegated work.
---

# Request a review

## Brief

Tell the reviewer to load the `review` skill and report in its format. Give it what it can't
find alone:

* **The spec.** Task requirements, applicable project rules and every claim the work makes
  (behavior, tests and what each catches, contract, prose). The reviewer judges against all
  three so the work can't narrow its own spec.
* **Correct alternatives that must pass.** Search the project for its own solutions to the
  same problem and list those the task still supports. A test or rule that rejects one is a
  bug. Give the same list to any worker adding or changing a test or rule.
* **Settled findings.** Findings rejected in earlier review rounds, each with its reason.
  Omit findings a worker rejected from its own cheap reviews; the reviewer judges those
  afresh.
* **Scope.** First reviews cover the whole change. For a re-check, name the fix commit and
  list earlier findings; the `review` skill defines re-check scope.
* **Reviewer.** Send a re-check to the reviewer that raised the findings, unless its family
  authored the fix.

## Act on the findings

* Judge severity yourself; reviewers rate high. A blocker causes serious harm or makes the
  central claim false. A major gives a user a wrong outcome, breaks a stated behavior or
  rejects a correct alternative.
* Verify a reasoned-only finding by running it when a run is cheap.
* Fix every real blocker and major, the minors you agree with and the suggestions you
  accept. Accepted suggestions join the spec.
* Get a re-check after fixing a blocker, a major or an accepted suggestion. Fixes to minors
  alone need none.
* When no real blocker or major remains, merge if authorized or hand the change to the user.

## Cheap reviews of delegated work

Brief low-cost reviewers as above, and run them on the worker's checkout or after a commit
so they see the exact diff. Use them as a first filter, not a gate. They catch mechanical
slips: house rules, sentences the change made false, deleted comments, edits beyond the
task and tests that reject the project's own patterns.
