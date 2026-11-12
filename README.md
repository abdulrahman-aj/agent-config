# agent-config

Personal instructions, skills, and OpenCode config for T3.

## Install

```bash
git clone git@github.com:abdulrahman-aj/agent-config.git ~/agent-config
make -C ~/agent-config
make -C ~/agent-config setup  # helper tooling (ccusage)
```

The links point into the checkout you run `make` from (`~/agent-config`), so
edits there are live for every agent. Edit in a git worktree when a change
shouldn't go live yet.

## One source

Edit `global/AGENTS.md` for personal instructions, `global/skills/<name>/SKILL.md` for skills,
`home/` for files stowed 1:1, and `hosts/<hostname>/` for files stowed on one machine only.
Fan-outs (one source, many homes) are linked by `scripts/link-shared.sh` instead. Anything 1:1 lives under `home/` or `hosts/<hostname>/`.

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
| `~/.claude/settings.json` | `home/.claude/settings.json` |
| `~/.local/bin/agent-wait` | `home/.local/bin/agent-wait` |
| `~/.config/environment.d/60-agent-heavy-jobs.conf` (laptop) | `hosts/zenbook-dux/.config/environment.d/60-agent-heavy-jobs.conf` |

Native directories remain real, so separately installed skills coexist.

`~/.claude/settings.json` compacts at 400k instead of the ~967k default on 1M models (Lydia Hallie,
https://x.com/lydiahallie/status/2108624109538291901): every turn re-reads the whole context, so a cap keeps
turns and post-idle cache rewrites bounded. `promptCacheTtl: "1h"` keeps the 1-hour cache even on usage credits,
where the default drops to 5 minutes. Claude Code writes `/autocompact` and `/config` changes through the link
into this repo, so they show up as a diff here.

Restart the harness or refresh the skill catalog to see edited instructions or
newly deployed skills. Changes to `environment.d` apply after the next login.

Run `make help` for targets.
