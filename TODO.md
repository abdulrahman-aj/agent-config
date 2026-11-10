# TODO

## Orchestration annoyances (from arch-niri-dux, 2026-11-06)

Each item: what went wrong, evidence (thread, task and schedule ids), and the proposed rule
or fix. Most belong in `global/AGENTS.md` ("Workflow" → delegation) or in a new orchestration
skill; a few are T3 issues to report upstream.

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

### Open
- [ ] **Parallel workers filled the build box's disk.**
  **In progress: arch-niri-dux `make gc` plus a 30 GiB free-disk guard before builds and VMs.** Evidence: by ~05:30 UTC on 2026-11-07 msi-dux had 670 MiB free
  (229 GB disk); per-worker BUILD_STATEs (7–39 GB each), verification disks and temporary worktrees from already-merged
  PRs were never cleaned. Two workers' VM checks failed or stalled (PR #71 ISO build stalled 2h43m; PR #73 and PR #70
  Windows provisioning refused). The architect cleaned merged-PR artifacts: 19 → 99 GB free. Fix: briefs require each
  worker to delete its own BUILD_STATE, VM disks and temporary worktree when done (keeping named fixtures); project
  tooling checks free disk before builds and VMs (like vm.py's RAM gate) and fails fast; the heartbeat checks `df` on the
  build box.

### Closed
- [x] **The architect idles or asks in prose instead of with the picker.**
  **Closed as prose only, because the user prefers the prose rule (global "Questions", orchestrate skill "Ask with the picker") over ~200 lines of hook. A Stop hook was built in the `structural-guards` PR and cut at the user's review.**
  Evidence: architect thread `mcp:launch:e71e088f…`, ~20:20 UTC: it ended a turn with "should I stop
  it?" in prose and left everything waiting on Sol's quota reset; the user replied "Pausing is
  annoying." Fix (rule for top-level orchestrators): ask with the picker in the same turn; before
  ending a turn, make sure something is in flight or a picker question is open; look for parallel
  work around a blocked stream.
- [x] **Workers asked the user directly through pickers.**
  **Closed as prose only, because the cause was top-level `t3_thread_launch` workers; proper `delegate_task` launches removed it. The prose rule in global AGENTS.md stays. A PreToolUse hook was built in the `structural-guards` PR and cut at the user's review.**
  Evidence: a Sol worker of the first architect used Codex `request_user_input` twice (see memory
  `workers-ask-architect` in `~/.claude/projects/-home-abdulrahman-Work-arch-niri-dux/memory/`; the
  thread ids are in `HANDOFF.md`). Partly fixed in agent-config #7 (no worker pickers). Remaining: put
  it in every brief template, and have orchestrators check `t3_pending_request` on their children.
- [x] **Wait loops can't tell a hung job from a slow one.**
  **Closed: `agent-wait --pid` reports a stall (exit 3) when the log stops changing; project side, downloads got timeouts and retries (arch-niri-dux #66).**
  Evidence: the formatter worker (msi-dux thread `mcp:launch:316fb085f76ddb1f6d0568a364ceb8f094bf96c7a68777616a15a6640c43efc4`)
  waited ~45 min on an ISO build whose builder VM had stalled on a download with no timeout
  (`~/.cache/arch-niri-dux-build-formatters/guest-build.log` last written 02:36 local, VM at ~3% CPU). The
  user noticed before any agent did. The architect killed and restarted the build at ~03:23. Its loop also
  used the self-matching `pgrep -f` pattern. Fix (rule for workers): when waiting, also check progress, for
  example the log's mtime or size, and report if nothing changes for N minutes (say 15) rather than waiting
  to a timeout. Fix (projects): network fetches in build tooling need timeouts and retries.
- [x] **Per-worker build folders re-download large inputs.**
  **Closed: arch-niri-dux #75 keeps hash-verified downloads in one shared cache.**
  Evidence: arch-niri-dux briefs give each worker a private `BUILD_STATE` to avoid the shared build lock.
  The formatter worker (msi-dux thread `mcp:launch:316fb085f76ddb1f6d0568a364ceb8f094bf96c7a68777616a15a6640c43efc4`)
  spent ~36 min (02:00–02:36 local, 2026-11-07) downloading the 1.6 GB `archlinux-2026.10.01` ISO already
  present byte-identical in `~/.cache/arch-niri-dux-build-pr59/` and `…-migration-core/`. Fix: in project
  build tooling, keep hash-verified downloads in one shared cache separate from per-build state (queued in
  arch-niri-dux as part of audit PR 5). Rule for briefs: when isolating build state per worker, check that
  immutable inputs are shared, or seed them by hardlink.
- [x] **Branches in the deployed checkout are live.**
  **Closed as prose only, because the user prefers live links into `~/agent-config` (as with ~/dotfiles): edit in a git worktree when a change shouldn't go live yet (agent-config README and AGENTS.md). A pinned-main deploy was built in the `structural-guards` PR and dropped at the user's review.** Deployed skills and AGENTS.md are symlinks into
  `~/agent-config`'s working tree, so checking out a branch there (as the architect and the PR #9 Opus did,
  2026-11-07) changes every running agent's instructions before review or merge. Evidence: switching to
  `unslop-model-invocation` immediately changed the live `unslop` skill description in the architect's
  session. Fix: edit agent-config in a separate worktree (for example `git worktree add ../agent-config-wt
  <branch>`) and keep `~/agent-config` on `main`; or deploy from a separate clone.
- [x] **Workers run heavy jobs on the wrong machine.**
  **Closed: the laptop sets `AGENT_HEAVY_JOBS=deny` through `~/.config/environment.d` (`hosts/zenbook-dux/`, agent-config `structural-guards` PR) and arch-niri-dux's heavy targets refuse while it's set (in flight there).** Evidence: the audit PR 5 worker (Opus, thread
  `thread:delegated-task:command%3Amcp%3A65c94a32-fabf-4c0e-92d7-1df8d6d03b9d%3Adelegate-task%3Ab3499ef1-18dc-47d7-ae41-5a5b02c53bb0`)
  ran `build-fetch-bootstrap` (1.6 GB) on the laptop at ~02:35 UTC on 2026-11-07, although the brief said to verify on
  msi-dux; the architect noticed only because the user asked. Fix candidates: a machine guard in project build entry
  points (refuse heavy targets when the host isn't the build box, unless overridden), or a fleet rule in global
  AGENTS.md ("heavy jobs: msi-dux only") that briefs inherit, plus the heartbeat's laptop check.
- [x] **Tailscale SSH check mode cuts agents off at night.**
  **Closed: the tailnet policy changed to `accept` on 2026-11-07; `tailscale ssh abdulrahman@msi-dux` ran without a check throughout the structural-guards work.** Evidence: from ~05:50 UTC on 2026-11-07, `tailscale ssh
  abdulrahman@msi-dux` hung printing "Tailscale SSH requires an additional check. To authenticate, visit:
  https://login.tailscale.com/a/…" while the user slept; workers' VM steps over SSH would have stalled. Workaround used:
  nested `delegate_task` runners on the T3 msi-dux environment (no SSH). Fix: a tailnet policy `accept` (or a long
  checkPeriod) for the agent laptop → build box, and briefs that prefer T3 remote runners for build-box steps.
- [x] **Command-runner children burn the strong model's quota.**
  **Closed as prose only: run commands on msi-dux directly with `tailscale ssh abdulrahman@msi-dux "bash -lc '<cmd>'"` (global fleet section) instead of a runner child. A `fleet-run` wrapper was cut as YAGNI at the user's review.** Evidence: the hand-fix rehearsal worker (Opus, thread
  `thread:delegated-task:command%3Amcp%3Af6a3651a-3497-4778-a994-ea5e0113659e%3Adelegate-task%3A0f62c0d9-412c-4407-a1f0-508840aa6104`)
  picked Sol as a T3 msi-dux command runner on 2026-11-07; Codex hit its limit at 10:52 UTC (reset 12:29), stalling the
  real Sol work on PR #73. Fix: briefs name the runner model explicitly (cheap: Muse/GLM) and forbid strong models for
  pure command-running; consider a rule in the orchestrate skill.

### Closed as prose only
- [x] **Workers end their turn while a background job runs.**
  **Closed as prose only, because the orchestrator catches a worker (or reviewer) that ends early from T3's completion notice; the agent-wait rule in global AGENTS.md stays. A Stop-hook job guard was built in the `structural-guards` PR and cut as YAGNI at the user's review.**
  Evidence: the same Muse thread `mcp:launch:4ff05808…` (msi-dux), run 1: it started
  `make iso-development` in the background and ended with "will proceed to make verify once it
  completes"; nothing would resume it. The build log is in msi-dux
  `~/.cache/arch-niri-dux-build-pr59/`. Fix (rule for delegated work): don't end your turn while a
  job runs; block in the foreground with bounded wait loops (`timeout 540 bash -c 'while pgrep …;
  do sleep 30; done'`) until done, or report a real blocker.
  Repeat: Muse ended its turn mid-build again even though the brief said in bold not to (task
  `…%3Aremote-delegate%3A7d8da349-a79f-4228-b7c6-fae5b0c9cbf9`, msi-dux thread
  `mcp:launch:5040cf274b53a5b3c34d2d0686f18744b0fd4070e65dda83210f81ab4811fea8`, ~21:45 UTC, "Waiting on the
  ISO build to complete before proceeding"). The architect re-dispatched to GLM 5.3 Flash with a literal
  wait command as step 1 (task `…%3Aremote-delegate%3A3876f686-f006-40d1-a62d-9bd43f5778f2`, thread
  `mcp:launch:4ef6c77f78a12463272183712cff1e191734b6dce486dbdfe20bad16c79455c2`). Prose rules aren't enough
  for Muse under OpenCode: give it a copy-paste wait command, compare models on this behavior, or give
  workers a wait helper script (a `make wait-*` target or a T3 background-wait primitive for children).
- [x] **Top-level worker threads don't wake the orchestrator.**
  **Prose only, because workers are only started with `delegate_task` (orchestrate skill), whose children do wake the orchestrator.**
  Evidence: the legacy Sol #58 thread `mcp:launch:5f6773a8…` needed a bound wake
  (`scheduled-task:a6d47117-317a-49ed-9b27-ec233cdb4e84`, 21:35 UTC) to resume it after its quota
  reset; the first architect also ran a 15-minute check-in schedule (see `HANDOFF.md` item 6). Fix
  (rule): workers are `delegate_task` children; scheduled wakes only for external waits (a quota
  reset, CI).
- [x] **A quota cut-off mid-work risks losing it.**
  **Prose only, because T3 auto-resumes limited threads (`autoResumeLimitedThreads: true`); the WIP-commit rule was dropped by the user.**
  Evidence: Sol thread `mcp:launch:f46d56e3…` (msi-dux) hit its usage limit during the migration
  core; the work survived only as WIP commit `671c5c7` on branch `migration-core`, pushed. Fix (rule
  for workers): if you approach or hit a limit, commit WIP and push the branch, then report.

### Open question
The user understands T3's sidebar philosophy (from Theo) as "a thread rises to the top only when it
needs input; otherwise it sits in Working". Observed behavior matches when children are tracked (see
the first item). Confirm with T3 docs or Theo before encoding it as a rule.

## T3 bugs (local workaround list; upstream drafts in `t3-issue-drafts.md`)

Each stays here until T3 fixes it; the workaround is the rule to follow meanwhile.

- [ ] **Continuing a finished child with `t3_thread_send` detaches it.**
  **Workaround: resume with a fresh `delegate_task` brief, `task_cancel` the old run first.**
  Evidence: the PR #59 Muse verifier (task `…%3Aremote-delegate%3A94e267bc-646a-4b08-9433-97cc57d43b63`,
  msi-dux thread `mcp:launch:4ff05808b4970a2fdd012e33ac5d51853665825f6a7482d8d9b3b38d8d6dadc1`)
  ended its turn early. The architect resent it with `t3_thread_send` (run ordinal 2, ~20:27 UTC).
  `task_status` on that task then showed `status: completed`, `hasPendingChildRuns: false` while run 2
  was active, so nothing would wake the architect, and the architect thread dropped out of the
  sidebar's "Working" section. It was replaced by tracked task
  `…%3Aremote-delegate%3A6c64ff09-c6fb-4742-8d8f-de1e1aba820b` (msi-dux thread
  `mcp:launch:af9cf55149cdebbbd91e8a129f401cc695bea069cf53c7ba410b753c997fb1ac`). A fallback schedule
  `scheduled-task:737219ce-2f3d-4867-8d75-f539efbdc7ca` had been added and was then deleted.
  Fix (rule): a stalled child gets a fresh `delegate_task` with a resume brief (state on disk, what's
  done, what's left). Stop the old run first, at a moment when no foreground job would die.
- [ ] **An orchestrator outside its project can't delegate.**
  **Workaround: the orchestrator lives in the project it orchestrates and starts children from there.**
  Evidence: the first architect lived in "No project" (project `779106d8-35e8-4c31-836a-81e740385e0a`,
  laptop). `delegate_task` refused ("A local task runs in this thread's project"), so it fell back to
  `t3_thread_launch`: workers such as Sol #58 `mcp:launch:5f6773a8b0924406311ace197cec86c46281e63d5295a99534e15ac4117322f2`
  (laptop), Sol migration core `mcp:launch:f46d56e394675f4b03b4a9e4b97f35a15253822ac7b039eca00db1888ad93656`
  and Muse #59 verify `mcp:launch:dd8dce8466de2ae91b0f468ded5cde09f25229012971b6a6e99a35e06d7b394a` (both
  msi-dux) were top-level, never woke the architect, and the msi-dux ones were invisible in the app. Fix
  (rule): the orchestrator lives in the project it orchestrates; if it doesn't, it says so and moves
  before launching anything. Use `t3_thread_launch` only when the user asks for a new thread.
- [ ] **Children on a linked environment can't use worktree isolation.**
  **Workaround: one writer per remote checkout, or point each child at its own existing worktree.**
  Evidence: architect thread `mcp:launch:e71e088f…`, ~20:03 UTC: `delegate_task` with
  `isolation: "worktree"` and `target.environmentId: c2da85ac-…` failed with "A task in a linked
  environment runs in that project's checkout; isolation \"worktree\" is not supported there." The
  retry without isolation (thread `mcp:launch:e6bba7a2eb33ec9512a7022560b967664ae33485def1fac3dc79f8bf30ad440d`)
  ran in msi-dux `~/Work/arch-niri-dux`. Fix: in the fleet section, say to serialize writers per
  remote checkout, or point each child at its own existing worktree (as the #59 and migration-core
  briefs do) or at a second registered clone. T3 upstream: support worktree isolation for remote
  delegates.
- [ ] **Remote children linger in the remote sidebar.**
  **Workaround: settle finished remote children with `t3_thread_organize settle` and their `environmentId`.**
  Evidence: "Test child: msi-dux" `mcp:launch:e6bba7a2…` showed inline in the architect's chat but
  was recorded on msi-dux with `parentThreadId: null`, `relationshipToParent: null`, in project
  `mcp:4545a593…`. Compare the local test child
  `thread:delegated-task:command%3Amcp%3Af2ada484-d25d-45e3-84e0-5b1bbe144d13%3Adelegate-task%3A41dc812b-17c0-472e-b90b-5449f0d91e12`.
  Fix (rule): settle finished msi-dux children with `t3_thread_organize settle` plus their
  `environmentId`. T3 upstream: record the parent link for remote delegates.
- [ ] **MCP-registered projects don't show in the app.**
  **Workaround: register projects that need a sidebar presence from the app.**
  Evidence: msi-dux project `mcp:4545a593…` (created over MCP) never appeared in the laptop sidebar;
  the app-created `7116a3e2…` (agent-config) did. A probe `t3_project_create` on msi-dux also returned
  an `mcp:` id (`mcp:d7370cc1-f071-4e58-8b53-ae2369f24830`, since deleted). Children still show inline,
  so this only hurts top-level threads. T3 upstream: report it; meanwhile register projects that need
  a sidebar presence from the app.
- [ ] **Superseded workers can auto-resume from queued background notices.**
  **Workaround: `t3_queue list` on the old thread and cancel stale items before replacing a worker.**
  Evidence: the legacy Sol #58 thread `mcp:launch:5f6773a8b0924406311ace197cec86c46281e63d5295a99534e15ac4117322f2`
  (laptop) had queued run ordinal 9 since 18:39:57 UTC: "Background command completed (exit 143):
  make verify … --directory out/verify-boot-policy-fresh …". On Sol's quota reset it could have started
  by itself in `~/.t3/worktrees/arch-niri-dux/package-owned-policy`, colliding with the replacement Sol
  child planned for 21:35 UTC. The architect found it at ~21:05 UTC with `t3_thread_list` (statuses
  queued/running) plus `t3_queue list`, then cancelled it and settled the thread. Fix (rule): before
  replacing or handing off a worker, check `t3_queue list` on its thread (with `environmentId`) and
  cancel the stale items; archiving or settling alone doesn't clear the queue. T3 upstream: drop queued
  background-completion notices when a thread is settled or archived.
- [ ] **OpenCode sessions keep working after T3 marks the turn complete.**
  **Workaround: before re-dispatching an OpenCode child, check `~/.local/share/opencode/log/opencode.log` or `pgrep -af` for activity after the run ended.**
  Evidence: Muse task `…%3Aremote-delegate%3A7d8da349-a79f-4228-b7c6-fae5b0c9cbf9` (msi-dux thread
  `mcp:launch:5040cf274b53a5b3c34d2d0686f18744b0fd4070e65dda83210f81ab4811fea8`) shows one run, completed
  21:46:28 UTC. But msi-dux `~/.local/share/opencode/log/opencode.log` (server run `77a7cd6d`) shows the
  same OpenCode server spawning that worker's tool calls from 21:50:42 (`make verify … verify-pr59-rebased`)
  through the commit `1649950` and push at ~22:06 UTC: OpenCode re-woke the model when its background job
  finished, which T3 never saw. The architect, believing the worker had stalled, dispatched GLM
  (`mcp:launch:4ef6c77f78a12463272183712cff1e191734b6dce486dbdfe20bad16c79455c2`), which then duplicated the
  ISO verification (`out/verify-pr59-final*`) in parallel on the same worktree; at least one extra VM run
  was wasted. Same pattern earlier: a verify-fast at 23:57 local after the architect interrupted thread
  `mcp:launch:4ff05808…`. So "Muse ends its turn mid-build" (the item above) is really T3 losing track
  of OpenCode's background-job continuation. Fix: T3 upstream: track OpenCode background-task wakes as
  part of the child run. Meanwhile (rule): before re-dispatching a "stalled" OpenCode child, check the
  OpenCode log (or `pgrep -af` for its jobs) for activity after the run's completion time, and tell
  OpenCode children to run long jobs in the foreground rather than as OpenCode background tasks.
- [ ] **SSH remotes break T3 worktree fetches.**
  **Workaround: clone over HTTPS (`gh auth setup-git`).**
  Evidence: the laptop clone `~/Work/arch-niri-dux` had an SSH origin that failed to fetch under T3;
  worktrees had to start from a stale ref (`baseRef: origin/main, startFromOrigin: false`) until
  `gh auth setup-git` switched it to HTTPS (`HANDOFF.md` "Setup already done"). Fix: clone over HTTPS
  (`gh auth setup-git`) in the README install step and for project clones.
- [ ] **Merged PRs settle the orchestrator's thread.**
  **Workaround: right after merging a watched PR, unwatch and unlink it.** `watch_pull_request` links the PR to the watching thread,
  and T3 "settles the thread on merge". The architect thread
  (`mcp:launch:e71e088f02a79c4d810218b748a1f136732f80d9baf494aae69429efcc315a68`) had 10 merged PRs linked
  (arch-niri-dux #58, #61–#68 via watches; agent-config #10 auto-linked as "created") and got settled after the
  #10 merge on 2026-11-07 (~02:05 UTC), so it dropped out of the user's view while work was in flight. Fix (rule
  for orchestrators): right after merging a watched PR, `unwatch` and `unlink` it (or `unlink_pull_requests
  states=[merged]`). T3 upstream: don't auto-settle a thread that has running children or other open work.

## Held back from PR #9 (T3 workarounds; revisit when T3 changes)

Removed from `global/skills/orchestrate/SKILL.md` before review, copied verbatim. Each note names the T3 change that would make it obsolete.

* **Home project.** Run from the project you orchestrate. `delegate_task` starts local children only in your thread's project, so if you're elsewhere, move before you start anything. For another repo, start the child from your project and point it at that repo's checkout.
  - Obsolete when a local `delegate_task` can start a child in another registered project.
* **Remote checkouts.** A child on a linked environment runs in that project's checkout, and worktree isolation fails there. Run one writer per remote checkout, or point each child at its own existing worktree.
  - Obsolete when `delegate_task` supports worktree isolation on linked environments.
* **Confirm the stall.** OpenCode resumes its model when a background job ends, even after T3 marked the run complete. Before you re-dispatch an OpenCode child, look for activity after that time in `~/.local/share/opencode/log/opencode.log` or with `pgrep -af`.
  - Obsolete when T3 tracks OpenCode's background-job continuations as part of the child run.
* **Resume with a new delegate.** Never continue a child with `t3_thread_send`. That run is untracked: nothing wakes you, and your thread leaves Working. Stop the old run with `task_cancel` when no foreground job would die, then `delegate_task` a resume brief that says what's on disk, what's done and what's left.
  - Obsolete when a `t3_thread_send` continuation stays tracked (wakes the parent, keeps it in Working).
* **Clear queues.** Before you replace or hand off a worker, run `t3_queue list` on its thread (with `environmentId` if remote) and cancel stale items. Settling or archiving leaves the queue intact, and a queued background notice can restart the old worker.
  - Obsolete when T3 drops queued background notices on settle or archive.
* **Settle remote children.** T3 doesn't record the parent of a remote child, so settle finished ones with `t3_thread_organize settle` and their `environmentId`.
  - Obsolete when T3 records the parent link for remote delegates.
* **Usage limits.** If you near a usage limit, commit your changes as WIP on your task branch, push it if your brief allows, and report.
  - Dropped by the user, not a T3 workaround: models can't reliably tell they're near a limit, and the rule made them worry about usage.
* Sentences removed from kept bullets:
  * "Children, not threads": "Only children wake you when they finish and show up in your chat."
    - Obsolete when top-level threads can wake the thread that launched them.
  * "Waits in briefs": "OpenCode may run long jobs as background tasks T3 can't see (see "Confirm the stall")."
    - Obsolete with "Confirm the stall" above.

## Rule → enforcement

What enforces each orchestration rule. "Prose only" rows say why nothing stronger fits.

| Rule (location) | Enforced by |
|---|---|
| No ask-user or picker tools in delegated work (global) | Prose only, because proper `delegate_task` launches removed the cause (top-level-launched workers). |
| Wait for your own jobs; report a stall (global) | `agent-wait` exit codes 0, 3, 4, 124 (`tests/test-agent-wait.py`). Ending early anyway: prose only, because the orchestrator catches it from T3's completion notice. |
| Stop a job by its process group (global) | Prose only, because `agent-wait --help` documents it and a wrong kill shows up as exit 4. |
| Report a blocker after 10 minutes (global) | Prose only, because blockers (memory, locks, quotas) share no signal a script could watch. |
| Ask with the picker (global "Questions", orchestrate skill) | Prose only, because the user prefers the rule over ~200 lines of hook. |
| Heavy jobs on `msi-dux` (global fleet) | `AGENT_HEAVY_JOBS=deny` on the laptop (`hosts/zenbook-dux/`) plus each repo's heavy-target guard. |
| Commands on `msi-dux` over `tailscale ssh … "bash -lc '…'"`, no runner children (global fleet) | Prose only; a wrapper script was cut as YAGNI. |
| Edit agent-config in a worktree when a change shouldn't go live yet (README, AGENTS.md) | Prose only, because the user wants live links into `~/agent-config`, as with ~/dotfiles. |
| Children, not threads (skill) | Prose only, because T3 has no hook to refuse `t3_thread_launch`. |
| Keep work moving (skill) | Prose only, because no hook can see whether work is in flight. |
| Answer worker questions (skill) | Prose only (`t3_pending_request` to check). |
| Waits in briefs (skill) | `agent-wait`, given as literal commands in the brief. |
| T3 workarounds (above) | Prose only, local; obsolete once T3 changes. |

- [ ] **A T3 or session restart kills agents' background jobs.** Evidence: 2026-11-07 ~16:29 UTC (19:29 local) the
  architect's laptop `make iso-development && make verify` (started via `agent-wait --start`, PID 1347852) died:
  `qemu-system-x86_64: terminating on signal 15 from pid 1795 (/usr/lib/systemd/systemd)` when the session restarted.
  agent-wait's setsid doesn't leave the T3 process cgroup, so systemd stops the job with the scope. Workaround used:
  `systemd-run --user --unit=<name> --collect -p WorkingDirectory=… bash -c '…'` (output in `journalctl --user -u`).
  Idea: agent-wait --start could launch through `systemd-run --user --scope` when available. Not started (fixed end point).

- [ ] **Workers end their turn while a review (or other non-agent-wait work) is still running.** Evidence: 2026-11-07
  ~18:40 UTC the ISO-signing Sol worker (thread:delegated-task:command%3Amcp%3A5a4d74fa-76ab-452b-a271-29517fc4479d%3Adelegate-task%3Abb397675-f521-4fd3-970c-2c3dd0fbd40a)
  reported "Muse review is running. I'll address findings … when it finishes" and ended its turn; T3 showed no pending
  child, so nothing would wake it. #11's job guard only covers agent-wait jobs. Not started (fixed end point).
