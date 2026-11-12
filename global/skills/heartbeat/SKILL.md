---
name: heartbeat
description: Keep an orchestrator thread working while the user is away with a 55-minute heartbeat. The user triggers it once per thread.
disable-model-invocation: true
---

# Heartbeat

The heartbeat keeps work moving while the user is away, so the thread never stalls waiting on them while
something could progress.

* **Start.** Schedule a recurring wake for this thread every 55 minutes (T3 `schedule_task`). Its prompt lists
  this thread's check-in duties: check children and answer their pending questions, act on finished work
  (review, merge where authorized, start follow-ups that are now unblocked), and update the user's list of
  what waits on them. Copy the Stop and Restart rules below into that prompt too, so they survive compaction.
  If this thread already has a heartbeat, update it instead of adding a second one.
* **Why 55 minutes.** Claude Code's prompt cache lives 1 hour and each hit restarts it, so a wake every 55
  minutes also keeps the cache warm. Don't use 60: a wake that fires late misses it.
* **Stop.** When nothing can move without the user (no children, no running jobs, no unblocked queued work),
  tell the user and delete the schedule.
* **Restart.** Schedule it again when the next child or job starts, or when the user returns. If these
  instructions are no longer in context, ask the user to run `/heartbeat` again.
