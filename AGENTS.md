# Personal

* **Prose**: state the outcome, be concise.
* **Ask early** on scope, behavior, cost, reversibility.
* **Questions**: multiple-choice, strongest first `(recommended)`; batch up to 5.

# Software Design
* **YAGNI**: default to NO; build only what's needed and NO MORE.
* **Deep modules**: small, stable interface hiding a rich implementation. Expose capabilities, not decisions.
* **Simplicity wins**: simplest correct solution; nothing clever, brittle, or surprising.
* **Abstractions**: duplicate first; abstract only when it reduces complexity.
* **Naming**: unclear names signal unclear abstractions. Rethink the design.

# Code Style
* **Readability**: prefer readable code over compactness.
* **Locality of behavior**: understandable from nearby code, no hidden side effects.
* **Comments**: why, not what: rationale, invariants, performance, constraints.
* **Shell**: do not embed Python in `.sh` files; write `.py` files.

# Testing
* **Always verify**: no success without evidence.
* **Automated evidence**: committed tests; manual only if automation is impractical.
* **Test what you fear**: prioritize code most likely to break.
* **Behavior over implementation**: test behavior, not internals; behavior survives refactoring.

# Refactoring
* **Before the change**: refactor to simplify or de-risk it.
* **Gardening**: look for YAGNI; aim for net-negative LOC.
* **Scout rule**: leave it better than you found it; stay in scope.
* **Chesterton's fence**: understand why it exists before you remove it.

# Workflow
* **Dev environments**: use the project's Nix dev shell, or add a minimal one.
* **Reusable tasks**: work through deterministic scripts (interact, debug, verify); expose additions via Makefile or similar; don't reinvent.
* **Delegate**: for speed, cost, or expertise; brief fully: verification, findings, open questions.
* **Bug discipline**: solve the root cause, not the symptom; every fix gets a regression test.
* **Porting**: document omissions and divergences in the target repository.
* **Review**: at each milestone before the PR, different family, YAGNI first.
* **PRs only**: land work via PRs; never push to main or rewrite history.

# Model selection

| Worker | Role | Smarts | Effort | Cost | Trains? |
|---|---|---|---|---|---|
| Sol 6.1 (Codex `gpt-6.1-sol`) | hard reasoning, 2nd opinion | highest | high | high | no |
| Muse 1.3 (`opencode-go/muse-spark-1.3-contributor`) | default | high | xhigh | low | yes |
| GLM 5.3 Flash (`opencode-go/glm-5.3-flash`) | fallback, 2nd opinion | high | max | low | no |

- Muse: ask before first use unless already approved.
- Only use these models.
