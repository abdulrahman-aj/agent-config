---
name: ask-for-review
description: Use when requesting an independent review of a diff, commit, range, or PR.
---

## Scope

Review the requested changes, or the current task's changes including untracked files.
Ask if you cannot tell which changes belong to the task; leave unrelated work out.

## Reviewers

Follow the Agent delegation rules in `~/.agents/AGENTS.md` and applicable project
instructions for reviewer count and allowed providers. Use an independent agent
that did not author the changes. Prefer a different model family when suitable,
but do not add reviewers just for diversity. Tell the user if a requested reviewer
cannot be used or fewer reviewers are available; self-review if none are.

## Delegate

In T3, select available providers and models with `orchestrator_capabilities`.
Use `delegate_task` with `role: "review"` and `mode: "async"`; retain its `taskId`
and use a distinct, retry-stable `clientRequestId` per reviewer and round. Native
same-provider delegation is suitable only when it supports the selected model.
Outside T3, use the runtime's native delegation when available.

Start independent reviewers in parallel when more than one is needed. Include the
repository path, exact review scope, relevant instructions, expected behavior,
and check results, not your conclusions on the first pass. Include the diff and
untracked files for an isolated review of uncommitted changes: T3 child worktrees
start from the local commit, without those files or the parent conversation.

Instruct the reviewer to:

- Look for bugs, broken existing behavior, and security or performance problems.
- Run checks in an isolated environment; do not change the author's checkout or external services.
- List problems from most to least serious, with `path:line`, evidence, and a suggested fix.
  Say if no problems were found and what could not be checked.

## Resolve

Check findings before changing code. Fix confirmed blockers; explain rejected findings.
If unsure, reproduce the problem or get another opinion. Ask the user when the
intended behavior or acceptable risk is unclear.

T3 delivers completion notifications; use `task_status` when needed mid-turn and
`task_cancel` for unwanted tasks. For every T3 review round, call `delegate_task`
again with the original brief, updated diff, prior findings, responses, and
unresolved objections. Track the new task and request IDs; do not resume a review
by messaging its backing child thread. The same model may check fixes in a new
task. Outside T3, continue an existing reviewer when the runtime supports it.
Do not repeat unaffected reviews. Report remaining risks and unrun checks.
