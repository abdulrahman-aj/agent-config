#!/usr/bin/env bash
# Deploy from a pinned checkout of origin/main, so branches in the dev checkout
# never change what running agents load.
# Usage: deploy.sh DEPLOY_DIR TARGET [HOST]
set -euo pipefail

dir="${1:?deploy dir required}"
target="${2:?target home required}"
host="${3:-}"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
fail() { echo "deploy: $*" >&2; exit 1; }

if [[ ! -e "$dir" ]]; then
    git clone --quiet "$(git -C "$repo" remote get-url origin)" "$dir"
fi
[[ -d "$dir/.git" ]] || fail "$dir exists but isn't a git checkout"
git -C "$dir" fetch --quiet origin
# Edits in the pinned checkout would be live and unreviewed; refuse rather than
# carry them over or discard them.
[[ -z "$(git -C "$dir" status --porcelain)" ]] \
    || fail "$dir has local changes; commit them through a PR instead"
git -C "$dir" switch --quiet --detach origin/main
echo "deploy: $dir at $(git -C "$dir" log -1 --format='%h %s')"
make -s -C "$dir" install TARGET="$target" DEPLOY_DIR="$dir" HOST="$host"
