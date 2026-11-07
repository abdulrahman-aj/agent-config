---
name: orchestrate
description: Rules for running T3 workers as delegate_task children. Load before you delegate, when a child looks stalled, and before you replace or hand off a worker.
---

# Orchestrate

## Where you run
* **Home project.** Run from the project you orchestrate. `delegate_task` starts local children only in your thread's project, so if you're elsewhere, move before you start anything. For another repo, start the child from your project and point it at that repo's checkout.
* **Children, not threads.** Start workers with `delegate_task`. Only children wake you when they finish and show up in your chat. Use `t3_thread_launch` only when the user asks for a new thread. Schedule wakes only for waits T3 can't see, such as a quota reset or CI.
* **Remote checkouts.** A child on a linked environment runs in that project's checkout, and worktree isolation fails there. Run one writer per remote checkout, or point each child at its own existing worktree.

## While children run
* **Keep work moving.** While work remains, run independent work beside a blocked stream. End a turn only with a tracked child running, a picker question open, or the task done.
* **Ask with the picker.** Ask the user with the picker, not in prose.
* **Worker questions.** Check `t3_pending_request` on your children and answer their questions yourself.
* **Waits in briefs.** OpenCode may run long jobs as background tasks T3 can't see (see "Confirm the stall"). When a brief includes a long job, write the wait as a literal command step, like the PID wait under "Delegated work" in the global instructions.

## Stalled and finished children
* **Confirm the stall.** OpenCode resumes its model when a background job ends, even after T3 marked the run complete. Before you re-dispatch an OpenCode child, look for activity after that time in `~/.local/share/opencode/log/opencode.log` or with `pgrep -af`.
* **Resume with a new delegate.** Never continue a child with `t3_thread_send`. That run is untracked: nothing wakes you, and your thread leaves Working. Stop the old run with `task_cancel` when no foreground job would die, then `delegate_task` a resume brief that says what's on disk, what's done and what's left.
* **Clear queues.** Before you replace or hand off a worker, run `t3_queue list` on its thread (with `environmentId` if remote) and cancel stale items. Settling or archiving leaves the queue intact, and a queued background notice can restart the old worker.
* **Settle remote children.** T3 doesn't record the parent of a remote child, so settle finished ones with `t3_thread_organize settle` and their `environmentId`.
