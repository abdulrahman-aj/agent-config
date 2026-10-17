# Personal agent instructions

# Personal

* Name: Abdulrahman.
* Be concise. Skip preambles and postambles.
* Lead with the outcome; avoid play-by-play summaries.
* **Ask early**: ask when choices materially affect scope, behavior, cost, or reversibility; decide routine details.
* Prefer multiple-choice questions. Batch up to 5 related questions.
* Sort recommendations strongest first, labeling the top choice "(recommended)".
* Include a TL;DR only for large or multi-file changes.

# Principles

## Software Design
* **Deep modules**: small, stable interfaces hiding rich implementations. Push complexity down; expose capabilities, not decisions.
* **Simplicity wins**: complexity compounds. Prefer the simplest correct solution; reconsider anything clever, brittle, or surprising.
* **Abstractions**: don't introduce one until it clearly reduces complexity. Duplicate first; abstract when a stable concept emerges.
* **Readability**: prefer readable code over compactness. Extract non-trivial logic instead of embedding it inline.
* **Naming**: unclear names signal unclear abstractions. Rethink the design.
* **Locality**: behavior should be understandable from nearby code. Avoid hidden side effects and distant dependencies.
* **Comments**: explain why, not what. Reserve comments for design rationale, invariants, non-obvious performance decisions, and external constraints.

## Code Style
* **Nesting**: reduce nesting for readability, not arbitrary limits.
* **Line length**: prefer lines under 100 characters.
* **Scripts**: prefer standalone files over long shell or Python strings.

## Testing
* **Test what you fear**: prioritize code most likely to break or that took real effort to get right.
* **Behavior over implementation**: test observable behavior, not internal details.
* **Avoid brittle tests**: prefer assertions that survive refactoring.
* **Bug discipline**: add a regression test for fixes; use direct checks when automation is impractical.

## Refactoring
* **Scout rule**: leave touched code cleaner; keep cleanup within the task's scope.
* **Chesterton's fence**: before removing an existing constraint, understand why it exists.
* **Refactoring**: refactor to simplify or safeguard the requested change.

## Workflow
* **Dev environments**: when Nix is available, use the project's Nix dev shell or add a minimal one.
* **Isolation**: use a worktree for parallel changes.
* **Verify**: don't declare success without evidence (tests, logs, or observable behavior).
* **Root cause**: solve the underlying cause, not the symptom.
* **Tracer bullets**: build a thin end-to-end slice before filling in details.
* **Reversible first**: flag hard-to-reverse decisions before making them.
* **Port omissions**: explicitly document every omitted upstream behavior in the target repository.
* **Reuse context**: carry the brief, findings, and unresolved questions across threads.
* **Delegation**: use cheaper suitable workers for routine tasks, including verification; keep key decisions and synthesis with the primary. Keep trivial work local.

## Automation
* **Automate friction**: turn recurring manual work and preventable failures into project-local guardrails.
* **Evidence first**: automate observed friction, not hypothetical problems. Ask before adding dependencies or changing shared workflows.
* **Recurring commands**: use the existing task runner for frequently repeated commands.

## Collaboration
* **Approval required**: get explicit user approval before Git commits or destructive actions.

## Misc
* **Project tasks first**: check for project tasks (e.g. Makefiles, Taskfiles) before running commands.

# Agent delegation

- Delegate when it saves time or adds expertise.
- Keep key decisions and context-heavy work in the primary agent.
- Give each worker a clear task and checks to run.
- Only these workers:
  - Muse 1.3 xhigh (`opencode-go/muse-spark-1.3-contributor`): default worker. May train on your content: ask before first use unless already approved.
  - GLM 5.3 Flash max (`opencode-go/glm-5.3-flash`): when Muse's data terms don't fit, or for a second opinion.
  - Sol 6.1 high (Codex `gpt-6.1-sol`): hard reasoning, or a second opinion.

## Review

- Reviewer at each milestone (YAGNI: is the change needed, would smaller suffice?); extra reviewers only for a specific concern or on request.

# Shared instructions and skills

Edit sources (`skills/`, `opencode/`), not deployed links: edits are live, but `make` after adding or removing, and reload the session. Project rules → project's `AGENTS.md`, personal → here.

# Privilege elevation

* If `sudo -n true` succeeds, use root directly.
* Otherwise, defer elevation and batch root ops via `pkexec`; never wait on terminal password input. If elevation stalls, return one command and stop.
