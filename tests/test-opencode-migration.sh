#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
checkout="$scratch/agent config"
legacy="$scratch/old dotfiles"
target="$scratch/home with spaces"

fail() { echo "FAIL: $*" >&2; exit 1; }
migrate() {
    make -s -C "$checkout" migrate-opencode TARGET="$target" DOTFILES_DIR="$legacy" "$@" \
        >"$scratch/migration.log" 2>&1
}
assert_legacy_links() {
    local config relative
    while IFS= read -r -d '' config; do
        relative="${config#"$checkout/opencode/"}"
        [[ "$(realpath -m "$target/.config/opencode/$relative")" \
            == "$legacy/home/.config/opencode/$relative" ]] \
            || fail "legacy link changed after failed migration: $relative"
    done < <(find "$checkout/opencode" -type f -print0)
}

mkdir -p "$checkout/scripts" "$legacy/home/.config" "$target/.codex"
cp "$repo/Makefile" "$checkout/"
cp "$repo/scripts/prepare-stow.sh" "$repo/scripts/migrate-opencode.sh" "$checkout/scripts/"
cp -R "$repo/opencode" "$checkout/opencode"
cp -R "$repo/opencode" "$legacy/home/.config/opencode"
printf 'instructions\n' > "$checkout/AGENTS.md"
stow --no-folding -d "$legacy" -t "$target" home
printf 'local runtime data\n' > "$target/.config/opencode/local-data.json"

# Failure elsewhere in the install restores all old OpenCode links.
printf 'local instructions\n' > "$target/.codex/AGENTS.md"
if migrate; then fail "migration accepted conflicting instructions"; fi
assert_legacy_links
grep -qx 'local instructions' "$target/.codex/AGENTS.md" || fail "local instructions changed"
rm "$target/.codex/AGENTS.md"

# Edited dotfiles sources must be reconciled, never silently discarded.
printf '\nmodified\n' >> "$legacy/home/.config/opencode/cli.json"
if migrate; then fail "migration accepted changed dotfiles content"; fi
assert_legacy_links
cp "$checkout/opencode/cli.json" "$legacy/home/.config/opencode/cli.json"

# A local replacement also prevents the handoff without unlinking the other files.
rm "$target/.config/opencode/cli.json"
printf 'local config\n' > "$target/.config/opencode/cli.json"
if migrate; then fail "migration replaced a local config"; fi
grep -qx 'local config' "$target/.config/opencode/cli.json" || fail "local config changed"
rm "$target/.config/opencode/cli.json"
ln -s "$legacy/home/.config/opencode/cli.json" "$target/.config/opencode/cli.json"
assert_legacy_links

# A late failure must undo links installed before Stow reported failure too.
cat > "$scratch/failing-stow" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
stow "$@"
for argument in "$@"; do
    [[ "$argument" != -S ]] || exit 1
done
EOF
chmod +x "$scratch/failing-stow"
if migrate STOW="$scratch/failing-stow"; then fail "late install failure was ignored"; fi
assert_legacy_links

# Support upgrading dotfiles first, leaving a recognized dangling link behind.
rm "$legacy/home/.config/opencode/opencode.jsonc"
migrate || { cat "$scratch/migration.log" >&2; fail "migration failed"; }
migrate || { cat "$scratch/migration.log" >&2; fail "repeated migration failed"; }
while IFS= read -r -d '' config; do
    relative="${config#"$checkout/opencode/"}"
    [[ "$(realpath "$target/.config/opencode/$relative")" == "$config" ]] \
        || fail "config was not handed off: $relative"
done < <(find "$checkout/opencode" -type f -print0)
grep -qx 'local runtime data' "$target/.config/opencode/local-data.json" \
    || fail "local runtime data changed"
echo "OpenCode migration test passed"
