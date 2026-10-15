#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target="$(realpath -m "${1:?target home required}")"
dotfiles="$(realpath -m "${2:?dotfiles checkout required}")"
paths=()
links=()
sources=()

# Only relinquish known dotfiles links; preserve local replacements and edited sources.
while IFS= read -r -d '' config; do
    relative="${config#"$repo/opencode/"}"
    destination="$target/.config/opencode/$relative"
    legacy="$dotfiles/home/.config/opencode/$relative"
    [[ -e "$destination" || -L "$destination" ]] || continue
    [[ "$(realpath -m "$destination")" != "$config" ]] || continue
    if [[ ! -L "$destination" || "$(realpath -m "$destination")" != "$legacy" ]]; then
        echo "Refusing to replace unmanaged OpenCode config: $destination" >&2
        exit 1
    fi
    if [[ -e "$legacy" ]] && ! cmp -s "$config" "$legacy"; then
        echo "OpenCode source differs; reconcile it before migrating: $legacy" >&2
        exit 1
    fi
    paths+=("$destination")
    links+=("$(readlink "$destination")")
    sources+=("$config")
done < <(find "$repo/opencode" -type f -print0)

restore_links() {
    local index
    for index in "${!paths[@]}"; do
        if [[ -L "${paths[index]}" \
            && "$(realpath -m "${paths[index]}")" == "${sources[index]}" ]]; then
            rm -- "${paths[index]}"
        fi
        if [[ ! -e "${paths[index]}" && ! -L "${paths[index]}" ]]; then
            mkdir -p "$(dirname "${paths[index]}")"
            ln -s -- "${links[index]}" "${paths[index]}"
        fi
    done
}
trap restore_links EXIT
for path in "${paths[@]}"; do
    rm -- "$path"
done
make -C "$repo" install TARGET="$target"
trap - EXIT
echo "OpenCode configuration is now managed by agent-config"
