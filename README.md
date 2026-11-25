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
| `~/<path>` | `home/<path>` |
| `~/<path>` (per host) | `hosts/<hostname>/<path>` |

Native directories remain real, so separately installed skills coexist.

T3 runs Gemini through its Antigravity provider. `binaryPath: agy` makes it use the `agy` CLI that dotfiles installs
with the other harnesses, instead of a runtime T3 downloads. T3 gives `agy` a private profile, so signing in from a
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

## Leak guard

`home/.local/bin/leak-check` stops private GitHub repository names from reaching public repositories.
It queries GitHub through `gh` for the target repository's visibility and its owner's private repository names, caching both under `~/.cache/leak-check/` for 24 hours.
Add extra project names that are not repository names, one per line, to `~/.config/leak-check/terms` (local only, never committed; `#` lines are comments and `!name` excludes a noisy repo name).

What it covers:
- Every agent's `git push` to a public GitHub repository, through the global `pre-push` hook in `home/.config/git/config`. It scans commit messages, tag messages, added filenames, and added lines not yet on any remote-tracking ref. Repository-local `pre-push` hooks still run alongside it.
- Claude Code's `Bash` tool calls that publish text with `gh` (`pr`, `issue`, `release`, and `api` calls with `-f`/`-F`/`--field`/`--raw-field`/`--input`, plus files passed via `--body-file`, `--notes-file`, `-F`, or `--input`), through the `PreToolUse` hook in `home/.claude/settings.json`.

What it does not cover:
- `gh` calls from other harnesses (Codex, Antigravity, OpenCode) rely on the rule in `global/AGENTS.md` and the git `pre-push` hook.
- Commits already contained in a remote-tracking ref, `git push --no-verify`, non-GitHub remotes, and text sent through other channels such as `curl` or a browser.
- Private repositories owned by a different GitHub account than the target repository's owner (add those to `~/.config/leak-check/terms`), private repositories past the 1,000-repo `gh repo list` cap, or repositories created within the 24-hour cache window.

If `gh` fails (offline or unauthenticated), `leak-check` fails closed. Set `LEAK_CHECK_SKIP=1` to bypass the check; it prints a notice to stderr when skipped.

Run `make help` for targets.
