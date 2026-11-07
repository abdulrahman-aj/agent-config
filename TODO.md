# TODO

## Orchestration annoyances (from arch-niri-dux, 2026-11-06)

Each item: what went wrong, evidence (thread, task and schedule ids), and the fix. Rules from
these items now live in `global/AGENTS.md` ("Delegated work") and `global/skills/orchestrate/`.
What's left are T3 issues to report upstream and project fixes.

### How to inspect the evidence
- Threads: `t3_thread_read` with `threadId` (add `environmentId` for msi-dux; `view: "activity"`
  for the full timeline). Delegated tasks: `task_status` with `taskId` (only from the thread
  that started them). Projects: `t3_project_list` / `t3_project_read`. Schedules:
  `list_scheduled_tasks`.
- Environments: laptop = local; msi-dux = `c2da85ac-af47-4a2c-ba03-89ffc13b81a8`.
- Projects: laptop arch-niri-dux `90142cc4-3f3f-474a-ba54-fc6ea11084dd`; msi-dux arch-niri-dux
  `mcp:4545a593-7778-43f6-8d03-ed7f37599884` (created over MCP); msi-dux agent-config
  `7116a3e2-a0f0-4410-a94e-ca5b69f402db` (created in the app).
- Architect (second, in project): `mcp:launch:e71e088f02a79c4d810218b748a1f136732f80d9baf494aae69429efcc315a68`
  (laptop). First architect (in "No project"): handoff and design notes in
  `~/.t3/scratch/2026-11-06-i-started-this-project-recently-43e139bd/` (`HANDOFF.md` lists its
  worker threads).
- Delegated task ids share the prefix
  `node:delegated-task:command%3Amcp%3Af2ada484-d25d-45e3-84e0-5b1bbe144d13%3A`; below they're
  abbreviated as `…%3A<suffix>`.

### Rule enforcement
What enforces each orchestration rule. "Prose only" rows are candidates for a script, lint or T3 feature.

| Rule (location) | Enforced by |
|---|---|
| No ask-user or picker tools in delegated work (global) | Prose only. T3 surfaces child questions as `t3_pending_request`, which helps the orchestrator notice. |
| Wait for your own jobs; report a stall (global) | `agent-wait` (exit codes 0, 3, 124; `tests/test-agent-wait.py`) |
| Report a blocker after 10 minutes (global) | Prose only |
| Commit and push WIP near a usage limit (global) | Prose only |
| Home project (skill) | T3: a local `delegate_task` refuses another project |
| Children, not threads (skill) | Prose only |
| Remote checkouts: one writer each (skill) | T3 refuses worktree isolation remotely; serializing writers is prose only |
| Keep work moving; ask with the picker (skill) | Prose only |
| Answer worker questions (skill) | Prose only (`t3_pending_request` to check) |
| Waits in briefs (skill) | `agent-wait`, given as a literal command in the brief |
| Confirm the stall before re-dispatching OpenCode (skill) | Prose only; candidate script that checks the OpenCode log for activity after a run's end |
| Resume with a new delegate (skill) | Prose only (T3's own orchestration prompt says the same) |
| Clear queues before replacing a worker (skill) | Prose only, until T3 drops queued notices on settle (upstream item below) |
| Settle remote children (skill) | Prose only, until T3 records remote parents (upstream item below) |

### Report to T3 upstream
- [ ] **Children on a linked environment can't use worktree isolation.**
  Evidence: architect thread `mcp:launch:e71e088f…`, ~20:03 UTC: `delegate_task` with
  `isolation: "worktree"` and `target.environmentId: c2da85ac-…` failed with "A task in a linked
  environment runs in that project's checkout; isolation \"worktree\" is not supported there." The
  retry without isolation (thread `mcp:launch:e6bba7a2eb33ec9512a7022560b967664ae33485def1fac3dc79f8bf30ad440d`)
  ran in msi-dux `~/Work/arch-niri-dux`. The workaround (one writer per
  remote checkout, or each child in its own existing worktree) is in the orchestrate skill. T3
  upstream: support worktree isolation for remote delegates.
- [ ] **Remote children linger in the remote sidebar.**
  Evidence: "Test child: msi-dux" `mcp:launch:e6bba7a2…` showed inline in the architect's chat but
  was recorded on msi-dux with `parentThreadId: null`, `relationshipToParent: null`, in project
  `mcp:4545a593…`. Compare the local test child
  `thread:delegated-task:command%3Amcp%3Af2ada484-d25d-45e3-84e0-5b1bbe144d13%3Adelegate-task%3A41dc812b-17c0-472e-b90b-5449f0d91e12`.
  The workaround (settle them with `environmentId`) is in the orchestrate skill. T3 upstream: record the parent link for remote delegates.
- [ ] **MCP-registered projects don't show in the app.**
  Evidence: msi-dux project `mcp:4545a593…` (created over MCP) never appeared in the laptop sidebar;
  the app-created `7116a3e2…` (agent-config) did. A probe `t3_project_create` on msi-dux also returned
  an `mcp:` id (`mcp:d7370cc1-f071-4e58-8b53-ae2369f24830`, since deleted). Children still show inline,
  so this only hurts top-level threads. T3 upstream: report it; meanwhile register projects that need
  a sidebar presence from the app.
- [ ] **Superseded workers can auto-resume from queued background notices.**
  Evidence: the legacy Sol #58 thread `mcp:launch:5f6773a8b0924406311ace197cec86c46281e63d5295a99534e15ac4117322f2`
  (laptop) had queued run ordinal 9 since 18:39:57 UTC: "Background command completed (exit 143):
  make verify … --directory out/verify-boot-policy-fresh …". On Sol's quota reset it could have started
  by itself in `~/.t3/worktrees/arch-niri-dux/package-owned-policy`, colliding with the replacement Sol
  child planned for 21:35 UTC. The architect found it at ~21:05 UTC with `t3_thread_list` (statuses
  queued/running) plus `t3_queue list`, then cancelled it and settled the thread. The workaround
  (clear `t3_queue list` before replacing a worker) is in the orchestrate skill. T3 upstream: drop queued
  background-completion notices when a thread is settled or archived.
- [ ] **OpenCode sessions keep working after T3 marks the turn complete.**
  Evidence: Muse task `…%3Aremote-delegate%3A7d8da349-a79f-4228-b7c6-fae5b0c9cbf9` (msi-dux thread
  `mcp:launch:5040cf274b53a5b3c34d2d0686f18744b0fd4070e65dda83210f81ab4811fea8`) shows one run, completed
  21:46:28 UTC. But msi-dux `~/.local/share/opencode/log/opencode.log` (server run `77a7cd6d`) shows the
  same OpenCode server spawning that worker's tool calls from 21:50:42 (`make verify … verify-pr59-rebased`)
  through the commit `1649950` and push at ~22:06 UTC: OpenCode re-woke the model when its background job
  finished, which T3 never saw. The architect, believing the worker had stalled, dispatched GLM
  (`mcp:launch:4ef6c77f78a12463272183712cff1e191734b6dce486dbdfe20bad16c79455c2`), which then duplicated the
  ISO verification (`out/verify-pr59-final*`) in parallel on the same worktree; at least one extra VM run
  was wasted. Same pattern earlier: a verify-fast at 23:57 local after the architect interrupted thread
  `mcp:launch:4ff05808…`. Muse "ending its turn mid-build" (msi-dux threads `mcp:launch:4ff05808…` run 1 and
  `mcp:launch:5040cf27…` ~21:45 UTC, despite a bold brief rule) is this: T3 loses track of OpenCode's
  background-job continuation. The workarounds (check the OpenCode log before re-dispatching, literal
  wait commands in briefs, workers wait in the foreground) are in the orchestrate skill and
  `global/AGENTS.md`. T3 upstream: track OpenCode background-task wakes as part of the child run.
- [ ] **`delegate_task` can't start a local child in another project.**
  Evidence: architect thread `mcp:launch:e71e088f02a79c4d810218b748a1f136732f80d9baf494aae69429efcc315a68`
  (laptop), 2026-11-07 ~03:00 local: a local `delegate_task` with another project's id failed with "A
  local task runs in this thread's project. Omit target.projectId…". Cross-repo work (this agent-config
  change) runs as a child in the architect's project, pointed at the other repo's checkout. T3 upstream:
  allow a local child in another registered project.

### Project fixes
- [ ] **arch-niri-dux: build downloads have no network timeout.**
  Evidence: the formatter worker (msi-dux thread `mcp:launch:316fb085f76ddb1f6d0568a364ceb8f094bf96c7a68777616a15a6640c43efc4`)
  waited ~45 min on an ISO build whose builder VM had stalled on a download with no timeout
  (`~/.cache/arch-niri-dux-build-formatters/guest-build.log` last written 02:36 local, VM at ~3% CPU). The
  user noticed before any agent did; the architect restarted the build at ~03:23. The worker-side rule
  (check progress, report a stall after 15 minutes) is in `global/AGENTS.md`. Fix: network fetches in the
  build tooling need timeouts and retries.
- [ ] **arch-niri-dux: per-worker build folders re-download large inputs.**
  Evidence: arch-niri-dux briefs give each worker a private `BUILD_STATE` to avoid the shared build lock.
  The formatter worker (msi-dux thread `mcp:launch:316fb085f76ddb1f6d0568a364ceb8f094bf96c7a68777616a15a6640c43efc4`)
  spent ~36 min (02:00–02:36 local, 2026-11-07) downloading the 1.6 GB `archlinux-2026.10.01` ISO already
  present byte-identical in `~/.cache/arch-niri-dux-build-pr59/` and `…-migration-core/`. Fix: in project
  build tooling, keep hash-verified downloads in one shared cache separate from per-build state (queued in
  arch-niri-dux as part of audit PR 5). Rule for briefs: when isolating build state per worker, check that
  immutable inputs are shared, or seed them by hardlink.
- [ ] **agent-config and project clones: SSH remotes break T3 worktree fetches.**
  Evidence: the laptop clone `~/Work/arch-niri-dux` had an SSH origin that failed to fetch under T3;
  worktrees had to start from a stale ref (`baseRef: origin/main, startFromOrigin: false`) until
  `gh auth setup-git` switched it to HTTPS (`HANDOFF.md` "Setup already done"). Fix: clone over HTTPS
  (`gh auth setup-git`) in the README install step and for project clones.

### Open question
The user understands T3's sidebar philosophy (from Theo) as "a thread rises to the top only when it
needs input; otherwise it sits in Working". Observed behavior matches when children are tracked (a child
continued with `t3_thread_send` dropped its parent out of Working). Confirm with T3 docs or Theo before encoding it as a rule.
