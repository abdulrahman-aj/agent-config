# agent-config

Personal instructions, skills, and OpenCode config for T3.

## Install

```bash
git clone https://github.com/abdulrahman-aj/agent-config.git ~/agent-config
make -C ~/agent-config        # deploy origin/main
make -C ~/agent-config setup  # helper tooling (ccusage)
```

`make` (`make deploy`) clones or updates a pinned checkout at
`~/.local/share/agent-config` to `origin/main` and links your home to it. Agents
load only merged work, so branches in `~/agent-config` are safe. `make install`
links the checkout you run it from, and refuses your home unless that checkout is
the pinned one.

## One source

Edit `global/AGENTS.md` for personal instructions, `global/skills/<name>/SKILL.md` for skills,
`home/` for files stowed 1:1, and `hosts/<hostname>/` for files stowed on one machine only. Fan-outs (one source, many homes) are linked
by `scripts/link-shared.sh` instead — anything 1:1 lives under `home/`.

| Installed path | Source |
| --- | --- |
| `~/.agents/AGENTS.md` | `global/AGENTS.md` |
| `~/.codex/AGENTS.md` | `global/AGENTS.md` |
| `~/.claude/CLAUDE.md` | `global/AGENTS.md` |
| `~/.config/opencode/AGENTS.md` | `global/AGENTS.md` |
| `~/.agents/skills/<name>` | `global/skills/<name>/` |
| `~/.claude/skills/<name>` | `global/skills/<name>/` |
| `~/.config/opencode/skills/<name>` | `global/skills/<name>/` |
| `~/.config/opencode/<file>` | `home/.config/opencode/<file>` |
| `~/.t3/userdata/settings.json` | `home/.t3/userdata/settings.json` |
| `~/.local/bin/agent-wait`, `~/.local/bin/fleet-run` | `home/.local/bin/` |
| `~/.claude/hooks/agent-guard` | `home/.claude/hooks/agent-guard` |
| `~/.claude/settings.json` (hook entries merged in) | `scripts/claude-hooks.py` |
| `~/.config/environment.d/60-agent-heavy-jobs.conf` (laptop) | `hosts/zenbook-arch-dux/` |

Native directories remain real, so separately installed skills coexist.

Restart the harness or refresh the skill catalog to see edited instructions or
newly deployed skills. Changes to `environment.d` apply after the next login.

Run `make help` for targets.
