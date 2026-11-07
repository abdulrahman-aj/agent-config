# agent-config

Personal T3/harness config, deployed to `$HOME`.

## Layout

- `global/`: everything fanned out to every harness (`AGENTS.md`, `skills/`).
- `home/`: files stowed 1:1 (e.g. `home/.config/opencode/`).
- `hosts/<hostname>/`: files stowed 1:1 on that machine only.
- `scripts/link-shared.sh`: the 1:N fan-out links plus stale-link repair.
- `scripts/deploy.sh`: pins `~/.local/share/agent-config` to origin/main and installs from it.
- `scripts/claude-hooks.py`: merges agent-guard's hooks into `~/.claude/settings.json`.

Placement rule: 1:1 files live under `home/` (or `hosts/<hostname>/`), and 1:N links go in the link script.

## Workflow

- `make` deploys merged work from the pinned checkout, so edit and switch
  branches in `~/agent-config` freely; `make check` dry-runs; `make test` is the gate (keep green);
  `make uninstall` tears down; `make setup` installs helper tooling.
- Land via PRs; commit only when asked.
