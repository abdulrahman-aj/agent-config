#!/usr/bin/env python3
"""Behavior tests for home/.local/bin/leak-check and its git/Claude hooks."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEAK_CHECK = os.path.join(REPO_ROOT, "home", ".local", "bin", "leak-check")
GIT_CONFIG = os.path.join(REPO_ROOT, "home", ".config", "git", "config")

FAKE_GH = """\
#!/usr/bin/env python3
import json, os, sys

if os.environ.get("FAKE_GH_FAIL") == "1":
    print("simulated gh failure", file=sys.stderr)
    sys.exit(1)

with open(os.environ["FAKE_GH_FIXTURE"], "r", encoding="utf-8") as f:
    data = json.load(f)

args = sys.argv[1:]
if len(args) >= 2 and args[0] == "api" and args[1].startswith("repos/"):
    vis = data.get("visibility", {}).get(args[1][len("repos/"):])
    if vis is None:
        sys.exit(1)
    print(vis)
    sys.exit(0)
if len(args) >= 3 and args[0] == "repo" and args[1] == "list":
    for name in data.get("private", {}).get(args[2], []):
        print(name)
    sys.exit(0)
sys.exit(1)
"""

# Redirects git-receive-pack / git-upload-pack to a local bare repo so git push uses a GitHub URL.
FAKE_SSH = """\
#!/usr/bin/env python3
import os, subprocess, sys

cmd, bare = sys.argv[-1], os.environ["TEST_BARE_REPO"]
if "git-receive-pack" in cmd:
    sys.exit(subprocess.call(["git-receive-pack", bare]))
if "git-upload-pack" in cmd:
    sys.exit(subprocess.call(["git-upload-pack", bare]))
sys.exit(1)
"""

FIXTURE = {
    "visibility": {"alice/public-repo": "public", "alice/private-repo": "private"},
    "private": {"alice": ["secret-thing", "hidden_proj", "alpha.beta"]},
}


class LeakCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = os.path.join(self.tmp.name, "home")
        self.bin_dir = os.path.join(self.tmp.name, "fake-bin")
        os.makedirs(os.path.join(self.home, ".local", "bin"))
        os.makedirs(os.path.join(self.home, ".config", "git"))
        os.makedirs(self.bin_dir)
        os.symlink(LEAK_CHECK, os.path.join(self.home, ".local", "bin", "leak-check"))
        os.symlink(GIT_CONFIG, os.path.join(self.home, ".config", "git", "config"))

        self.fixture_path = os.path.join(self.tmp.name, "gh-fixture.json")
        with open(self.fixture_path, "w", encoding="utf-8") as f:
            json.dump(FIXTURE, f)

        for path, body in [
            (os.path.join(self.bin_dir, "gh"), FAKE_GH),
            (os.path.join(self.tmp.name, "fake-ssh"), FAKE_SSH),
        ]:
            with open(path, "w", encoding="utf-8") as f:
                f.write(body)
            os.chmod(path, 0o755)
        self.fake_ssh = os.path.join(self.tmp.name, "fake-ssh")

    def tearDown(self):
        self.tmp.cleanup()

    def base_env(self, extra=None):
        env = {
            **os.environ,
            "HOME": self.home,
            "XDG_CONFIG_HOME": os.path.join(self.home, ".config"),
            "XDG_CACHE_HOME": os.path.join(self.home, ".cache"),
            "PATH": f"{self.bin_dir}:{os.path.join(self.home, '.local', 'bin')}:{os.environ.get('PATH', '')}",
            "FAKE_GH_FIXTURE": self.fixture_path,
            "GIT_CONFIG_NOSYSTEM": "1",
        }
        for key in ("LEAK_CHECK_SKIP", "FAKE_GH_FAIL", "GH_REPO"):
            env.pop(key, None)
        if extra:
            env.update(extra)
        return env

    def run_cli(self, args, stdin_text="", extra_env=None):
        return subprocess.run(
            [sys.executable, LEAK_CHECK, *args],
            input=stdin_text,
            capture_output=True,
            text=True,
            env=self.base_env(extra_env),
            timeout=30,
        )

    def run_claude_hook(self, command, cwd=None, extra_env=None):
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": cwd or self.tmp.name})
        return self.run_cli(["--claude-hook"], stdin_text=payload, extra_env=extra_env)

    def make_repo_pair(self, name, remote_url):
        bare = os.path.join(self.tmp.name, f"{name}-bare.git")
        work = os.path.join(self.tmp.name, f"{name}-work")
        env = self.base_env({"TEST_BARE_REPO": bare, "GIT_SSH_COMMAND": self.fake_ssh})
        subprocess.run(["git", "init", "--bare", "-b", "main", bare], env=env, check=True, capture_output=True)
        subprocess.run(["git", "init", "-b", "main", work], env=env, check=True, capture_output=True)
        subprocess.run(["git", "-C", work, "config", "user.email", "test@example.com"], env=env, check=True)
        subprocess.run(["git", "-C", work, "config", "user.name", "Test User"], env=env, check=True)
        subprocess.run(["git", "-C", work, "remote", "add", "origin", remote_url], env=env, check=True)
        return work, bare, env

    def commit_file(self, work, env, relpath, content, message):
        with open(os.path.join(work, relpath), "w", encoding="utf-8") as f:
            f.write(content)
        subprocess.run(["git", "-C", work, "add", relpath], env=env, check=True, capture_output=True)
        subprocess.run(["git", "-C", work, "commit", "-m", message], env=env, check=True, capture_output=True)

    def bare_has(self, bare, ref, env):
        return subprocess.run(["git", "-C", bare, "show-ref", "--verify", ref], env=env, capture_output=True).returncode == 0

    def test_boundaries_terms_file_and_cache(self):
        for text in ["~/Work/secret-thing/.git", "foo_secret-thing_bar", "SECRET-THING.md", "dir/alpha.beta/x"]:
            self.assertNotEqual(self.run_cli(["alice/public-repo"], text).returncode, 0)
        for text in ["just thing", "mysecret-thing", "secret-thing2", "clean text"]:
            self.assertEqual(self.run_cli(["alice/public-repo"], text).returncode, 0)
        self.assertEqual(self.run_cli(["alice/private-repo"], "secret-thing").returncode, 0)

        # Extra terms file supports comments and !exclusions.
        terms_dir = os.path.join(self.home, ".config", "leak-check")
        os.makedirs(terms_dir, exist_ok=True)
        with open(os.path.join(terms_dir, "terms"), "w", encoding="utf-8") as f:
            f.write("# comment\ncodename-orchid\n!hidden_proj\n")
        self.assertNotEqual(self.run_cli(["alice/public-repo"], "codename-orchid").returncode, 0)
        self.assertEqual(self.run_cli(["alice/public-repo"], "hidden_proj").returncode, 0)

        # Cached visibility and private list survive a subsequent gh failure.
        self.assertNotEqual(
            self.run_cli(["alice/public-repo"], "secret-thing", extra_env={"FAKE_GH_FAIL": "1"}).returncode, 0
        )

    def test_public_push_refused_for_message_and_added_line(self):
        work, bare, env = self.make_repo_pair("msg", "git@github.com:alice/public-repo.git")
        self.commit_file(work, env, "notes.txt", "clean\n", "mentions secret-thing")
        self.assertNotEqual(subprocess.run(["git", "-C", work, "push", "origin", "main"], env=env, capture_output=True).returncode, 0)
        self.assertFalse(self.bare_has(bare, "refs/heads/main", env))

        work2, bare2, env2 = self.make_repo_pair("line", "git@github.com:alice/public-repo.git")
        self.commit_file(work2, env2, "notes.txt", "see ~/Work/secret-thing/.git\n", "clean message")
        self.assertNotEqual(subprocess.run(["git", "-C", work2, "push", "origin", "main"], env=env2, capture_output=True).returncode, 0)
        self.assertFalse(self.bare_has(bare2, "refs/heads/main", env2))

    def test_private_push_clean_push_deletion_and_local_hook(self):
        priv_work, priv_bare, priv_env = self.make_repo_pair("priv", "git@github.com:alice/private-repo.git")
        self.commit_file(priv_work, priv_env, "notes.txt", "secret-thing\n", "secret-thing")
        self.assertEqual(subprocess.run(["git", "-C", priv_work, "push", "origin", "main"], env=priv_env, capture_output=True).returncode, 0)
        self.assertTrue(self.bare_has(priv_bare, "refs/heads/main", priv_env))

        work, bare, env = self.make_repo_pair("pub", "git@github.com:alice/public-repo.git")
        marker = os.path.join(self.tmp.name, "local-hook-ran")
        local_hook = os.path.join(work, ".git", "hooks", "pre-push")
        with open(local_hook, "w", encoding="utf-8") as f:
            f.write(f"#!/bin/sh\ntouch '{marker}'\n")
        os.chmod(local_hook, 0o755)

        self.commit_file(work, env, "notes.txt", "clean\n", "clean")
        self.assertEqual(subprocess.run(["git", "-C", work, "push", "origin", "main"], env=env, capture_output=True).returncode, 0)
        self.assertTrue(self.bare_has(bare, "refs/heads/main", env))
        self.assertTrue(os.path.exists(marker))

        # Branch deletion pushes nothing to scan and passes even when gh fails.
        subprocess.run(["git", "-C", work, "checkout", "-b", "temp"], env=env, check=True, capture_output=True)
        self.assertEqual(subprocess.run(["git", "-C", work, "push", "origin", "temp"], env=env, capture_output=True).returncode, 0)
        self.assertEqual(
            subprocess.run(["git", "-C", work, "push", "origin", "--delete", "temp"], env={**env, "FAKE_GH_FAIL": "1"}, capture_output=True).returncode,
            0,
        )
        self.assertFalse(self.bare_has(bare, "refs/heads/temp", env))

    def test_already_pushed_leak_is_not_rescanned_and_non_github_skipped(self):
        work, _, env = self.make_repo_pair("existing", "git@github.com:alice/public-repo.git")
        self.commit_file(work, env, "notes.txt", "secret-thing\n", "initial leak")
        self.assertEqual(
            subprocess.run(["git", "-C", work, "push", "origin", "main"], env={**env, "LEAK_CHECK_SKIP": "1"}, capture_output=True).returncode,
            0,
        )
        self.commit_file(work, env, "notes.txt", "clean now\n", "remove leak")
        self.assertEqual(subprocess.run(["git", "-C", work, "push", "origin", "main"], env=env, capture_output=True).returncode, 0)

        bare = os.path.join(self.tmp.name, "direct-bare.git")
        local_work, _, local_env = self.make_repo_pair("direct", bare)
        self.commit_file(local_work, local_env, "notes.txt", "secret-thing\n", "secret-thing")
        self.assertEqual(
            subprocess.run(["git", "-C", local_work, "push", "origin", "main"], env={**local_env, "FAKE_GH_FAIL": "1"}, capture_output=True).returncode,
            0,
        )

    def test_claude_hook_body_file_and_command_substitution(self):
        work, _, _ = self.make_repo_pair("claude", "https://github.com/alice/public-repo.git")
        dirty = os.path.join(self.tmp.name, "dirty.md")
        clean = os.path.join(self.tmp.name, "clean.md")
        with open(dirty, "w", encoding="utf-8") as f:
            f.write("Evidence from secret-thing.\n")
        with open(clean, "w", encoding="utf-8") as f:
            f.write("Generic evidence.\n")

        self.assertEqual(self.run_claude_hook(f"gh pr create --title Fix --body-file {dirty}", cwd=work).returncode, 2)
        self.assertEqual(self.run_claude_hook(f"gh pr create --title Fix --body-file {clean}", cwd=work).returncode, 0)
        self.assertEqual(self.run_claude_hook(f'gh pr create --title Fix --body "$(cat {dirty})"', cwd=work).returncode, 2)
        self.assertEqual(
            self.run_claude_hook(f"gh api repos/alice/public-repo/issues/1/comments -F body=@{dirty}").returncode,
            2,
        )
        self.assertEqual(
            self.run_claude_hook(f"gh pr create -R alice/private-repo --body-file {dirty}").returncode,
            0,
        )
        self.assertEqual(
            self.run_claude_hook("echo secret-thing", cwd=work, extra_env={"FAKE_GH_FAIL": "1"}).returncode,
            0,
        )

    def test_gh_failure_fails_closed_and_skip_overrides(self):
        self.assertNotEqual(self.run_cli(["alice/public-repo"], "clean", extra_env={"FAKE_GH_FAIL": "1"}).returncode, 0)
        self.assertEqual(
            self.run_cli(["alice/public-repo"], "secret-thing", extra_env={"FAKE_GH_FAIL": "1", "LEAK_CHECK_SKIP": "1"}).returncode,
            0,
        )

        work, bare, env = self.make_repo_pair("fail", "git@github.com:alice/public-repo.git")
        self.commit_file(work, env, "notes.txt", "clean\n", "clean")
        self.assertNotEqual(
            subprocess.run(["git", "-C", work, "push", "origin", "main"], env={**env, "FAKE_GH_FAIL": "1"}, capture_output=True).returncode,
            0,
        )
        self.assertFalse(self.bare_has(bare, "refs/heads/main", env))
        self.assertEqual(
            subprocess.run(
                ["git", "-C", work, "push", "origin", "main"],
                env={**env, "FAKE_GH_FAIL": "1", "LEAK_CHECK_SKIP": "1"},
                capture_output=True,
            ).returncode,
            0,
        )
        self.assertTrue(self.bare_has(bare, "refs/heads/main", env))

        self.assertEqual(
            self.run_claude_hook("gh pr create --title Clean --body Clean", cwd=work, extra_env={"FAKE_GH_FAIL": "1"}).returncode,
            2,
        )
        self.assertEqual(
            self.run_claude_hook(
                "gh pr create --title secret-thing",
                cwd=work,
                extra_env={"FAKE_GH_FAIL": "1", "LEAK_CHECK_SKIP": "1"},
            ).returncode,
            0,
        )


if __name__ == "__main__":
    unittest.main()
