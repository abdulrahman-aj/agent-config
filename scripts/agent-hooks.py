#!/usr/bin/env python3
"""Add or remove agent-guard's hooks in Claude Code's and Codex's hook config.

Claude Code: TARGET/.claude/settings.json. Codex: TARGET/.codex/hooks.json, which
uses the same shape. Both files may hold the user's own settings and hooks
(Claude Code writes settings.json itself), so they can't be stowed links;
instead this merges our entries in place and leaves everything else alone. Our
entries are found by their command, so reinstalling replaces them rather than
adding copies.

Codex runs a user hook only after the user trusts its exact definition. On
install this asks Codex itself (`codex app-server`: hooks/list, then
config/batchWrite) to trust our hooks, as its TUI does after a review, so the
trust lands in TARGET/.codex/config.toml in Codex's own format. Without codex
on PATH that step is skipped; the TUI then asks at startup.
Usage: agent-hooks.py install|uninstall TARGET
"""

import json
import os
import shlex
import shutil
import subprocess
import sys

MARKER = "/.claude/hooks/agent-guard"
# The picker tools each harness offers. Codex's T3 sessions offer
# request_user_input_async; its Plan mode offers request_user_input.
PICKERS = {"claude": "AskUserQuestion", "codex": "request_user_input|request_user_input_async"}
FILES = {"claude": (".claude", "settings.json"), "codex": (".codex", "hooks.json")}


def ours(hook):
    return MARKER in hook.get("command", "")


def wanted(target, harness):
    guard = shlex.quote(os.path.join(target, ".claude", "hooks", "agent-guard"))
    command = lambda mode: {"type": "command", "command": f"{guard} {mode} {harness}"}
    return {
        "Stop": {"hooks": [command("stop")]},
        "PreToolUse": {"matcher": PICKERS[harness], "hooks": [command("ask")]},
    }


def merge(mode, target, harness):
    path = os.path.join(target, *FILES[harness])
    try:
        with open(path) as f:
            settings = json.load(f)
    except FileNotFoundError:
        if mode == "uninstall":
            return
        settings = {}
    except ValueError as error:
        sys.exit(f"agent-hooks: {path} isn't valid JSON ({error}); fix it and rerun.")
    hooks = settings.setdefault("hooks", {})
    # Drop our hooks one by one, so a user hook sharing a group with ours stays.
    for event in list(hooks):
        for group in hooks[event]:
            group["hooks"] = [hook for hook in group.get("hooks", []) if not ours(hook)]
        hooks[event] = [group for group in hooks[event] if group["hooks"]]
        if not hooks[event]:
            del hooks[event]
    if mode == "install":
        # Appended last: Codex keys hook trust by position, so the user's
        # hooks keep their keys across our reinstalls.
        for event, group in wanted(target, harness).items():
            hooks.setdefault(event, []).append(group)
    if not hooks:
        del settings["hooks"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Through a rename, so a running harness never reads half a file.
    with open(path + ".agent-config.tmp", "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    os.replace(path + ".agent-config.tmp", path)


def trust_codex_hooks(target):
    codex = shutil.which("codex")
    if not codex:
        print("agent-hooks: codex not found; Codex will ask to trust the hooks at startup")
        return
    env = dict(os.environ, CODEX_HOME=os.path.join(target, ".codex"))
    # stderr is Codex's own logging; failures come back as JSON-RPC errors.
    server = subprocess.Popen([codex, "app-server"], env=env, stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

    def call(request_id, method, params):
        server.stdin.write(json.dumps({"id": request_id, "method": method, "params": params}) + "\n")
        server.stdin.flush()
        for line in server.stdout:
            message = json.loads(line)
            if message.get("id") == request_id:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message["result"]
        raise RuntimeError(f"{method}: codex app-server exited")

    try:
        call(1, "initialize", {"clientInfo": {"name": "agent-config", "version": "1"}})
        server.stdin.write(json.dumps({"method": "initialized"}) + "\n")
        listed = call(2, "hooks/list", {"cwds": [target]})["data"]
        trust = {hook["key"]: {"trusted_hash": hook["currentHash"]}
                 for entry in listed for hook in entry["hooks"]
                 if ours(hook) and hook["trustStatus"] in ("untrusted", "modified")}
        if trust:
            call(3, "config/batchWrite", {"edits": [
                {"keyPath": "hooks.state", "value": trust, "mergeStrategy": "upsert"}]})
    finally:
        server.stdin.close()
        server.wait(timeout=30)
        server.stdout.close()


def main():
    mode, target = sys.argv[1], os.path.realpath(sys.argv[2])
    for harness in FILES:
        merge(mode, target, harness)
    if mode == "install":
        trust_codex_hooks(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
