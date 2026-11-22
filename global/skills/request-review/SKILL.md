---
name: request-review
description: Brief a reviewer and act on its findings. Load before you ask for a review, act on review findings, or run cheap reviews of your own delegated work.
---

# Request a review

## Brief

Tell the reviewer to load the `review` skill and report in its format. Then give it what it
can't find alone:

* **The spec.** The task's requirements, the project rules that apply, and every claim the
  work makes: its behavior, its tests and what each one catches, its contract, its prose.
  The reviewer judges against all three, so the work can't narrow its own spec.
* **Correct alternatives that must pass.** Search the project for its own solutions to the
  same problem, and list those the task still supports. A test or rule that rejects one of
  them is a bug. Give the same list to a worker who adds or changes a test or rule.
* **Settled findings.** List the findings that earlier review rounds rejected, each with its
  reason. Leave out what a worker rejected from its own cheap reviews; the reviewer judges
  those afresh.
* **Scope.** A first review covers the whole change. For a re-check, name the fix commit
  and list the earlier findings; the `review` skill says what a re-check covers.
* **Reviewer.** A different model family than the author's. Send a re-check to the reviewer
  that raised the findings, as long as its family still differs from the fix's author.
* **Permissions.** Whether it's read-only, and what it may run.

## Act on the findings

* Judge severity yourself; reviewers rate high. A finding blocks when the work does serious
  harm or its central claim is false (blocker), or when a user who follows it gets a wrong
  outcome, a stated behavior fails, or a correct alternative fails (major). When a finding
  is reasoned only and a run is cheap, run it.
* Fix every real blocker and major, the minors you agree with, and the suggestions you
  accept. An accepted suggestion joins the spec.
* After fixing a blocker, a major or an accepted suggestion, get a re-check. Fixes to minors
  alone need none.
* Once no real blocker or major remains, the change is ready: merge it where you're
  authorized to, or hand it to the user.

## Cheap reviews of delegated work

The global agent instructions say when a worker gets these. Run them on the worker's own
checkout, or after a commit, so they see the exact diff, and brief them as above. They
catch mechanical slips: house rules, a sentence the change made false, a deleted comment,
edits beyond the task, a test that rejects the project's own pattern. They are a first
filter, not a gate.
