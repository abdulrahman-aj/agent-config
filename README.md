# agent-config

Private personal instructions and Agent Skills shared by Codex, OpenCode, and
Claude Code, plus OpenCode configuration, including when run through T3 Code.

## Install

Requires Bash, GNU Stow, GNU coreutils, Git, and Make.

```bash
git clone git@github.com:abdulrahman-aj/agent-config.git ~/agent-config
make -C ~/agent-config
```

Dotfiles can bootstrap the same checkout with `make agents`. No harness is installed.

## One source

Edit `AGENTS.md` for personal instructions, `skills/<name>/SKILL.md` for skills,
and `opencode/` for OpenCode configuration.
Keep each skill's scripts, references, and other resources in the same folder.

| Installed path | Source |
| --- | --- |
| `~/.agents/AGENTS.md` | `AGENTS.md` |
| `~/.codex/AGENTS.md` | `AGENTS.md` |
| `~/.claude/CLAUDE.md` | `AGENTS.md` |
| `~/.config/opencode/AGENTS.md` | `AGENTS.md` |
| `~/.agents/skills/<name>` | `skills/<name>/` |
| `~/.claude/skills/<name>` | `skills/<name>/` |
| `~/.config/opencode/skills/<name>` | `skills/<name>/` |
| `~/.config/opencode/<file>` | `opencode/<file>` (including nested plugin files) |

`make` prepares symlink aliases in the ignored `.stow/home/` package, then deploys
them with `stow --no-folding`. The helper creates path mappings only; all content
stays in the source files. Native configuration and skill directories remain real
directories, so separately installed skills can coexist without being imported.

Only repository-owned configuration is deployed. OpenCode credentials, databases,
and other runtime data remain local and are never imported. `opencode.jsonc`
includes personal Linear/Todoist MCP registrations; VM configurations must omit
or disable these unless explicitly approved.

Edits, atomic file replacements, and resources within installed skill folders are
live. Run `make` after adding or removing a skill or to repair links. A source
folder becomes a skill when it contains `SKILL.md`. Unstow before moving or deleting
the checkout; install again from its new location. If the checkout is lost, restore
it at the original path before unstowing.

Global instruction changes may require a new harness session. Refresh the skill
catalog or restart if a newly deployed skill does not appear in the running session.

Stow reports conflicting user files or skill names and leaves them untouched.
Resolve those conflicts explicitly and rerun `make`. Unlike the previous installer,
this setup does not automatically back up conflicts, import local skills, resolve
collisions, or relocate local data. `make unstow` leaves unrelated skills and the
source checkout in place.

Run `make` after removing a shared skill before reusing its name for a local skill.
Otherwise Stow can report `unstow_contents() called with non-directory path` for
the old alias. To recover without losing the local skill, temporarily move its
folder outside the native skills directory, run `make`, then move it back.

## Commands

```bash
make                         # deploy or refresh the shared links
make check                   # refresh path aliases and dry-run without changing installed paths
make test                    # test deployment and preservation in a temporary home
make unstow                  # remove managed links
make TARGET=/path/to/home     # deploy for another home
```

`make check` includes newly added skills. It updates only the ignored path aliases,
without changing installed links. A conflicting reinstall leaves working links in place.
Its target home must already exist; `make unstow` is a no-op for a missing home.

## Moving OpenCode configuration from dotfiles

Run this once on an existing host:

```bash
make migrate-opencode DOTFILES_DIR="$HOME/dotfiles"
```

The handoff replaces only links to the old dotfiles OpenCode paths, then installs
all shared configuration. It refuses unmanaged files and changed dotfiles sources;
reconcile those changes first. A failed installation restores the old links.
Recognized dangling links left after updating dotfiles are supported too.
`TARGET` is honored, and repeated migration is safe. Fresh machines need only `make`.
