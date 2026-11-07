#!/usr/bin/env python3
"""Behavior tests for the agent-guard hooks, through the settings that deploy installs.

Each test installs the hooks into a temporary home with scripts/claude-hooks.py,
then runs the command the settings name, with synthetic hook JSON on stdin, and
checks only the decision: blocked, denied or allowed.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CLAUDE_HOOKS = os.path.join(ROOT, "scripts", "claude-hooks.py")
AGENT_WAIT = os.path.join(ROOT, "home", ".local", "bin", "agent-wait")

DELEGATED = "thread:delegated-task:command%3Amcp%3Aabc%3Adelegate-task%3Adef"
ORCHESTRATOR = "mcp:launch:e71e088f"
USER_HOOK = {"hooks": [{"type": "command", "command": "notify-send done"}]}


class AgentGuardTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.home)
        hooks_dir = os.path.join(self.home, ".claude", "hooks")
        os.makedirs(hooks_dir)
        shutil.copy(os.path.join(ROOT, "home", ".claude", "hooks", "agent-guard"), hooks_dir)
        self.settings_path = os.path.join(self.home, ".claude", "settings.json")
        with open(self.settings_path, "w") as f:
            json.dump({"theme": "dark", "hooks": {"Stop": [USER_HOOK]}}, f)
        self.manage("install")
        self.manage("install")  # Redeploys must not stack copies.
        self.env = {k: v for k, v in os.environ.items()
                    if k not in ("T3CODE_THREAD_ID", "CLAUDE_CODE_ENTRYPOINT")}
        self.env["XDG_STATE_HOME"] = os.path.join(self.home, "state")
        self.jobs = []

    def tearDown(self):
        for pid in self.jobs:
            try:
                os.killpg(pid, 9)
            except ProcessLookupError:
                pass

    def manage(self, mode):
        subprocess.run([sys.executable, CLAUDE_HOOKS, mode, self.home], check=True)

    def settings(self):
        with open(self.settings_path) as f:
            return json.load(f)

    def guard_commands(self, event):
        return [hook["command"] for group in self.settings().get("hooks", {}).get(event, [])
                for hook in group["hooks"] if hook not in USER_HOOK["hooks"]]

    def fire(self, event, payload, thread=None, entrypoint="t3-code"):
        """Run the installed hooks for EVENT; return the decisions they printed."""
        env = dict(self.env, CLAUDE_CODE_ENTRYPOINT=entrypoint)
        if thread:
            env["T3CODE_THREAD_ID"] = thread
        decisions = []
        for command in self.guard_commands(event):
            result = subprocess.run(command, shell=True, input=json.dumps(payload), env=env,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            if result.stdout.strip():
                decisions.append(json.loads(result.stdout))
        return decisions

    def stop_blocks(self, message, active=False, **kwargs):
        payload = {"hook_event_name": "Stop", "stop_hook_active": active,
                   "last_assistant_message": message}
        return any(d.get("decision") == "block" for d in self.fire("Stop", payload, **kwargs))

    def ask_denied(self, **kwargs):
        payload = {"hook_event_name": "PreToolUse", "tool_name": "AskUserQuestion",
                   "tool_input": {"questions": []}}
        return any(d.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
                   for d in self.fire("PreToolUse", payload, **kwargs))

    # Settings merge

    def test_install_keeps_user_settings_and_adds_one_copy(self):
        settings = self.settings()
        self.assertEqual(settings["theme"], "dark")
        self.assertIn(USER_HOOK, settings["hooks"]["Stop"])
        self.assertEqual(len(self.guard_commands("Stop")), 1)
        self.assertEqual(len(self.guard_commands("PreToolUse")), 1)

    def test_uninstall_removes_only_ours(self):
        self.manage("uninstall")
        self.assertEqual(self.settings(), {"theme": "dark", "hooks": {"Stop": [USER_HOOK]}})

    # Prose questions (top-level sessions)

    def test_final_question_blocks_once(self):
        message = "I merged #84.\n\nShould I start the audit PR now?"
        self.assertTrue(self.stop_blocks(message, thread=ORCHESTRATOR))
        self.assertTrue(self.stop_blocks(message))  # Outside T3 too.
        self.assertTrue(self.stop_blocks("Done. Want me to open the PR?", entrypoint="cli"))
        self.assertFalse(self.stop_blocks(message, active=True, thread=ORCHESTRATOR))

    def test_statements_and_quoted_questions_pass(self):
        for message in [
            "I merged #84 and started the audit PR.",
            "Fixed it.\n\n```python\nwhy = input('Why?')\n```",
            "The user asked:\n\n> Should we ship it?",
            "Its help text reads \"Is the VM up?\" now.",
            "Use `fleet-run host -- cmd?` for that.",
            "See https://example.com/search?q=t3 for details.",
            "Should I wait? No: I started both.\n\nPR #85 is open and CI is running.",
            "",
        ]:
            with self.subTest(message=message):
                self.assertFalse(self.stop_blocks(message, thread=ORCHESTRATOR))

    def test_sessions_without_the_picker_pass(self):
        self.assertFalse(self.stop_blocks("Should I continue?", entrypoint="sdk-cli"))

    def test_delegated_children_may_end_on_a_question(self):
        self.assertFalse(self.stop_blocks("Which schema should I use?", thread=DELEGATED))

    # Pickers

    def test_picker_denied_only_in_delegated_children(self):
        self.assertTrue(self.ask_denied(thread=DELEGATED))
        self.assertFalse(self.ask_denied(thread=ORCHESTRATOR))
        self.assertFalse(self.ask_denied())

    # Unwaited jobs (delegated children)

    def agent_wait(self, *argv, thread=DELEGATED):
        env = dict(self.env, T3CODE_THREAD_ID=thread)
        return subprocess.run([AGENT_WAIT, *argv], env=env, capture_output=True, text=True,
                              timeout=60)

    def start_job(self, seconds, thread=DELEGATED):
        log = os.path.join(self.home, "job.log")
        started = self.agent_wait("--start", "--log", log, "--", "sleep", str(seconds),
                                  thread=thread)
        pid = int(started.stdout)
        self.jobs.append(pid)
        return str(pid), log

    def test_running_job_blocks_until_a_wait_sees_it_end(self):
        pid, log = self.start_job(2)
        # Even when Claude is already continuing from a block: waiting lifts it.
        self.assertTrue(self.stop_blocks("Job started; I'll report.", active=True, thread=DELEGATED))
        self.assertEqual(self.agent_wait("--pid", pid, "--log", log, "--max-seconds", "0").returncode, 124)
        self.assertTrue(self.stop_blocks("Still running.", thread=DELEGATED))
        self.assertEqual(self.agent_wait("--pid", pid, "--log", log).returncode, 0)
        self.assertFalse(self.stop_blocks("The build passed.", thread=DELEGATED))

    def test_job_that_ended_unseen_still_blocks(self):
        pid, log = self.start_job(0)
        subprocess.run(["sleep", "0.5"])
        self.assertTrue(self.stop_blocks("Done.", thread=DELEGATED))
        self.assertEqual(self.agent_wait("--pid", pid, "--log", log).returncode, 0)
        self.assertFalse(self.stop_blocks("Done.", thread=DELEGATED))

    def test_other_threads_jobs_do_not_block(self):
        self.start_job(30, thread="thread:delegated-task:other")
        self.assertFalse(self.stop_blocks("Done.", thread=DELEGATED))

    def test_broken_input_allows(self):
        for command in self.guard_commands("Stop"):
            result = subprocess.run(command, shell=True, input="not json", env=self.env,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual((result.returncode, result.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main(verbosity=1, argv=[sys.argv[0]])
