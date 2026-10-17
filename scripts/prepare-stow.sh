#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
package="$repo/.stow/home"
# The old alias set stays in place until install unstows and restows it.
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

while IFS= read -r -d '' config; do
    relative="${config#"$repo/opencode/"}"
    alias="$package/.config/opencode/$relative"
    mkdir -p "$(dirname "$alias")"
    ln -srfn "$config" "$alias"
done < <(find "$repo/opencode" -type f -print0)
