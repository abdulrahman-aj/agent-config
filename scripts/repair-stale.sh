#!/usr/bin/env bash
# Keep the deployed tree consistent with the prepared package before Stow runs.
# Removes links left stale by moves, deletions, and unpackaged sources; aborts
# on genuine conflicts instead of letting Stow fail cryptically. Relocation is
# detected via a record outside the checkout, so re-cloning elsewhere works too.
# Usage: repair-stale.sh [--check] TARGET
#        repair-stale.sh record TARGET   - remember this checkout for TARGET
#        repair-stale.sh forget TARGET   - drop the remembered checkout
# In --check mode nothing is changed; pending removals are reported and real
# conflicts still abort. Requires a freshly prepared .stow/home package.
set -euo pipefail
shopt -s nullglob

if [[ "${1:-}" == record ]]; then
    target="$(realpath -m "${2:?target home required}")"
    cache="${XDG_CACHE_HOME:-$HOME/.cache}/agent-config"
    mkdir -p "$cache"
    pwd -P > "$cache/repo.$(printf '%s' "$target" | cksum | cut -d' ' -f1)"
    exit 0
fi
if [[ "${1:-}" == forget ]]; then
    target="$(realpath -m "${2:?target home required}")"
    cache="${XDG_CACHE_HOME:-$HOME/.cache}/agent-config"
    rm -f "$cache/repo.$(printf '%s' "$target" | cksum | cut -d' ' -f1)"
    exit 0
fi

check=0
if [[ "${1:-}" == --check ]]; then
    check=1
    shift
fi
target="$(realpath -m "${1:?target home required}")"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
package="$repo/.stow/home"
record="${XDG_CACHE_HOME:-$HOME/.cache}/agent-config/repo.$(printf '%s' "$target" | cksum | cut -d' ' -f1)"
roots=(.agents .claude .codex .config/opencode)
acted=0
# TARGET paths slated for removal in --check mode (already gone on install).
# The conflict check below must evaluate post-repair state, not pre-repair.
declare -A pending=()

fail() { echo "repair-stale: $*" >&2; exit 1; }
note() { echo "repair-stale: $*"; }

remove_or_report() {  # $1 = link, $2 = reason
    acted=1
    if (( check )); then
        pending["$1"]=1
        note "would remove stale link: $1 ($2)"
    else
        note "removing stale link: $1 ($2)"
        rm -- "$1"
    fi
}

managed_links() {
    local r
    for r in "${roots[@]}"; do
        [[ -d "$target/$r" ]] || continue
        find "$target/$r" -type l -print0
    done
}

# Sources currently packaged, by resolved path.
declare -A packaged=()
while IFS= read -r -d '' alias; do
    [[ -L "$alias" ]] || continue
    # Ghost aliases (source removed) never match a managed link; drop them so
    # a removed shared skill cannot masquerade as a live conflict.
    if [[ ! -e "$alias" ]]; then
        acted=1
        if (( check )); then
            note "would drop stale alias: $alias"
        else
            note "dropping stale alias: $alias"
            rm -- "$alias"
        fi
        continue
    fi
    packaged["$(realpath "$alias")"]=1
done < <(find "$package" -mindepth 1 -print0)

# 1. Relocated checkout: drop links pointing into the previous checkout path.
#    The record lives outside the checkout, so this also covers re-cloning
#    elsewhere after losing the old checkout.
old=""
if [[ -f "$record" ]]; then
    old="$(cat "$record")"
fi
if [[ -n "$old" && "$old" != "$repo" ]]; then
    while IFS= read -r -d '' link; do
        resolved="$(realpath -m "$link")"
        case "$resolved" in
            "$old"/*) remove_or_report "$link" "checkout moved" ;;
        esac
    done < <(managed_links)
fi

# 2. Dangling links pointing into this checkout (removed sources).
while IFS= read -r -d '' link; do
    [[ -e "$link" ]] && continue
    resolved="$(realpath -m "$link")"
    case "$resolved" in
        "$repo"/*) remove_or_report "$link" "source removed" ;;
    esac
done < <(managed_links)

# 3. Refuse on anything else occupying a managed path. Ghost aliases are
#    skipped (dropped above on install; gone on the next prepare on check),
#    as are targets already slated for removal.
while IFS= read -r -d '' alias; do
    [[ -L "$alias" ]] || continue
    [[ -e "$alias" ]] || continue
    counterpart="$target/${alias#"$package"/}"
    [[ -n "${pending[$counterpart]:-}" ]] && continue
    [[ -e "$counterpart" || -L "$counterpart" ]] || continue
    if [[ -L "$counterpart" && "$(realpath -m "$counterpart")" == "$(realpath -m "$alias")" ]]; then
        continue
    fi
    fail "conflicting path: $counterpart (not a managed link). Move it aside and rerun 'make'."
done < <(find "$package" -mindepth 1 -print0)

# 4. Report live links into this repo that nothing packages (e.g. a skill that
#    lost its SKILL.md). Left alone; this only makes the drift visible.
while IFS= read -r -d '' link; do
    [[ -e "$link" ]] || continue
    resolved="$(realpath "$link")"
    case "$resolved" in
        "$repo"/*)
            if [[ -z "${packaged[$resolved]:-}" ]]; then
                note "orphaned link (no longer packaged, left alone): $link"
            fi
            ;;
    esac
done < <(managed_links)

if (( check )) && (( acted )); then
    note "run 'make install' to apply these removals"
fi
