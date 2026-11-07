#!/usr/bin/env python3
"""Add or remove agent-guard's hooks in TARGET/.claude/settings.json.

Claude Code writes that file itself (theme, /config), so it can't be a stowed
link. Instead this merges our entries in place and leaves every other key and
hook alone. Our entries are found by their command, so reinstalling replaces
them rather than adding copies.
Usage: claude-hooks.py install|uninstall TARGET
"""

import json
import os
import shlex
import sys

MARKER = "/.claude/hooks/agent-guard"


def ours(group):
    return any(MARKER in hook.get("command", "") for hook in group.get("hooks", []))


def wanted(target):
    guard = shlex.quote(os.path.join(target, ".claude", "hooks", "agent-guard"))
    command = lambda mode: {"type": "command", "command": f"{guard} {mode}"}
    return {
        "Stop": {"hooks": [command("stop")]},
        "PreToolUse": {"matcher": "AskUserQuestion", "hooks": [command("ask")]},
    }


def main():
    mode, target = sys.argv[1], os.path.realpath(sys.argv[2])
    path = os.path.join(target, ".claude", "settings.json")
    try:
        with open(path) as f:
            settings = json.load(f)
    except FileNotFoundError:
        if mode == "uninstall":
            return 0
        settings = {}
    hooks = settings.setdefault("hooks", {})
    for event in list(hooks):
        hooks[event] = [group for group in hooks[event] if not ours(group)]
        if not hooks[event]:
            del hooks[event]
    if mode == "install":
        for event, group in wanted(target).items():
            hooks.setdefault(event, []).append(group)
    if not hooks:
        del settings["hooks"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Through a rename, so a running Claude Code never reads half a file.
    with open(path + ".agent-config.tmp", "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    os.replace(path + ".agent-config.tmp", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
