---
name: orchestrate
description: Rules for running T3 workers as delegate_task children. Load before you delegate.
---

# Orchestrate

* **Children, not threads.** Start workers with `delegate_task`. Use `t3_thread_launch` only when the user asks for a new thread. Schedule wakes only for waits T3 can't see, such as a quota reset or CI.
* **Keep work moving.** While work remains, run independent work beside a blocked stream. End a turn only with a tracked child running, a picker question open, or the task done.
* **Ask with the picker.** Ask the user with the picker, not in prose.
* **Worker questions.** Check `t3_pending_request` on your children and answer their questions yourself.
* **Reviews.** Load `request-review` before briefing a reviewer or acting on its findings. If no agent started you, start implementers and strong gates yourself, and never brief a worker to start them. When the work adds or changes a test or rule, list in its brief the project's own solutions that must still pass.
* **Waits in briefs.** When a brief includes a long job, write the wait as literal steps: `agent-wait --start --log <log> -- <job>`, then `agent-wait --pid <pid> --log <log>` until it stops returning 124.
