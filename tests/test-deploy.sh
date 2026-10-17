#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
export XDG_CACHE_HOME="$scratch/cache"
checkout="$scratch/checkout with spaces"
target="$scratch/home with spaces"
roots=(.agents .claude .config/opencode)
record_key="$(printf '%s' "$target" | cksum | cut -d' ' -f1)"
record_is() { [[ "$(cat "$XDG_CACHE_HOME/agent-config/repo.$record_key")" == "$(realpath "$checkout")" ]]; }

fail() { echo "FAIL: $*" >&2; exit 1; }
deploy() { make -s -C "$checkout" "$@" TARGET="$target" >/dev/null; }

# Legacy double-hop links (via an intermediate alias, as the old farm made)
# must be normalized to a single hop on install.
mkdir -p "$checkout/scripts" "$checkout/global/skills/example" "$checkout/global" "$checkout/home/.config/opencode" "$checkout/home/.t3/userdata" "$scratch/omarchy"
cp "$repo/Makefile" "$checkout/Makefile"
cp "$repo/scripts/link-shared.sh" "$checkout/scripts/"
cp "$repo/home/.config/opencode/cli.json" "$repo/home/.config/opencode/opencode.jsonc" "$checkout/home/.config/opencode/"
cp "$repo/home/.t3/userdata/settings.json" "$repo/home/.t3/userdata/keybindings.json" "$checkout/home/.t3/userdata/"
printf 'instructions\n' > "$checkout/global/AGENTS.md"
printf 'skill\n' > "$checkout/global/skills/example/SKILL.md"
printf 'system skill\n' > "$scratch/omarchy/SKILL.md"
for root in "${roots[@]}"; do
    mkdir -p "$target/$root/skills/local"
    printf 'local skill\n' > "$target/$root/skills/local/SKILL.md"
    ln -s "$scratch/omarchy" "$target/$root/skills/omarchy"
done
ln -s "$checkout/global/skills/example" "$scratch/mid-skill"
ln -s "$scratch/mid-skill" "$target/.agents/skills/example"
mkdir -p "$target/.codex"
ln -s "$checkout/global/AGENTS.md" "$scratch/mid-instructions"
ln -s "$scratch/mid-instructions" "$target/.codex/AGENTS.md"

deploy install
deploy install
record_is || fail "repo record wrong"
deploy check
while IFS= read -r -d '' config; do
    relative="${config#"$checkout/home/"}"
    [[ "$(realpath "$target/$relative")" == "$config" ]] \
        || fail "stowed file is not linked: $relative"
done < <(find "$checkout/home" -type f -print0)
for root in "${roots[@]}"; do
    [[ -d "$target/$root/skills" && ! -L "$target/$root/skills" ]] \
        || fail "native skills directory was replaced: $root"
    [[ "$(realpath "$target/$root/skills/example")" == "$checkout/global/skills/example" ]] \
        || fail "shared skill is not linked: $root"
    grep -qx 'local skill' "$target/$root/skills/local/SKILL.md" || fail "local skill changed"
    [[ "$(readlink "$target/$root/skills/omarchy")" == "$scratch/omarchy" ]] \
        || fail "Omarchy link changed"
done
# Single hop: the link's immediate target, resolved from its own directory,
# is the repo source itself — no intermediate farm links.
[[ "$(realpath -m "$target/.agents/skills/$(readlink "$target/.agents/skills/example")")" == "$checkout/global/skills/example" ]] \
    || fail "skill link is not single-hop"
[[ "$(realpath -m "$target/.codex/$(readlink "$target/.codex/AGENTS.md")")" == "$checkout/global/AGENTS.md" ]] \
    || fail "instruction link is not single-hop"

# Atomic edits follow the source; resources within a linked skill are live too.
printf 'updated instructions\n' > "$checkout/global/replacement.md"
mv "$checkout/global/replacement.md" "$checkout/global/AGENTS.md"
mkdir "$checkout/global/skills/example/references"
printf 'resource\n' > "$checkout/global/skills/example/references/new.md"
for path in .agents/AGENTS.md .codex/AGENTS.md .claude/CLAUDE.md .config/opencode/AGENTS.md; do
    grep -qx 'updated instructions' "$target/$path" || fail "instruction edit is not live"
done
for root in "${roots[@]}"; do
    grep -qx 'resource' "$target/$root/skills/example/references/new.md" \
        || fail "resource is not live"
done

mkdir "$checkout/global/skills/new-skill"
printf 'new skill\n' > "$checkout/global/skills/new-skill/SKILL.md"
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
rm -rf "$checkout/global/skills/new-skill"
deploy install
for root in "${roots[@]}"; do
    [[ ! -L "$target/$root/skills/new-skill" ]] || fail "removed skill link remains"
done

# A removed shared skill leaves a same-name user directory alone.
rm -f "$target/.agents/skills/relocated"
mkdir "$checkout/global/skills/relocated"
printf 'shared skill\n' > "$checkout/global/skills/relocated/SKILL.md"
deploy install
rm -rf "$checkout/global/skills/relocated"
rm -f "$target/.agents/skills/relocated"
mkdir "$target/.agents/skills/relocated"
printf 'user skill\n' > "$target/.agents/skills/relocated/SKILL.md"
deploy install
grep -qx 'user skill' "$target/.agents/skills/relocated/SKILL.md" || fail "user dir changed"
[[ ! -L "$target/.agents/skills/relocated" ]] || fail "user dir replaced by link"
rm -rf "$target/.agents/skills/relocated"

# Moving the checkout then installing cleans stale links and relinks fresh.
mv "$checkout" "$scratch/moved checkout"
checkout="$scratch/moved checkout"
deploy install
record_is || fail "repo record not updated after move"
for root in "${roots[@]}"; do
    [[ "$(realpath "$target/$root/skills/example")" == "$checkout/global/skills/example" ]] \
        || fail "skill not relinked after move: $root"
done
[[ "$(realpath "$target/.codex/AGENTS.md")" == "$checkout/global/AGENTS.md" ]] \
    || fail "instructions not relinked after move"
[[ "$(realpath "$target/.config/opencode/cli.json")" == "$checkout/home/.config/opencode/cli.json" ]] \
    || fail "stowed config not relinked after move"
[[ -z "$(find "$target/.agents" "$target/.claude" "$target/.codex" "$target/.config" -xtype l 2>/dev/null)" ]] \
    || fail "dangling links remain after move"

# `check` reports stale links without touching them; install applies the fix.
mv "$checkout" "$scratch/moved checkout 2"
checkout="$scratch/moved checkout 2"
out="$(make -s -C "$checkout" check TARGET="$target" 2>&1 || true)"
grep -q "would remove stale link" <<<"$out" || fail "check did not report stale links"
grep -q "run 'make install' to apply" <<<"$out" || fail "check gave no install hint"
deploy install

# Losing the checkout entirely then re-cloning elsewhere still installs cleanly.
cp -R "$checkout" "$scratch/recloned checkout"
rm -rf "$checkout"
checkout="$scratch/recloned checkout"
deploy install
record_is || fail "repo record not updated after reclone"
[[ "$(realpath "$target/.agents/skills/example")" == "$checkout/global/skills/example" ]] \
    || fail "skill not relinked after reclone"

# A replacement of an installed instruction must not unlink other managed paths.
rm "$target/.codex/AGENTS.md"
printf 'user instructions\n' > "$target/.codex/AGENTS.md"
if deploy install 2>"$scratch/conflict.log"; then
    fail "install accepted conflicting instructions"
fi
grep -qx 'user instructions' "$target/.codex/AGENTS.md" || fail "conflicting file changed"
[[ -L "$target/.agents/skills/example" ]] || fail "instruction conflict unlinked skills"
rm "$target/.codex/AGENTS.md"
deploy install
deploy uninstall
deploy uninstall
[[ ! -L "$target/.config/opencode/cli.json" ]] || fail "stowed config link remains"
for root in "${roots[@]}"; do
    [[ ! -L "$target/$root/skills/example" ]] || fail "managed link remains"
    grep -qx 'local skill' "$target/$root/skills/local/SKILL.md" || fail "local skill lost"
    [[ -L "$target/$root/skills/omarchy" ]] || fail "Omarchy link removed"
done
if make -s -C "$checkout" check TARGET="$scratch/nonexistent" \
    >"$scratch/missing-target.log" 2>&1; then
    fail "check accepted a missing target"
fi
make -s -C "$checkout" uninstall TARGET="$scratch/nonexistent" >/dev/null
[[ ! -e "$scratch/nonexistent" ]] || fail "check or uninstall created the missing target"
echo "Agent Stow deployment test passed"
