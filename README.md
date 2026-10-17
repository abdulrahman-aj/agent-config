# agent-config

Personal instructions, skills, and OpenCode config for T3.

## Install

```bash
git clone git@github.com:abdulrahman-aj/agent-config.git ~/agent-config
make -C ~/agent-config
```

## One source

Edit `AGENTS.md` for personal instructions, `skills/<name>/SKILL.md` for skills,
and `home/` for files stowed 1:1. Fan-outs (one source, many homes) are linked
by `scripts/link-shared.sh` instead — anything 1:1 lives under `home/`.

| Installed path | Source |
| --- | --- |
| `~/.agents/AGENTS.md` | `AGENTS.md` |
| `~/.codex/AGENTS.md` | `AGENTS.md` |
| `~/.claude/CLAUDE.md` | `AGENTS.md` |
| `~/.config/opencode/AGENTS.md` | `AGENTS.md` |
| `~/.agents/skills/<name>` | `skills/<name>/` |
| `~/.claude/skills/<name>` | `skills/<name>/` |
| `~/.config/opencode/skills/<name>` | `skills/<name>/` |
| `~/.config/opencode/<file>` | `home/.config/opencode/<file>` |

Native directories remain real, so separately installed skills coexist.

Restart the harness or refresh the skill catalog to see edited instructions or
newly deployed skills.

Run `make help` for targets.
