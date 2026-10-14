#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
package="$repo/.stow/home"
# Keep old aliases until installation has checked conflicts and unstowed them.
mkdir -p "$package/.codex"

for root in .agents .claude .config/opencode; do
    mkdir -p "$package/$root/skills"
    name=AGENTS.md
    [[ "$root" != .claude ]] || name=CLAUDE.md
    ln -srfn "$repo/AGENTS.md" "$package/$root/$name"
    for skill in "$repo"/skills/*; do
        [[ -f "$skill/SKILL.md" ]] || continue
        ln -srfn "$skill" "$package/$root/skills/$(basename "$skill")"
    done
done
ln -srfn "$repo/AGENTS.md" "$package/.codex/AGENTS.md"
