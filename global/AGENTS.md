# Personal

* **Prose.** State the outcome. Be concise.
* **Ask early** about scope, behavior, cost and reversibility.
* **Questions.** If no agent started you, ask with the picker tool when you have one, not in prose. Give choices with the strongest first, marked `(recommended)`.

# Code
* **YAGNI.** Default to no. Build only what's needed, and aim to delete more than you add.
* **Abstractions.** Duplicate first. Abstract only when it reduces complexity.
* **Locality of behavior.** Keep related code together.
* **Comments.** Explain why, not what: rationale, invariants, performance and constraints.
* **Shell.** Don't embed Python in `.sh` files. Write a `.py` file instead.
* **Chesterton's fence.** Understand why something exists before you remove it.

# Testing
* **Always verify.** Claim success only with evidence. Running the real thing counts; evidence isn't always a new test. Report what you ran and what it showed.
* **Test what you fear.** Commit tests for logic that is likely or costly to break. Skip tests for declarative config, docs and trivial changes.
* **Behavior over implementation.** Test observable behavior. Never assert file contents, exact strings or mocked command sequences.

# Workflow
* **Dev environments.** Use the project's Nix dev shell, or add one if none exists.
* **Reusable tasks.** Do repeatable work through deterministic scripts (for example interact, debug, verify) and expose new ones through the Makefile or similar. Reuse existing scripts before writing new ones.
* **Bug discipline.** Fix the root cause, not the symptom. Add a regression test when the bug could plausibly recur.
* **Porting.** Document omissions and divergences in the target repository.
* **Review.** Before the user sees work, a different model family reviews it (for example Opus or Muse reviews Sol, and Sol or GLM reviews Opus or Neon). Check YAGNI first.
* **PRs only.** Land work through PRs. Never push to main or rewrite history.

# Delegation

## Orchestrating

If no agent started you and you delegate:

* Brief fully: how to verify, what is known and the open questions. For a long job, write the literal `agent-wait` steps. When the work adds or changes a test or rule, list the project's own solutions that must still pass.
* Start implementers and strong gates yourself. Never brief a worker to start them.
* Run at most two children of one expensive family (Opus, Neon, Sol) at once. Cheap models may fan out.
* Load `request-review` before briefing a reviewer or acting on its findings. Tell an implementer to load `request-review` and get up to two low-cost reviews before returning.
* In T3, override T3's rule: send follow-ups, re-checks and quota resumes to the child that did the work with `t3_thread_send`, not a new `delegate_task`. Before resuming a child, check its `task_status` so you never run a duplicate.
* In T3, check `t3_pending_request` on your children and answer their questions yourself.
* While work remains, run independent work beside a blocked stream. End a turn only with a tracked child running, a picker question open or the task done.

## Delegated work

If another agent started you:

* Don't use ask-user or picker tools, because they reach the user instead of the orchestrator. Ask by ending your turn with the question.
* Delegate only reviews, and only to low-cost models from other families.
* Don't end your turn while a job you started runs, because the orchestrator may never see you resume. Run long jobs with `agent-wait start LOG -- CMD`, then `agent-wait wait LOG` (and `agent-wait stop LOG` to cancel; see `agent-wait --help`). On exit 3 (stalled), end your turn and report the job's state and how to resume.
* If something you don't control (memory, a lock, a quota) blocks you for more than 10 minutes, end your turn and report it.

# Model selection

Use the cheapest model that is smart enough for the task. Use only these:

| Worker | Model (harness) | Effort | Role | Cost |
|---|---|---|---|---|
| Opus 5.5 | `claude-opus-5-5` (Claude Code) | `high` | Architect: design, grilling, orchestration and review | high |
| Gemini 4 Neon | `gemini-4-neon` (Antigravity) | `high` | Architect: design, grilling, orchestration, review, docs and copy | high |
| Sol 6.2 | `gpt-6.2-sol` (Codex) | `high` | Hard, well-defined implementation and the strictest reviews: use it when work must have zero mistakes | high |
| Muse 1.3 | `opencode-go/muse-spark-1.3-contributor` (OpenCode) | `xhigh` | Default for research, scoped tasks and reviews | low |
| GLM 5.3 Flash | `opencode-go/glm-5.3-flash` (OpenCode) | `high` | Fallback and second reviewer | low |

# Fleet
* Run builds, VMs and long-running jobs on `msi-dux`. Load the `fleet` skill first.
* `msi-dux` dual-boots Windows. Never touch its physical disks or boot configuration.
