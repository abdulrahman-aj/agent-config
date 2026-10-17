#!/usr/bin/env bash
# Keep the deployed tree consistent with the prepared package before Stow runs.
# Removes links left stale by moves and deletions; aborts
# on genuine conflicts instead of letting Stow fail cryptically. Relocation is
# detected via a record outside the checkout, so re-cloning elsewhere works too.
# Usage: repair-stale.sh [--check] TARGET
#        repair-stale.sh record TARGET   - remember this checkout for TARGET
#        repair-stale.sh forget TARGET   - drop the remembered checkout
# In --check mode nothing is changed; pending removals are reported and real
# conflicts still abort. Requires a freshly prepared .stow/home package.
set -euo pipefail
shopt -s nullglob

record_path() {  # $1 = target home
    local cache="${XDG_CACHE_HOME:-$HOME/.cache}/agent-config"
    printf '%s' "$cache/repo.$(printf '%s' "$1" | cksum | cut -d' ' -f1)"
}

if [[ "${1:-}" == record ]]; then
    target="$(realpath -m "${2:?target home required}")"
    path="$(record_path "$target")"
    mkdir -p "${path%/*}"
    pwd -P > "$path"
    exit 0
fi
if [[ "${1:-}" == forget ]]; then
    target="$(realpath -m "${2:?target home required}")"
    rm -f "$(record_path "$target")"
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
record="$(record_path "$target")"
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

# Drop ghost aliases (source removed). Not optional: without this, Stow -D
# aborts with "unstow_contents() called with non-directory path" (verified by
# disabling this loop and running the suite).
while IFS= read -r -d '' alias; do
    [[ -L "$alias" ]] || continue
    [[ -e "$alias" ]] && continue
    acted=1
    if (( check )); then
        note "would drop stale alias: $alias"
    else
        note "dropping stale alias: $alias"
        rm -- "$alias"
    fi
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

if (( check )) && (( acted )); then
    note "run 'make install' to apply these removals"
fi
