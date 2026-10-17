# agent-config

Personal instructions, skills, and OpenCode config for T3.

## Install

```bash
git clone git@github.com:abdulrahman-aj/agent-config.git ~/agent-config
make -C ~/agent-config
make -C ~/agent-config setup  # helper tooling (ccusage)
```

## One source

Edit `global/AGENTS.md` for personal instructions, `global/skills/<name>/SKILL.md` for skills,
and `home/` for files stowed 1:1. Fan-outs (one source, many homes) are linked
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
| `~/.t3/userdata/keybindings.json` | `home/.t3/userdata/keybindings.json` |

Native directories remain real, so separately installed skills coexist.

Restart the harness or refresh the skill catalog to see edited instructions or
newly deployed skills.

Run `make help` for targets.
