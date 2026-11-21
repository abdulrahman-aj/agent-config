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
| `~/.gemini/AGENTS.md` | `global/AGENTS.md` |
| `~/.agents/skills/<name>` | `global/skills/<name>/` |
| `~/.claude/skills/<name>` | `global/skills/<name>/` |
| `~/.config/opencode/skills/<name>` | `global/skills/<name>/` |
| `~/.gemini/config/skills/<name>` | `global/skills/<name>/` |
| `~/.config/opencode/<file>` | `home/.config/opencode/<file>` |
| `~/.t3/userdata/settings.json` | `home/.t3/userdata/settings.json` |
| `~/.claude/settings.json` | `home/.claude/settings.json` |
| `~/.local/bin/agent-wait` | `home/.local/bin/agent-wait` |
| `~/.config/environment.d/60-agent-heavy-jobs.conf` (laptop) | `hosts/zenbook-dux/.config/environment.d/60-agent-heavy-jobs.conf` |

Native directories remain real, so separately installed skills coexist.

T3 runs Gemini through its Antigravity provider. `binaryPath: agy` makes it use the `agy` CLI that dotfiles installs
with the other harnesses, instead of a runtime T3 downloads. T3 gives `agy` a private profile, so `agy login` in a
terminal doesn't sign T3 in: sign in once per machine in T3's Antigravity provider settings. T3 0.1.11 or newer is
needed for that profile to pick up `~/.gemini/AGENTS.md` and for sign-in on a headless host such as msi-dux.

`~/.claude/settings.json` is plain JSON, so its reasons live here. It compacts at 400k (about 367k in practice)
instead of the ~967k default, because every request re-reads the whole context, and pins the 1-hour prompt cache.
Leave `subagentPromptCacheTtl` unset: T3 would apply it to delegate children, whose cache would then expire during
build waits. Claude Code writes `/autocompact` and `/config` changes through the link into this repo, and under T3
a change applies when T3 next starts the Claude process. Evidence:
[PR #13](https://github.com/abdulrahman-aj/agent-config/pull/13).

Restart the harness or refresh the skill catalog to see edited instructions or
newly deployed skills. Changes to `environment.d` apply after the next login.

Run `make help` for targets.
