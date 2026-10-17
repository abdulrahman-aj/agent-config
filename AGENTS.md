# agent-config

Personal T3/harness config, deployed to `$HOME`.

## Layout

- `global/` — everything fanned out to every harness (`AGENTS.md`, `skills/`).
- `home/` — files stowed 1:1 (e.g. `home/.config/opencode/`).
- `scripts/link-shared.sh` — the 1:N fan-out links plus stale-link repair.

Placement rule: 1:1 lives under `home/`; 1:N goes in the link script.

## Workflow

- `make` deploys; `make check` dry-runs; `make test` is the gate (keep green);
  `make uninstall` tears down; `make setup` installs helper tooling.
- Land via PRs; commit only when asked.
