---
name: parallel-work
description: Use to run approved independent tasks in parallel, each in its own worktree.
---

# Parallel Work

Use for authorized tasks that can be implemented independently. Follow the Agent
delegation rules in `~/.agents/AGENTS.md` and applicable project instructions.

1. Resolve material scope questions before starting dependent work. Check whether
   required code is uncommitted: T3 child worktrees start from the parent's local
   commit. Supply a scoped patch or artifacts, or obtain approval to commit the
   required base. Do not assume the worker sees parent edits or conversation.
2. In T3, select available providers and models through `orchestrator_capabilities`
   and call `delegate_task` with `isolation: "worktree"`, `role: "implementation"`,
   and `mode: "async"`. Use a distinct, retry-stable `clientRequestId` per task and
   retain its `taskId`. Outside T3, use supported native delegation and separate
   worktrees. If unavailable, explain the limitation and work sequentially.
3. Give each worker its scope, relevant instructions, dependencies, expected
   behavior, and checks. Require changes to stay in its checkout. Return the
   worktree path, full diff including untracked files, checks, and risks. Permit
   commits or pushes only when the user has authorized them.
4. Continue independent work while children run. T3 notifies the parent on
   completion; use `task_status` only when needed and `task_cancel` for unwanted
   tasks. Do not create top-level conversations for delegated tasks.
5. Review each full diff; use `ask-for-review` when independent review is warranted.
   Fix confirmed problems and verify fixes. Corrections in a new T3 task need the
   original brief, findings, and prior diff or approved commits.
6. Present changes, checks, and risks before requesting any still-required commit
   or merge approval. Once authorized, integrate and check the combined result.
   Remove worktrees only after verifying integration and that no uncommitted or
   unrelated work would be lost.
