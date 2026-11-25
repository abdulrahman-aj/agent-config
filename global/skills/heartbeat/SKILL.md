---
name: heartbeat
description: Keep an orchestrator thread working while the user is away with a 55-minute heartbeat. Use when the user asks for a heartbeat or says they will be away while children or jobs run.
---

# Heartbeat

The heartbeat keeps work moving while the user is away, so the thread never stalls waiting on them while
something could progress.

* **Start.** Schedule a recurring wake for this thread every 55 minutes with T3 `schedule_task`. Its prompt lists
  this thread's check-in duties: verify child liveness, answer pending questions, act on finished work
  (review, merge where authorized, start follow-ups that are now unblocked), and update the user's list of
  what waits on them. Copy the Check liveness, Stop and Restart rules below into that prompt too, so they
  survive compaction. If this thread already has a heartbeat, update it instead of adding a second one.
* **Check liveness.** For every blocked stream, check `task_status` and the child's live thread status
  (`t3_thread_list` or `t3_thread_read`) to confirm whether work is still running. Never assume silence means
  progress. A child can stop mid-job or reach `failed`, `completed` or `result_available` without waking the
  parent. Reading status or results is always safe; act on finished or failed results you find. Send a resume
  or start a replacement only when the child has unfinished work, nothing is active (`preparing`, `starting`,
  `running`, `waiting` or `queued`), and, after a quota failure, the reset wait in `Orchestrating` (`AGENTS.md`)
  has passed.
* **Why 55 minutes.** When the orchestrator runs on Claude Code, a wake every 55 minutes also keeps its
  1-hour prompt cache warm (each hit restarts the hour). Other harnesses' caches are cheap to miss. Don't use
  60: a wake that fires late misses the cache.
* **Stop.** When nothing can move without the user (no children, no running jobs, no unblocked queued work),
  tell the user and delete the schedule.
* **Restart.** Schedule it again when the next child or job starts, or when the user returns. If these
  instructions are no longer in context, load the heartbeat skill again.
