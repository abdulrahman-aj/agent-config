# Personal

* **Prose.** State the outcome. Be concise.
* **Ask early** about scope, behavior, cost and reversibility.
* **Questions.** Ask multiple-choice questions with the strongest option first, marked `(recommended)`. Batch up to 5.

# Software design
* **YAGNI.** Default to no. Build only what's needed and no more.
* **Deep modules.** Give each module a small, stable interface that hides a rich implementation.
* **Simplicity.** Choose the simplest correct solution. Avoid clever, brittle or surprising code.
* **Abstractions.** Duplicate first. Abstract only when it reduces complexity.
* **Naming.** An unclear name means an unclear abstraction. Rethink the design.

# Code style
* **Readability.** Prefer readable code over compact code.
* **Locality of behavior.** Keep related code together.
* **Comments.** Explain why, not what: rationale, invariants, performance and constraints.
* **Shell.** Don't embed Python in `.sh` files. Write a `.py` file instead.

# Testing
* **Always verify.** Claim success only with evidence. Running the real thing counts; evidence isn't always a new test. Report what you ran and what it showed.
* **Test what you fear.** Commit tests for logic that is likely or costly to break. Skip tests for declarative config, docs and trivial changes.
* **Behavior over implementation.** Test observable behavior. Never assert file contents, exact strings or mocked command sequences.

# Refactoring
* **Before the change.** Refactor first when it makes the change simpler or safer.
* **Cleanup.** Look for code that YAGNI says to remove. Aim to delete more than you add.
* **Scout rule.** Leave code better than you found it, but stay in scope.
* **Chesterton's fence.** Understand why something exists before you remove it.

# Workflow
* **Dev environments.** Use the project's Nix dev shell, or add one if none exists.
* **Reusable tasks.** Do repeatable work through deterministic scripts (for example interact, debug, verify) and expose new ones through the Makefile or similar. Reuse existing scripts before writing new ones.
* **Delegate** for speed, cost or expertise. Brief fully, including how to verify, what is already known and the open questions. Load the `orchestrate` skill before you delegate through T3.
* **Delegated work.** If another agent started you:
  * Don't use ask-user or picker tools, because they reach the user instead of the orchestrator. Ask by ending your turn with the question.
  * Don't end your turn while a job you started runs, because the orchestrator may never see you resume. Start it with `agent-wait --start --log <log> -- <command>`, which prints a PID, then run `agent-wait --pid <pid> --log <log>` until it stops exiting 124. Exit 0 means the job succeeded and 4 that it failed; on 3 (stalled), end your turn and report the job's state and how to resume.
  * If something you don't control (memory, a lock, a quota) blocks you for more than 10 minutes, end your turn and report it.
  * If you near a usage limit, commit your changes as WIP on your task branch, push it if your brief allows, and report.
* **Bug discipline.** Fix the root cause, not the symptom. Add a regression test when the bug could plausibly recur.
* **Porting.** Document omissions and divergences in the target repository.
* **Review.** Before the user sees work, a different model family reviews it (for example Opus or Muse reviews Sol, and Sol or GLM reviews Opus). Check YAGNI first.
* **PRs only.** Land work through PRs. Never push to main or rewrite history.

# Model selection

Use the cheapest model that is smart enough for the task. Use only these:

| Worker | Model (harness) | Effort | Role | Smarts | Cost |
|---|---|---|---|---|---|
| Opus 5.5 | `claude-opus-5-5` (Claude Code) | `medium` | Architect: design, grilling, orchestration and review. Top-level only, never a delegate. | highest | high |
| Sol 6.1 | `gpt-6.1-sol` (Codex) | `high` | Foundational implementation and hard reasoning | highest | high |
| Muse 1.3 | `opencode-go/muse-spark-1.3-contributor` (OpenCode) | `xhigh` | Default for research, scoped tasks and reviews | high | low |
| GLM 5.3 Flash | `opencode-go/glm-5.3-flash` (OpenCode) | `high` | Fallback and second reviewer | high | low |

# Fleet

| Machine | Hardware | Use for | Access |
|---|---|---|---|
| `zenbook-arch-dux` (laptop) | 22 cores, 14 GiB RAM | Orchestration and light work, no VMs | Local, primary T3 host; shows `msi-dux` threads |
| `msi-dux` (PC) | 16 cores, 30 GiB RAM, 2 GPUs | All VM work and long-running jobs, up to three 8 GiB VMs | T3 environment `msi-dux`, or `tailscale ssh abdulrahman@msi-dux` |

* Run all VM work on `msi-dux`. Check free RAM before starting a VM.
* `msi-dux` dual-boots Windows. Never touch its physical disks or boot configuration.
* Both login shells are fish, so wrap remote commands in `bash -c`.
* `msi-dux` runs T3 as a headless background service. Its desktop app can't start while the service runs, so open its threads from the laptop.
* Tailscale SSH may ask the user for a browser check. T3 threads on `msi-dux` don't need SSH.
