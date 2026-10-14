#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
checkout="$scratch/checkout with spaces"
target="$scratch/home with spaces"
roots=(.agents .claude .config/opencode)

fail() { echo "FAIL: $*" >&2; exit 1; }
deploy() { make -s -C "$checkout" "$@" TARGET="$target" >/dev/null; }

mkdir -p "$checkout/scripts" "$checkout/skills/example" "$scratch/omarchy"
cp "$repo/Makefile" "$checkout/Makefile"
cp "$repo/scripts/prepare-stow.sh" "$checkout/scripts/"
printf 'instructions\n' > "$checkout/AGENTS.md"
printf 'skill\n' > "$checkout/skills/example/SKILL.md"
printf 'system skill\n' > "$scratch/omarchy/SKILL.md"
for root in "${roots[@]}"; do
    mkdir -p "$target/$root/skills/local"
    printf 'local skill\n' > "$target/$root/skills/local/SKILL.md"
    ln -s "$scratch/omarchy" "$target/$root/skills/omarchy"
done

deploy install
deploy install
deploy check
for root in "${roots[@]}"; do
    [[ -d "$target/$root/skills" && ! -L "$target/$root/skills" ]] \
        || fail "native skills directory was replaced: $root"
    [[ "$(realpath "$target/$root/skills/example")" == "$checkout/skills/example" ]] \
        || fail "shared skill is not linked: $root"
    grep -qx 'local skill' "$target/$root/skills/local/SKILL.md" || fail "local skill changed"
    [[ "$(readlink "$target/$root/skills/omarchy")" == "$scratch/omarchy" ]] \
        || fail "Omarchy link changed"
done

# Atomic edits follow the source; resources within a linked skill are live too.
printf 'updated instructions\n' > "$checkout/replacement.md"
mv "$checkout/replacement.md" "$checkout/AGENTS.md"
mkdir "$checkout/skills/example/references"
printf 'resource\n' > "$checkout/skills/example/references/new.md"
for path in .agents/AGENTS.md .codex/AGENTS.md .claude/CLAUDE.md .config/opencode/AGENTS.md; do
    grep -qx 'updated instructions' "$target/$path" || fail "instruction edit is not live"
done
for root in "${roots[@]}"; do
    grep -qx 'resource' "$target/$root/skills/example/references/new.md" \
        || fail "resource is not live"
done

mkdir "$checkout/skills/new-skill"
printf 'new skill\n' > "$checkout/skills/new-skill/SKILL.md"
[[ ! -e "$target/.agents/skills/new-skill" ]] || fail "new skill appeared before make"
# Checking a new name must detect its conflicts without uninstalling working links.
mkdir "$target/.agents/skills/new-skill"
printf 'user skill\n' > "$target/.agents/skills/new-skill/SKILL.md"
if deploy check 2>"$scratch/check-conflict.log"; then
    fail "check missed conflicting new skill"
fi
if deploy install 2>"$scratch/install-conflict.log"; then
    fail "install accepted conflicting new skill"
fi
grep -qx 'user skill' "$target/.agents/skills/new-skill/SKILL.md" \
    || fail "conflicting skill changed"
[[ -L "$target/.agents/skills/example" ]] || fail "failed reinstall removed working skill"
grep -qx 'updated instructions' "$target/.claude/CLAUDE.md" \
    || fail "failed reinstall removed working instructions"
rm -rf "$target/.agents/skills/new-skill"
deploy install
for root in "${roots[@]}"; do
    grep -qx 'new skill' "$target/$root/skills/new-skill/SKILL.md" || fail "new skill missing"
done
rm -rf "$checkout/skills/new-skill"
deploy install
for root in "${roots[@]}"; do
    [[ ! -L "$target/$root/skills/new-skill" ]] || fail "removed skill link remains"
done

# A replacement of an installed instruction must not unlink other managed paths.
rm "$target/.codex/AGENTS.md"
printf 'user instructions\n' > "$target/.codex/AGENTS.md"
if deploy install 2>"$scratch/conflict.log"; then
    fail "Stow accepted conflicting instructions"
fi
grep -qx 'user instructions' "$target/.codex/AGENTS.md" || fail "conflicting file changed"
[[ -L "$target/.agents/skills/example" ]] || fail "instruction conflict unlinked skills"
rm "$target/.codex/AGENTS.md"
deploy install
deploy unstow
deploy unstow
for root in "${roots[@]}"; do
    [[ ! -L "$target/$root/skills/example" ]] || fail "managed link remains"
    grep -qx 'local skill' "$target/$root/skills/local/SKILL.md" || fail "local skill lost"
    [[ -L "$target/$root/skills/omarchy" ]] || fail "Omarchy link removed"
done
if make -s -C "$checkout" check TARGET="$scratch/nonexistent" \
    >"$scratch/missing-target.log" 2>&1; then
    fail "check accepted a missing target"
fi
make -s -C "$checkout" unstow TARGET="$scratch/nonexistent" >/dev/null
[[ ! -e "$scratch/nonexistent" ]] || fail "check or unstow created the missing target"
echo "Agent Stow deployment test passed"
