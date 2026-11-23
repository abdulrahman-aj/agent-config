---
name: request-review
description: Brief a reviewer and act on its findings. Load before you ask for a review, act on review findings, or run cheap reviews of your own delegated work.
---

# Request a review

Tell the reviewer to load `review`, and give it:

* **Revision.** Commit first and name the commit, so the reviewer reads a fixed revision,
  not half-applied fixes.
* **Spec.** Task requirements, project rules and the work's claims, so the work can't
  narrow its own spec. For rules or structure, ask where each line belongs as well as what
  it means.
* **Correct alternatives.** The project's own solutions that the task still supports.
* **Settled findings.** Findings rejected in earlier gates, with reasons. Leave out what a
  worker rejected from its cheap reviews, so the gate judges those afresh.
* **Re-checks.** Name the earlier findings. Send it to the same reviewer, in its existing
  thread, unless that reviewer's family wrote the fix.

## Act on gate findings

* Judge severity yourself, because reviewers rate high. A blocker causes serious harm or
  makes the central claim false. A major gives a user who follows the work a wrong
  outcome, breaks a stated behavior or rejects a correct alternative.
* Fix every real blocker and major. Accepted suggestions join the spec. Get a re-check
  after fixing a blocker, a major or an accepted suggestion. Fixes to minors alone need
  none.

## Cheap reviews

Cheap reviewers are a filter, not a gate. Treat their findings as leads to verify before
acting, and skip re-checks. They catch house-rule slips, sentences the change made false,
deleted comments and edits beyond the task.
