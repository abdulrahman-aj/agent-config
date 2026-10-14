---
name: parallel-work
description: Use to run approved independent tasks in parallel, each in its own worktree.
---

# Parallel Work

Use for user-approved tasks that can be done independently. Get permission to commit locally.

1. Ask necessary implementation questions in one message; wait for answers.
2. Create (or reuse) a worktree for each task — see `wt switch --help`.
3. Start workers in parallel. Give each its task, worktree path, and check commands.
   Keep edits in that worktree; commit locally, never push. Return commits, check results, and risks.
4. Review all changes for each task, not just its latest commit; follow `ask-for-review`.
   Send confirmed problems back to the worker and check that the fixes resolve them.
5. Summarize changes, check results, and unresolved questions. Ask permission to merge.
6. After approval, merge, resolve conflicts, and check the combined result.
   Only if checks pass, run `wt remove <branch>` (deletes the branch if merged).
