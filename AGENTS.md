# agent-config

Personal T3/harness config, deployed to `$HOME`.

## Layout

- `global/`: everything fanned out to every harness (`AGENTS.md`, `skills/`).
- `home/`: files stowed 1:1 (e.g. `home/.config/opencode/`).
- `hosts/<hostname>/`: files stowed 1:1 on that machine only.
- `scripts/link-shared.sh`: the 1:N fan-out links plus stale-link repair.

Placement rule: 1:1 files live under `home/` (or `hosts/<hostname>/`), and 1:N links go in the link script.

## Workflow

- `make` deploys; `make check` dry-runs; `make test` is the gate (keep green);
  `make uninstall` tears down; `make setup` installs helper tooling.
- Deployed links point into the checkout `make` ran from (`~/agent-config`), so
  edits there are live. Edit in a git worktree when a change shouldn't go live yet.
- Land via PRs; commit only when asked.
