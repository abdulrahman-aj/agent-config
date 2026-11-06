# Personal

* **Prose**: state the outcome, be concise.
* **Ask early** on scope, behavior, cost, reversibility.
* **Questions**: multiple-choice, strongest first `(recommended)`; batch up to 5.

# Software Design
* **YAGNI**: default to NO; build only what's needed and NO MORE.
* **Deep modules**: small, stable interface hiding a rich implementation.
* **Simplicity wins**: simplest correct solution; nothing clever, brittle, or surprising.
* **Abstractions**: duplicate first; abstract only when it reduces complexity.
* **Naming**: unclear names signal unclear abstractions. Rethink the design.

# Code Style
* **Readability**: prefer readable code over compactness.
* **Locality of behavior**: group related code nearby.
* **Comments**: why, not what: rationale, invariants, performance, constraints.
* **Shell**: do not embed Python in `.sh` files; write `.py` files.

# Testing
* **Always verify**: no success without evidence.
* **Automated evidence**: committed tests; manual only if automation is impractical.
* **Test what you fear**: prioritize code most likely to break.
* **Behavior over implementation**: test behavior, not internals; behavior survives refactoring.

# Refactoring
* **Before the change**: refactor to simplify or de-risk it.
* **Gardening**: look for YAGNI; aim to delete more than you add.
* **Scout rule**: leave it better than you found it; stay in scope.
* **Chesterton's fence**: understand why it exists before you remove it.

# Workflow
* **Dev environments**: use the project's Nix dev shell, or add one if none exists.
* **Reusable tasks**: work through deterministic scripts (e.g. interact, debug, verify); expose additions via Makefile or similar; don't reinvent.
* **Delegate**: for speed, cost, or expertise; brief fully: verification, findings, open questions.
* **Bug discipline**: solve the root cause, not the symptom; every fix gets a regression test.
* **Porting**: document omissions and divergences in the target repository.
* **Review**: before the user sees it, by a different family (e.g. Opus or Muse reviews Sol; Sol or GLM reviews Opus); YAGNI first.
* **PRs only**: land work via PRs; never push to main or rewrite history.

# Model selection

Use the cheapest model smart enough for the task. Only these:

| Worker | Model (harness) | Effort | Role | Smarts | Cost |
|---|---|---|---|---|---|
| Opus 5.5 | `claude-opus-5-5` (Claude Code) | `medium` | architect: design, grilling, orchestration, review; top-level only, never a delegate | highest | high |
| Sol 6.1 | `gpt-6.1-sol` (Codex) | `high` | foundational implementation, hard reasoning | highest | high |
| Muse 1.3 | `opencode-go/muse-spark-1.3-contributor` (OpenCode) | `xhigh` | default: research, scoped tasks, reviews | high | low |
| GLM 5.3 Flash | `opencode-go/glm-5.3-flash` (OpenCode) | `high` | fallback; second reviewer | high | low |
