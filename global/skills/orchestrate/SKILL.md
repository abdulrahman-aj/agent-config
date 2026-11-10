---
name: orchestrate
description: Rules for running T3 workers as delegate_task children. Load before you delegate.
---

# Orchestrate

* **Children, not threads.** Start workers with `delegate_task`. Use `t3_thread_launch` only when the user asks for a new thread. Schedule wakes only for waits T3 can't see, such as a quota reset or CI.
* **Keep work moving.** While work remains, run independent work beside a blocked stream. End a turn only with a tracked child running, a picker question open, or the task done.
* **Ask with the picker.** Ask the user with the picker, not in prose.
* **Worker questions.** Check `t3_pending_request` on your children and answer their questions yourself.
* **Waits in briefs.** When a brief includes a long job, write the wait as literal steps: `agent-wait --start --log <log> -- <job>`, then `agent-wait --pid <pid> --log <log>` until it stops returning 124.
* **Ready to build.** Brief an implementation only when its design has no open technical question. Answer each question first with a cheap research child (citing `file:line` from what it read) or a short spike.
* **Size.** State the expected diff size in lines. The worker stops and reports back at twice that.
* **Blind reviews.** Give the reviewer the task statement and the diff, never your findings. It answers in this order: what to delete or simplify, then defects, then dismissed. Prefer fixing a finding by removing code. After two fix rounds, stop reviewing and decide yourself whether it ships.
