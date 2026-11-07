#!/usr/bin/env python3
"""Behavior tests for the agent-guard hooks, through the config that deploy installs.

Each test installs the hooks into a temporary home with scripts/agent-hooks.py,
then runs the command Claude Code's settings.json or Codex's hooks.json names,
with synthetic hook JSON on stdin, and checks only the decision: blocked, denied
or allowed. One test asks a real Codex whether it trusts the installed hooks.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
AGENT_HOOKS = os.path.join(ROOT, "scripts", "agent-hooks.py")
AGENT_WAIT = os.path.join(ROOT, "home", ".local", "bin", "agent-wait")

DELEGATED = "thread:delegated-task:command%3Amcp%3Aabc%3Adelegate-task%3Adef"
ORCHESTRATOR = "mcp:launch:e71e088f"
USER_HOOK = {"hooks": [{"type": "command", "command": "notify-send done"}]}
# An entry from an earlier install, which kept agent-guard under ~/.claude/hooks.
OLD_GUARD_HOOK = {"hooks": [{"type": "command", "command": "/old/.claude/hooks/agent-guard stop"}]}
# The user's own hook with a similar name: not ours to remove.
LOOKALIKE_HOOK = {"hooks": [{"type": "command", "command": "/h/.local/bin/agent-guardian stop"}]}
CONFIG = {"claude": (".claude", "settings.json"), "codex": (".codex", "hooks.json")}
# Without codex on PATH, install skips asking Codex to trust the hooks.
NO_CODEX_PATH = os.path.dirname(sys.executable) + ":/usr/bin:/bin"


class AgentGuardTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.home)
        bin_dir = os.path.join(self.home, ".local", "bin")
        os.makedirs(bin_dir)
        shutil.copy(os.path.join(ROOT, "home", ".local", "bin", "agent-guard"), bin_dir)
        os.makedirs(os.path.join(self.home, ".claude"))
        self.settings_path = os.path.join(self.home, ".claude", "settings.json")
        with open(self.settings_path, "w") as f:
            json.dump({"theme": "dark", "hooks": {"Stop": [USER_HOOK, OLD_GUARD_HOOK]}}, f)
        os.makedirs(os.path.join(self.home, ".codex"))
        with open(os.path.join(self.home, ".codex", "hooks.json"), "w") as f:
            json.dump({"hooks": {"Stop": [USER_HOOK, OLD_GUARD_HOOK, LOOKALIKE_HOOK]}}, f)
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

    def manage(self, mode, path=NO_CODEX_PATH):
        subprocess.run([sys.executable, AGENT_HOOKS, mode, self.home], check=True,
                       env=dict(os.environ, PATH=path), stdout=subprocess.DEVNULL)

    def settings(self, harness="claude"):
        with open(os.path.join(self.home, *CONFIG[harness])) as f:
            return json.load(f)

    def guard_commands(self, event, harness="claude"):
        return [hook["command"]
                for group in self.settings(harness).get("hooks", {}).get(event, [])
                for hook in group["hooks"]
                if hook not in USER_HOOK["hooks"] + LOOKALIKE_HOOK["hooks"]]

    def fire(self, event, payload, thread=None, entrypoint="t3-code", harness="claude",
             originator="T3 Code", source="vscode"):
        """Run the installed hooks for EVENT; return the decisions they printed.

        Under Codex, the payload's transcript starts with a session_meta line
        from ORIGINATOR and SOURCE, as Codex's rollouts do. Codex inherits the
        Claude Code env of whoever started it, so the entrypoint stays set.
        """
        env = dict(self.env, CLAUDE_CODE_ENTRYPOINT=entrypoint)
        if thread:
            env["T3CODE_THREAD_ID"] = thread
        if harness == "codex":
            transcript = os.path.join(self.home, "rollout.jsonl")
            with open(transcript, "w") as f:
                f.write(json.dumps({"type": "session_meta", "payload": {
                    "originator": originator, "source": source}}) + "\n")
            payload = dict(payload, transcript_path=transcript)
        decisions = []
        for command in self.guard_commands(event, harness):
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

    def ask_denied(self, tool="AskUserQuestion", **kwargs):
        payload = {"hook_event_name": "PreToolUse", "tool_name": tool,
                   "tool_input": {"questions": []}}
        return any(d.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"
                   for d in self.fire("PreToolUse", payload, **kwargs))

    # Settings merge

    def test_install_keeps_user_settings_and_adds_one_copy(self):
        self.assertEqual(self.settings()["theme"], "dark")
        for harness in CONFIG:
            with self.subTest(harness=harness):
                self.assertIn(USER_HOOK, self.settings(harness)["hooks"]["Stop"])
                self.assertNotIn(OLD_GUARD_HOOK, self.settings(harness)["hooks"]["Stop"])
                self.assertEqual(len(self.guard_commands("Stop", harness)), 1)
                self.assertEqual(len(self.guard_commands("PreToolUse", harness)), 1)

    @unittest.skipUnless(shutil.which("codex"), "codex not installed")
    def test_codex_trusts_the_installed_hooks(self):
        self.manage("install", path=os.environ["PATH"])
        self.assertEqual(sorted(codex_hook_trust(self.home).values()), ["trusted", "trusted"])

    def test_user_hook_sharing_a_group_with_ours_survives(self):
        settings = self.settings()
        settings["hooks"]["Stop"][-1]["hooks"].append(USER_HOOK["hooks"][0])
        with open(self.settings_path, "w") as f:
            json.dump(settings, f)
        self.manage("install")
        self.manage("uninstall")
        commands = [h["command"] for g in self.settings()["hooks"]["Stop"] for h in g["hooks"]]
        self.assertEqual(commands, ["notify-send done", "notify-send done"])

    def test_uninstall_removes_only_ours(self):
        self.manage("uninstall")
        self.assertEqual(self.settings(), {"theme": "dark", "hooks": {"Stop": [USER_HOOK]}})
        self.assertEqual(self.settings("codex"), {"hooks": {"Stop": [USER_HOOK, LOOKALIKE_HOOK]}})

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
        self.assertFalse(self.stop_blocks("Which schema?", thread=DELEGATED, harness="codex"))

    def test_codex_blocks_only_in_t3_sessions(self):
        message = "Merged.\n\nShould I start the next PR?"
        codex = dict(harness="codex", thread=ORCHESTRATOR)
        self.assertTrue(self.stop_blocks(message, **codex))
        self.assertFalse(self.stop_blocks(message, active=True, **codex))
        self.assertFalse(self.stop_blocks("Merged #84.", **codex))
        # `codex exec` (even one started inside a T3 session), a plain TUI and a
        # Codex subagent have no picker in Default mode.
        self.assertFalse(self.stop_blocks(message, source="exec", **codex))
        self.assertFalse(self.stop_blocks(message, originator="codex-tui", **codex))
        self.assertFalse(self.stop_blocks(message, source={"subagent": {}}, **codex))

    def test_codex_without_a_transcript_allows(self):
        payload = {"hook_event_name": "Stop", "stop_hook_active": False,
                   "last_assistant_message": "Should I go on?", "transcript_path": None}
        for command in self.guard_commands("Stop", "codex"):
            result = subprocess.run(command, shell=True, input=json.dumps(payload), timeout=30,
                                    env=dict(self.env, T3CODE_THREAD_ID=ORCHESTRATOR),
                                    capture_output=True, text=True)
            self.assertEqual((result.returncode, result.stdout), (0, ""))

    # Pickers

    def test_picker_denied_only_in_delegated_children(self):
        for harness, tool in [("claude", "AskUserQuestion"), ("codex", "request_user_input_async"),
                              ("codex", "request_user_input")]:
            with self.subTest(harness=harness):
                self.assertTrue(self.ask_denied(tool, thread=DELEGATED, harness=harness))
                self.assertFalse(self.ask_denied(tool, thread=ORCHESTRATOR, harness=harness))
                self.assertFalse(self.ask_denied(tool, harness=harness))

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

    def test_codex_child_job_blocks_until_waited(self):
        pid, log = self.start_job(0)
        self.assertTrue(self.stop_blocks("Started.", active=True, thread=DELEGATED, harness="codex"))
        self.agent_wait("--pid", pid, "--log", log)
        self.assertFalse(self.stop_blocks("Passed.", thread=DELEGATED, harness="codex"))

    def test_job_blocks_are_bounded_until_the_agent_waits(self):
        pid, log = self.start_job(30)
        blocks = [self.stop_blocks("Started.", active=True, thread=DELEGATED) for _ in range(9)]
        self.assertEqual(blocks, [True] * 8 + [False])
        self.assertEqual(self.agent_wait("--pid", pid, "--log", log, "--max-seconds", "0").returncode, 124)
        self.assertTrue(self.stop_blocks("Still running.", thread=DELEGATED))

    def test_job_that_ended_unseen_still_blocks(self):
        pid, log = self.start_job(0)
        subprocess.run(["sleep", "0.5"])
        self.assertTrue(self.stop_blocks("Done.", thread=DELEGATED))
        self.assertEqual(self.agent_wait("--pid", pid, "--log", log).returncode, 0)
        self.assertFalse(self.stop_blocks("Done.", thread=DELEGATED))

    def test_malformed_records_do_not_hide_a_job(self):
        self.start_job(30)
        jobs = os.path.join(self.home, "state", "agent-jobs")
        for name, text in [("a.json", '{"owner": "%s"}' % DELEGATED), ("b.json", "[]"), ("c.json", "{")]:
            with open(os.path.join(jobs, name), "w") as f:
                f.write(text)
        self.assertTrue(self.stop_blocks("Started.", thread=DELEGATED))

    def test_a_wait_from_another_thread_does_not_clear_the_job(self):
        pid, log = self.start_job(0)
        self.agent_wait("--pid", pid, "--log", log, thread="thread:delegated-task:other")
        self.assertTrue(self.stop_blocks("Done.", thread=DELEGATED))

    def test_other_threads_jobs_do_not_block(self):
        self.start_job(30, thread="thread:delegated-task:other")
        self.assertFalse(self.stop_blocks("Done.", thread=DELEGATED))

    def test_broken_input_allows(self):
        for command in self.guard_commands("Stop"):
            result = subprocess.run(command, shell=True, input="not json", env=self.env,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual((result.returncode, result.stdout), (0, ""))


def codex_hook_trust(home):
    """Ask a real Codex for each agent-guard hook's trust status, by hook key."""
    server = subprocess.Popen(["codex", "app-server"], stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                              env=dict(os.environ, CODEX_HOME=os.path.join(home, ".codex")))
    try:
        for request_id, method, params in [
                (1, "initialize", {"clientInfo": {"name": "test", "version": "1"}}),
                (2, "hooks/list", {"cwds": [home]})]:
            server.stdin.write(json.dumps({"id": request_id, "method": method,
                                           "params": params}) + "\n")
            server.stdin.flush()
            for line in server.stdout:
                message = json.loads(line)
                if message.get("id") == request_id:
                    break
        return {hook["key"]: hook["trustStatus"] for entry in message["result"]["data"]
                for hook in entry["hooks"] if "/.local/bin/agent-guard " in hook.get("command", "")}
    finally:
        server.stdin.close()
        server.wait(timeout=30)
        server.stdout.close()


if __name__ == "__main__":
    unittest.main(verbosity=1, argv=[sys.argv[0]])
