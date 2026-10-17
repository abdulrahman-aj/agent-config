#!/usr/bin/env bash
# Single-hop fan-out links for mappings Stow cannot express (one source, many
# homes): AGENTS.md into every harness, each skill into every skill dir.
# Stowed 1:1 files under home/ are not touched here; the Makefile owns those.
# Stale links come from moves and deletions; relocation is detected via a
# record outside the checkout, so re-cloning elsewhere works too.
# Usage: link-shared.sh clean [--check] TARGET     - drop stale links, refuse conflicts
#        link-shared.sh link [--check] TARGET      - create the fan-out links
#        link-shared.sh uninstall TARGET           - remove the fan-out links
#        link-shared.sh record TARGET              - remember this checkout for TARGET
#        link-shared.sh forget TARGET              - drop the remembered checkout
# In --check mode nothing is changed.
set -euo pipefail

record_path() {  # $1 = target home
    local cache="${XDG_CACHE_HOME:-$HOME/.cache}/agent-config"
    printf '%s' "$cache/repo.$(printf '%s' "$1" | cksum | cut -d' ' -f1)"
}

fail() { echo "link-shared: $*" >&2; exit 1; }
note() { echo "link-shared: $*"; }

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

mode="${1:?usage: link-shared.sh clean|link|uninstall [--check] TARGET}"
check=0
if [[ "${2:-}" == --check ]]; then
    check=1
    shift
fi
target="$(realpath -m "${2:?target home required}")"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
record="$(record_path "$target")"
roots=(.agents .claude .codex .config/opencode)
acted=0
# TARGET paths slated for removal in --check mode (already gone on install).
# The conflict check must evaluate post-clean state, not pre-clean.
declare -A pending=()

# Desired fan-out links: target-relative path, then absolute source.
declare -a dests=() srcs=()
want() { dests+=("$1"); srcs+=("$2"); }
want .agents/AGENTS.md "$repo/AGENTS.md"
want .codex/AGENTS.md "$repo/AGENTS.md"
want .claude/CLAUDE.md "$repo/AGENTS.md"
want .config/opencode/AGENTS.md "$repo/AGENTS.md"
for skill in "$repo"/skills/*; do
    [[ -f "$skill/SKILL.md" ]] || continue
    name="$(basename "$skill")"
    want ".agents/skills/$name" "$skill"
    want ".claude/skills/$name" "$skill"
    want ".config/opencode/skills/$name" "$skill"
done

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

sweep_stale() {
    # 1. Relocated checkout: drop links pointing into the previous path.
    local old=""
    if [[ -f "$record" ]]; then
        old="$(cat "$record")"
    fi
    if [[ -n "$old" && "$old" != "$repo" ]]; then
        while IFS= read -r -d '' link; do
            case "$(realpath -m "$link")" in
                "$old"/*) remove_or_report "$link" "checkout moved" ;;
            esac
        done < <(managed_links)
    fi

    # 2. Dangling links pointing into this checkout (removed sources).
    while IFS= read -r -d '' link; do
        [[ -e "$link" ]] && continue
        case "$(realpath -m "$link")" in
            "$repo"/*) remove_or_report "$link" "source removed" ;;
        esac
    done < <(managed_links)
}

refuse_conflicts() {
    # Anything occupying a desired path that is not already our link aborts,
    # except targets already slated for removal in --check mode.
    local i dest
    for i in "${!dests[@]}"; do
        dest="$target/${dests[$i]}"
        [[ -n "${pending[$dest]:-}" ]] && continue
        [[ -e "$dest" || -L "$dest" ]] || continue
        if [[ -L "$dest" && "$(realpath -m "$dest")" == "${srcs[$i]}" ]]; then
            continue
        fi
        fail "conflicting path: $dest (not a managed link). Move it aside and rerun 'make'."
    done
}

case "$mode" in
clean)
    sweep_stale
    refuse_conflicts
    if (( check )) && (( acted )); then
        note "run 'make install' to apply these removals"
    fi
    ;;
link)
    for i in "${!dests[@]}"; do
        dest="$target/${dests[$i]}"
        expected="$(realpath --relative-to="$(dirname "$dest")" "${srcs[$i]}")"
        if [[ -L "$dest" ]]; then
            [[ "$(realpath -m "$dest")" == "${srcs[$i]}" ]] \
                || fail "conflicting path: $dest (not a managed link). Move it aside and rerun 'make'."
            [[ "$(readlink "$dest")" == "$expected" ]] && continue
            # Same ultimate target, wrong hop (legacy alias farm): normalize.
            if (( check )); then
                note "would relink single-hop: $dest"
                continue
            fi
            note "relinking single-hop: $dest"
            rm -- "$dest"
        fi
        [[ -e "$dest" ]] \
            && fail "conflicting path: $dest (not a managed link). Move it aside and rerun 'make'."
        if (( check )); then
            note "would link: $dest -> ${srcs[$i]}"
        else
            mkdir -p "$(dirname "$dest")"
            ln -sr "${srcs[$i]}" "$dest"
        fi
    done
    ;;
uninstall)
    sweep_stale
    for i in "${!dests[@]}"; do
        dest="$target/${dests[$i]}"
        [[ -L "$dest" ]] || continue
        case "$(realpath -m "$dest")" in
            "$repo"/*) note "removing link: $dest"; rm -- "$dest" ;;
        esac
    done
    ;;
*)
    fail "usage: link-shared.sh clean|link|uninstall [--check] TARGET"
    ;;
esac
