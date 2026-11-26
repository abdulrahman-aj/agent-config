#!/usr/bin/env bash
# Peer-side runner for `heavy`, piped to `bash -l -s` inside a `{ ... }` block.
# shellcheck disable=SC2154  # inputs below are prepended as assignments by heavy
#
# Expected shell variables (prepended by heavy as shlex-quoted assignments):
#   mode          "probe" to exit 0/10 after the deny check; empty to run a job
#   mark          per-run protocol prefix (without leading RS or trailing space)
#   id            12-hex staging id under ~/.cache/heavy/work
#   need_git      "1" for a linked worktree (stages common .git under .../git), else ""
#   stage_tree    staging worktree path relative to $HOME
#   stage_gitdir  staged worktree gitdir relative to $HOME (empty for plain repos)
#   stage_cwd     job working directory relative to $HOME
#   lock_dir      slot lock directory (defaults to /tmp/heavy-$(id -u) if empty)
#   grace         seconds between SIGTERM and SIGKILL for the job's process group
#   command       shell command line passed to `bash -c --`
#
# Protocol with heavy:
#   stderr: `\036$mark <event> [value]` lines: ready, slot <n>/<N>, job-done,
#           cleanup-failed <rc>, exit <rc>, denied, prep-failed, lock-failed <path>
#   stdin:  stays open while local heavy lives. After `ready`, heavy runs rsync
#           and writes `go\n`. Later EOF triggers SIGTERM to the job group, and
#           after `exit` the script blocks on EOF so fd 8 stays held for copy-back.
#   fds:    7 drains upload.lock before `ready`; 8 holds per-staging-dir lock
#           until EOF after `exit`; 9 holds the RAM slot lock until after cleanup.
#           Child processes close 8>&- 9>&- so daemons never inherit locks.

is_denied() {
  [ "${AGENT_HEAVY_JOBS:-}" = deny ] && return 0
  XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}" \
    systemctl --user show-environment 2>/dev/null | grep -qx 'AGENT_HEAVY_JOBS=deny' && return 0
  local p
  for p in /usr/lib/systemd/user-environment-generators/30-systemd-environment-d-generator \
           /lib/systemd/user-environment-generators/30-systemd-environment-d-generator; do
    if [ -x "$p" ]; then "$p" 2>/dev/null | grep -qx 'AGENT_HEAVY_JOBS=deny'; return $?; fi
  done
  grep -qxs 'AGENT_HEAVY_JOBS=deny' "${XDG_CONFIG_HOME:-$HOME/.config}"/environment.d/*.conf
}

# Run mark in a subshell so a broken stderr pipe after client SIGKILL cannot
# kill the main shell before .heavy-cleanup finishes.
mark() { (printf '\036%s %s\n' "${mark:-}" "$*" >&2) 8>&- 9>&-; }
pfail() { [ -n "${1:-}" ] && echo "heavy: $1" >&2; mark prep-failed; exit 255; }

if is_denied; then
  [ "${mode:-}" = probe ] || mark denied
  exit 10
fi
[ "${mode:-}" = probe ] && exit 0

set -m  # job control: the job gets its own process group so one kill reaches all of it
root="$HOME/.cache/heavy/work"
case "${id:-}" in ''|*[!0-9a-f]*) pfail ;; esac
for p in "$HOME/.cache" "$HOME/.cache/heavy" "$root" "$root/$id" "$root/$id/tree" \
         "$root/$id/lock" "$root/$id/upload.lock" "$root/$id/run" ${need_git:+"$root/$id/git"}; do
  [ -L "$p" ] && pfail "refusing symlink in staging path: $p"
done
mkdir -p -- "$root/$id/tree" || pfail
if [ -n "${need_git:-}" ]; then mkdir -p -- "$root/$id/git" || pfail; fi
real_home=$(cd -P -- "$HOME" && pwd -P) || pfail
real_root=$(cd -P -- "$root" && pwd -P) || pfail
[ "$real_root" = "$real_home/.cache/heavy/work" ] || pfail "staging root $real_root outside $real_home/.cache/heavy/work"
for sub in tree ${need_git:+git}; do
  real_sub=$(cd -P -- "$root/$id/$sub" && pwd -P) || pfail
  case "$real_sub" in "$real_root"/*) ;; *) pfail "staging path $real_sub outside $real_root" ;; esac
done

# Hold per-staging-dir lock on peer from before rsync until copy-back finishes.
exec 8>"$root/$id/lock" || { mark lock-failed "$root/$id/lock"; exit 255; }
while ! flock -n 8; do
  rc=0; read -r -t 0.5 _ || rc=$?
  [ "$rc" -lt 128 ] && exit 143
done
printf '%s\n' "$mark" > "$root/$id/run" || pfail
# Drain any surviving rsync receiver from a killed prior run before accepting uploads.
exec 7>"$root/$id/upload.lock" || { rm -f "$root/$id/run"; mark lock-failed "$root/$id/upload.lock"; exit 255; }
while ! flock -n 7; do
  rc=0; read -r -t 0.5 _ || rc=$?
  [ "$rc" -lt 128 ] && { rm -f "$root/$id/run"; exit 143; }
done
exec 7>&-
mark ready
read -r go || { rm -f "$root/$id/run"; exit 143; }
rm -f "$root/$id/run"
[ "$go" = go ] || exit 143

stop() {
  stopped=1
  if [ -n "${pid:-}" ]; then
    kill -TERM -- "-$pid" 2>/dev/null
    (sleep "$grace"; kill -KILL -- "-$pid" 2>/dev/null) 8>&- 9>&- >/dev/null 2>&1 &
    timer=$!
  fi
}
trap stop TERM INT HUP
(cat >/dev/null; kill -TERM $$) 8>&- >/dev/null 2>&1 &
watcher=$!
fail() { mark "$@"; kill -- "-$watcher" 2>/dev/null; exit 255; }

tree_path="$HOME/$stage_tree"
if [ -n "${stage_gitdir:-}" ]; then
  gitdir_path="$HOME/$stage_gitdir"
  printf 'gitdir: %s\n' "$gitdir_path" > "$tree_path/.git"
  if [ -f "$gitdir_path/gitdir" ]; then
    printf '%s/.git\n' "$tree_path" > "$gitdir_path/gitdir"
  fi
fi

# One slot per 10 GiB of host RAM (min 1): an 8 GiB VM or heavy build needs ~10 GiB with headroom.
slots=$(awk '/^MemTotal:/ {s = int($2 / 10485760); print (s < 1 ? 1 : s)}' /proc/meminfo 2>/dev/null)
slots=${slots:-1}
lock_dir=${lock_dir:-/tmp/heavy-$(id -u)}
(umask 077; mkdir -p -- "$lock_dir") || fail lock-failed "$lock_dir"
while [ -z "${stopped:-}" ]; do
  for ((slot = 1; slot <= slots; slot++)); do
    # fd 9 holds the slot. Jobs get 8>&- 9>&- so daemons can't inherit either lock.
    exec 9>"$lock_dir/slot-$slot.lock" || fail lock-failed "$lock_dir/slot-$slot.lock"
    flock -n 9 && break 2
  done
  exec 9>&-
  sleep 1
done

if [ -n "${stopped:-}" ]; then
  rc=143
elif is_denied; then
  mark denied; kill -- "-$watcher" 2>/dev/null; exit 10
else
  mark slot "$slot/$slots"
  (cd "$HOME/$stage_cwd" && exec bash -c -- "$command") 8>&- 9>&- </dev/null &
  pid=$!
  [ -n "${stopped:-}" ] && stop  # stop arrived between check and launch
  while :; do
    wait "$pid"; rc=$?
    kill -0 "$pid" 2>/dev/null || break
  done
  kill -TERM -- "-$pid" 2>/dev/null
  for ((i = 0; i < grace * 10; i++)); do kill -0 -- "-$pid" 2>/dev/null || break; sleep 0.1; done
  kill -KILL -- "-$pid" 2>/dev/null
  [ -n "${timer:-}" ] && kill -- "-$timer" 2>/dev/null
  mark job-done
  if [ -f "$tree_path/.heavy-cleanup" ]; then
    (cd "$tree_path" && bash .heavy-cleanup) 8>&- 9>&- </dev/null || mark cleanup-failed $?
  fi
fi
kill -- "-$watcher" 2>/dev/null
exec 9>&-
mark exit "$rc"
cat >/dev/null  # keep fd 8 held until client finishes --out copy-back and closes stdin
exit "$rc"
