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

## Context and cache settings

Every request re-reads the whole context, so each harness gets a bounded context. Evidence and numbers are in
[PR #13](https://github.com/abdulrahman-aj/agent-config/pull/13).

- **Claude Code** (`~/.claude/settings.json`): `autoCompactWindow: 400000` compacts at about 367k (the window
  minus a ~33k reserve) instead of the ~967k default on 1M models. `promptCacheTtl: "1h"` pins the 1-hour
  cache, which otherwise drops to 5 minutes on usage credits. Leave `subagentPromptCacheTtl` unset: T3 applies
  it to delegate children, and a 5-minute cache would expire during every build wait. Claude Code writes
  `/autocompact` and `/config` changes through the link into this repo, so they show up as a diff here.
  Under T3, a change takes effect when T3 next starts the Claude process, which can be several turns later.
- **Codex**: no file. `gpt-6.1-sol` already runs a 500k window and compacts at 450k, and Codex has no
  cache-lifetime setting. To compact earlier, set `model_auto_compact_token_limit` in `~/.codex/config.toml`.
- **OpenCode** (`~/.config/opencode/opencode.jsonc`): `compaction.buffer: "60%"` compacts at 40% of the
  window, about 400–420k on the 1M Muse and GLM models. The default waits until 85%.

Orchestrators run the user-triggered `/heartbeat` skill: a 55-minute check-in that keeps work moving while the
user is away. On Claude it also keeps the 1-hour cache warm; Codex and OpenCode caches are short-lived and cheap
to miss, so they need no keep-alive of their own.

Restart the harness or refresh the skill catalog to see edited instructions or
newly deployed skills. Changes to `environment.d` apply after the next login.

Run `make help` for targets.
