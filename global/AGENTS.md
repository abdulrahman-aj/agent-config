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
* **File locations.** Never put logs, evidence, dumps or scratch files at the top level of `~`. Put logs and evidence under the worktree's `out/`, reusable data under `~/.local/share/<project>/`, caches under `~/.cache/<project>/`, and scratch in `/tmp` or the session scratchpad. Delete scratch when done.
* **Bug discipline.** Fix the root cause, not the symptom. Add a regression test when the bug could plausibly recur.
* **Porting.** Document omissions and divergences in the target repository.
* **Review.** Before the user sees work, a different model family reviews it (each row in Model selection is a separate family). Check YAGNI first.
* **PRs only.** Land work through PRs. Never push to main or rewrite history.

# Delegation

## Orchestrating

If no agent started you and you delegate:

* Brief fully: how to verify, what is known and the open questions. For a long job, write the literal `agent-wait` steps. When the work adds or changes a test or rule, list the project's own solutions that must still pass.
* Start implementers and strong gates yourself. Never brief a worker to start them.
* Run at most two children of one expensive family (Opus, Neon, Sol) at once. Cheap models may fan out.
* Load `request-review` before briefing a reviewer or acting on its findings. Tell an implementer to load `request-review` and get up to two low-cost reviews before returning.
* **In T3:**
  * Send follow-ups and re-checks to the child that did the work (`t3_thread_send`), not a new `delegate_task`, so it keeps its context. This overrides T3's own rule.
  * Never start a new child for work that a stalled or quota-failed child still holds; resume that child instead.
  * After a quota failure, T3 usually resumes the child itself once the reset passes, with a run that says "Continue where you left off". Resume it yourself (`t3_thread_send`) only if, a few minutes after the reset, `task_status` and `t3_thread_list` show no run started since the failure. Otherwise your message is a second "continue". If the failure reported no reset time, T3 won't resume the child, so resume it yourself once the quota is back.
  * Use `mode: "auto"`. It steers a running turn, so a correction can reach a long gate before its turn ends; otherwise it starts or queues the message. Use `mode: "queue"` for a separate next task.
  * Clear stale queued sends with `t3_queue`, not `task_cancel`, which stops the child's current work and its delegates even when the task ID you pass already finished.
* While work remains, run independent work beside a blocked stream. End a turn only with a tracked child running, a picker question open or the task done.

## Delegated work

If another agent started you:

* Don't use ask-user or picker tools, because they reach the user instead of the orchestrator. Ask by ending your turn with the question.
* Delegate only reviews, and only to low-cost models from other families.
* Don't end your turn while a shell job or harness background task you started is still running, even if your harness says it will wake you. Ending your turn hands control back to the orchestrator, and a background completion wake can still be missed. Run long jobs with `agent-wait start LOG -- CMD`, then `agent-wait wait LOG` (and `agent-wait stop LOG` to cancel; see `agent-wait --help`). On exit 3 (stalled), end your turn and report the job's state and how to resume.
* If something you don't control (memory, a lock, a quota) blocks you for more than 10 minutes, end your turn and report it.

# Model selection

Use the cheapest model that is smart enough for the task. Use only these:

| Worker | Model (harness) | Effort | Role | Cost |
|---|---|---|---|---|
| Opus 5.5 | `claude-opus-5-5` (Claude Code) | `high` | Architect: design, grilling, orchestration and review | high |
| Gemini 4 Neon | `gemini-4-neon` (Antigravity) | `high` | Architect: design, grilling, orchestration, review, docs and copy | high |
| Sol 6.2 | `gpt-6.2-sol` (Codex) | `high` | Hard, well-defined implementation and the strictest reviews: use it when work must have zero mistakes | high |
| Muse 1.3 | `opencode-go/muse-spark-1.3-contributor` (OpenCode) | `xhigh` | Default for research, scoped tasks and low-cost reviews | low |
| GLM 5.3 Flash | `opencode-go/glm-5.3-flash` (OpenCode) | `high` | Fallback and second low-cost reviewer | low |

# Fleet
* Run builds, VMs and long-running jobs on `msi-dux`. Load the `fleet` skill first.
* `msi-dux` dual-boots Windows. Never touch its physical disks or boot configuration.
