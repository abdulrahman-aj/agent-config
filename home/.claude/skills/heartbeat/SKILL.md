---
name: heartbeat
description: Keep a long-lived Claude Code orchestrator thread's prompt cache warm with a 55-minute heartbeat. The user triggers it once per thread.
disable-model-invocation: true
---

# Heartbeat

Claude Code's prompt cache lives 1 hour, and each request that hits it restarts the clock. After a longer gap the
next turn rewrites the whole context at 2x the input price.

* **Start.** Schedule a recurring wake for this thread every 55 minutes (T3 `schedule_task`). Its prompt lists
  this thread's check-in duties: check children and their pending questions, act on finished work, update the
  user's list. If this thread already has a heartbeat, update it instead of adding a second one. Never use
  60 minutes: a wake that fires late misses the cache.
* **Stop.** When the user signs off and no child or job is in flight, delete the schedule. A thread left idle
  pays one full rewrite on return, which the context cap bounds.
* **Restart.** Schedule it again when the next child or job starts, or when the user returns.
