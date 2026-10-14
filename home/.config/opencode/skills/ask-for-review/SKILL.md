---
name: ask-for-review
description: Use when requesting an independent review of a diff, commit, range, or PR.
---

## Scope

Review the requested changes, or the current task's changes including untracked files.
Ask if you cannot tell which changes belong to the task; leave unrelated work out.

## Reviewers

Follow `agent-delegation.md` for reviewer count and allowed providers. Never choose
the author or the same reviewer twice, even as a replacement. Prefer a different
model family, but do not add reviewers just for diversity. Tell the user if a requested
reviewer cannot be used or fewer reviewers are available; self-review if none are.

## Delegate

Start reviewers in parallel. Give them the repository path, changes to review,
expected behavior, and check results, not your own conclusions. Send the diff if
they cannot access the repository.

Instruct the reviewer to:

- Look for bugs, broken existing behavior, and security or performance problems.
- Run checks in an isolated environment; do not change project files or external services.
- List problems from most to least serious, with `path:line`, evidence, and a suggested fix.
  Say if no problems were found and what could not be checked.

## Resolve

Check findings before changing code. Fix confirmed blockers; explain rejected findings.
If unsure, reproduce the problem or get another opinion. Ask the user when the
intended behavior or acceptable risk is unclear.

Keep reviewer `task_id`s to resume unfinished reviews and check fixes with the same
reviewer. Do not repeat unaffected reviews. Report remaining risks and unrun checks.
