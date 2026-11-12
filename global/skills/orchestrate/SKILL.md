---
name: orchestrate
description: Rules for running T3 workers as delegate_task children. Load before you delegate.
---

# Orchestrate

* **Children, not threads.** Start workers with `delegate_task`. Use `t3_thread_launch` only when the user asks for a new thread. Schedule wakes only for waits T3 can't see, such as a quota reset or CI.
* **Keep work moving.** While work remains, run independent work beside a blocked stream. End a turn only with a tracked child running, a picker question open, or the task done.
* **Ask with the picker.** Ask the user with the picker, not in prose.
* **OpenCode children.** Always set `providerInstanceId: "opencode"`. Without it, T3 silently runs the task on another provider.
* **Context.** Children do the bulk reading and report summaries. Keep your own context for decisions.
* **Worker questions.** Check `t3_pending_request` on your children and answer their questions yourself.
* **Waits in briefs.** When a brief includes a long job, write the wait as literal steps: `agent-wait --start --log <log> -- <job>`, then `agent-wait --pid <pid> --log <log>` until it stops returning 124.
* **Ready to build.** Brief an implementation only when its design has no open technical question. Answer each question first with a cheap research child (citing `file:line` from what it read) or a short spike.
* **Size.** State the expected diff size in lines. When the worker reports, run `git diff --shortstat <base>...<head>`; send anything over twice the estimate back to trim before review.
* **Blind reviews.** Give the reviewer the task statement and the diff, never your findings. It lists what the task didn't ask for or could be simpler, then defects with a `file:line` or a failing command, then what it dismissed. Fix by removing code where you can; after two rounds, decide yourself.
