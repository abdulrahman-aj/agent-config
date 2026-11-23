---
name: request-review
description: Brief a reviewer and act on its findings. Load before you ask for a review, act on review findings, or run cheap reviews of your own delegated work.
---

# Request a review

Tell the reviewer to load `review`, and give it:

* **Spec.** Task requirements, project rules and the work's claims, so the work can't
  narrow its own spec.
* **Correct alternatives.** The project's own solutions that the task still supports.
* **Settled findings.** Findings rejected in earlier gates, with reasons. Leave out what a
  worker rejected from its cheap reviews, so the gate judges those afresh.
* **Re-checks.** Name the fix commit and the earlier findings. Send it to the same reviewer
  unless that reviewer's family wrote the fix.

## Act

* Judge severity yourself, because reviewers rate high. A blocker causes serious harm or
  makes the central claim false. A major gives a user who follows the work a wrong outcome.
* Accepted suggestions join the spec. Get a re-check after fixing a blocker, a major or an
  accepted suggestion. Fixes to minors alone need none.

## Cheap reviews

Run cheap reviewers after a commit, or on the worker's checkout, so they see the exact diff.
They are a filter, not a gate. They catch house-rule slips, sentences the change made false,
deleted comments and edits beyond the task.
