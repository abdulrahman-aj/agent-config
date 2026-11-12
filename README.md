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
| `~/.local/share/applications/t3code.desktop` (laptop) | `hosts/zenbook-dux/.local/share/applications/t3code.desktop` |

Native directories remain real, so separately installed skills coexist.

`~/.claude/settings.json` is plain JSON, so its reasons live here. It compacts at 400k (about 367k in practice)
instead of the ~967k default, because every request re-reads the whole context, and pins the 1-hour prompt cache.
Leave `subagentPromptCacheTtl` unset: T3 would apply it to delegate children, whose cache would then expire during
build waits. Claude Code writes `/autocompact` and `/config` changes through the link into this repo, and under T3
a change applies when T3 next starts the Claude process. Evidence:
[PR #13](https://github.com/abdulrahman-aj/agent-config/pull/13).

Restart the harness or refresh the skill catalog to see edited instructions or
newly deployed skills. The T3 launcher override applies the next time T3 is
started from the app launcher; one re-login clears the old session-wide
variable from terminals.

Run `make help` for targets.
