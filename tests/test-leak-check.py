#!/usr/bin/env python3
"""Behavior tests for home/.local/bin/leak-check and its git/Claude hooks."""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEAK_CHECK = os.path.join(REPO_ROOT, "home", ".local", "bin", "leak-check")
GIT_CONFIG = os.path.join(REPO_ROOT, "home", ".config", "git", "config")

# Fake gh script backed by a JSON fixture file (FAKE_GH_FIXTURE) and optional FAKE_GH_FAIL=1.
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
    repo = args[1][len("repos/"):]
    vis = data.get("visibility", {}).get(repo)
    if vis is None:
        print(f"not found: {repo}", file=sys.stderr)
        sys.exit(1)
    print(vis)
    sys.exit(0)

if len(args) >= 3 and args[0] == "repo" and args[1] == "list":
    owner = args[2]
    for name in data.get("private", {}).get(owner, []):
        print(name)
    sys.exit(0)

print(f"unexpected gh invocation: {args}", file=sys.stderr)
sys.exit(1)
"""

# Fake ssh wrapper that redirects git-receive-pack / git-upload-pack to a local bare repo,
# letting real git push use a GitHub SSH remote URL end-to-end.
FAKE_SSH = """\
#!/usr/bin/env python3
import os, subprocess, sys

cmd = sys.argv[-1]
bare = os.environ["TEST_BARE_REPO"]
if "git-receive-pack" in cmd:
    sys.exit(subprocess.call(["git-receive-pack", bare]))
if "git-upload-pack" in cmd:
    sys.exit(subprocess.call(["git-upload-pack", bare]))
sys.exit(1)
"""

FIXTURE = {
    "visibility": {
        "alice/public-repo": "public",
        "alice/private-repo": "private",
    },
    "private": {
        "alice": ["secret-thing", "hidden_proj", "alpha.beta"],
    },
}


class LeakCheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = os.path.join(self.tmp.name, "home")
        self.bin_dir = os.path.join(self.tmp.name, "fake-bin")
        os.makedirs(os.path.join(self.home, ".local", "bin"))
        os.makedirs(os.path.join(self.home, ".config", "git"))
        os.makedirs(self.bin_dir)

        # Install leak-check and git config into the throwaway HOME just like stow does.
        os.symlink(LEAK_CHECK, os.path.join(self.home, ".local", "bin", "leak-check"))
        os.symlink(GIT_CONFIG, os.path.join(self.home, ".config", "git", "config"))

        self.fixture_path = os.path.join(self.tmp.name, "gh-fixture.json")
        with open(self.fixture_path, "w", encoding="utf-8") as f:
            json.dump(FIXTURE, f)

        fake_gh = os.path.join(self.bin_dir, "gh")
        with open(fake_gh, "w", encoding="utf-8") as f:
            f.write(FAKE_GH)
        os.chmod(fake_gh, 0o755)

        self.fake_ssh = os.path.join(self.tmp.name, "fake-ssh")
        with open(self.fake_ssh, "w", encoding="utf-8") as f:
            f.write(FAKE_SSH)
        os.chmod(self.fake_ssh, 0o755)

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
        env.pop("LEAK_CHECK_SKIP", None)
        env.pop("FAKE_GH_FAIL", None)
        env.pop("GH_REPO", None)
        if extra:
            env.update(extra)
        return env

    def run_leak_check(self, args, stdin_text="", extra_env=None):
        return subprocess.run(
            [sys.executable, LEAK_CHECK, *args],
            input=stdin_text,
            capture_output=True,
            text=True,
            env=self.base_env(extra_env),
            timeout=30,
        )

    def run_claude_hook(self, command, cwd=None, extra_env=None):
        payload = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": command},
            "cwd": cwd or self.tmp.name,
        })
        return self.run_leak_check(["--claude-hook"], stdin_text=payload, extra_env=extra_env)

    def make_repo_pair(self, name, remote_url):
        """Create a local repo and a bare remote wired via fake-ssh (or direct path)."""
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
        full = os.path.join(work, relpath)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        subprocess.run(["git", "-C", work, "add", relpath], env=env, check=True, capture_output=True)
        subprocess.run(["git", "-C", work, "commit", "-m", message], env=env, check=True, capture_output=True)

    def bare_ref_exists(self, bare, ref, env):
        r = subprocess.run(["git", "-C", bare, "show-ref", "--verify", ref], env=env, capture_output=True)
        return r.returncode == 0

    def bare_head_oid(self, bare, ref, env):
        r = subprocess.run(["git", "-C", bare, "rev-parse", ref], env=env, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None

    # --- Direct CLI & matching behavior ---

    def test_word_boundaries_and_case_insensitivity(self):
        for hit_text in [
            "path ~/Work/secret-thing/.git here",
            "prefix_secret-thing_suffix",
            "in SECRET-THING.md",
            "dash-hidden_proj-end",
            "dir/alpha.beta/file",
        ]:
            with self.subTest(hit=hit_text):
                r = self.run_leak_check(["alice/public-repo"], stdin_text=hit_text)
                self.assertNotEqual(r.returncode, 0)

        for clean_text in [
            "just thing alone is fine",
            "mysecret-thing is attached on left",
            "secret-thing2 is attached on right",
            "ordinary public text",
        ]:
            with self.subTest(clean=clean_text):
                r = self.run_leak_check(["alice/public-repo"], stdin_text=clean_text)
                self.assertEqual(r.returncode, 0)

    def test_private_repo_allows_private_names(self):
        r = self.run_leak_check(["alice/private-repo"], stdin_text="mentions secret-thing")
        self.assertEqual(r.returncode, 0)

    def test_extra_terms_file_blocks_custom_terms_and_honors_exclusions(self):
        terms_dir = os.path.join(self.home, ".config", "leak-check")
        os.makedirs(terms_dir, exist_ok=True)
        with open(os.path.join(terms_dir, "terms"), "w", encoding="utf-8") as f:
            f.write("# comment line\n\ncodename-orchid\n!hidden_proj\n")
        self.assertNotEqual(
            self.run_leak_check(["alice/public-repo"], stdin_text="notes on codename-orchid").returncode,
            0,
        )
        self.assertEqual(
            self.run_leak_check(["alice/public-repo"], stdin_text="comment line").returncode,
            0,
        )
        self.assertEqual(
            self.run_leak_check(["alice/public-repo"], stdin_text="mentions hidden_proj").returncode,
            0,
        )

    def test_cache_serves_subsequent_calls_without_gh(self):
        # Populate cache via fake gh.
        self.assertEqual(self.run_leak_check(["alice/public-repo"], stdin_text="clean").returncode, 0)
        # With gh failing, cached visibility and private list still work.
        self.assertNotEqual(
            self.run_leak_check(["alice/public-repo"], stdin_text="secret-thing", extra_env={"FAKE_GH_FAIL": "1"}).returncode,
            0,
        )

    def test_gh_failure_fails_closed_and_skip_overrides(self):
        r_fail = self.run_leak_check(["alice/public-repo"], stdin_text="clean", extra_env={"FAKE_GH_FAIL": "1"})
        self.assertNotEqual(r_fail.returncode, 0)
        r_skip = self.run_leak_check(
            ["alice/public-repo"],
            stdin_text="secret-thing",
            extra_env={"FAKE_GH_FAIL": "1", "LEAK_CHECK_SKIP": "1"},
        )
        self.assertEqual(r_skip.returncode, 0)

    # --- Git pre-push hook behavior ---

    def test_push_to_public_repo_blocks_private_name_in_commit_message(self):
        work, bare, env = self.make_repo_pair("pub-msg", "git@github.com:alice/public-repo.git")
        self.commit_file(work, env, "notes.txt", "clean content\n", "mention secret-thing here")
        r = subprocess.run(["git", "-C", work, "push", "origin", "main"], env=env, capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.bare_ref_exists(bare, "refs/heads/main", env))

    def test_push_to_public_repo_blocks_private_name_in_added_line(self):
        work, bare, env = self.make_repo_pair("pub-line", "git@github.com:alice/public-repo.git")
        self.commit_file(work, env, "notes.txt", "see ~/Work/secret-thing/.git\n", "clean message")
        r = subprocess.run(["git", "-C", work, "push", "origin", "main"], env=env, capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.bare_ref_exists(bare, "refs/heads/main", env))

    def test_push_to_public_repo_blocks_private_name_in_added_filename(self):
        work, bare, env = self.make_repo_pair("pub-file", "git@github.com:alice/public-repo.git")
        self.commit_file(work, env, "docs/secret-thing.md", "clean body\n", "add doc")
        r = subprocess.run(["git", "-C", work, "push", "origin", "main"], env=env, capture_output=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.bare_ref_exists(bare, "refs/heads/main", env))

    def test_push_to_private_repo_passes_with_private_name(self):
        work, bare, env = self.make_repo_pair("priv", "git@github.com:alice/private-repo.git")
        self.commit_file(work, env, "notes.txt", "secret-thing\n", "secret-thing")
        r = subprocess.run(["git", "-C", work, "push", "origin", "main"], env=env, capture_output=True)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(self.bare_ref_exists(bare, "refs/heads/main", env))

    def test_clean_push_and_branch_deletion_pass(self):
        work, bare, env = self.make_repo_pair("clean-del", "git@github.com:alice/public-repo.git")
        self.commit_file(work, env, "notes.txt", "hello world\n", "initial commit")
        r = subprocess.run(["git", "-C", work, "push", "origin", "main"], env=env, capture_output=True)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(self.bare_ref_exists(bare, "refs/heads/main", env))

        subprocess.run(["git", "-C", work, "checkout", "-b", "temp"], env=env, check=True, capture_output=True)
        r = subprocess.run(["git", "-C", work, "push", "origin", "temp"], env=env, capture_output=True)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(self.bare_ref_exists(bare, "refs/heads/temp", env))

        # Deleting a remote branch pushes nothing to scan and must pass even if gh fails.
        r = subprocess.run(
            ["git", "-C", work, "push", "origin", "--delete", "temp"],
            env={**env, "FAKE_GH_FAIL": "1"},
            capture_output=True,
        )
        self.assertEqual(r.returncode, 0)
        self.assertFalse(self.bare_ref_exists(bare, "refs/heads/temp", env))

    def test_already_pushed_leak_is_not_rescanned_and_deletion_of_leak_passes(self):
        work, bare, env = self.make_repo_pair("existing", "git@github.com:alice/public-repo.git")
        # Push a commit containing a private name using the skip override.
        self.commit_file(work, env, "notes.txt", "secret-thing\n", "initial leak")
        r = subprocess.run(
            ["git", "-C", work, "push", "origin", "main"],
            env={**env, "LEAK_CHECK_SKIP": "1"},
            capture_output=True,
        )
        self.assertEqual(r.returncode, 0)
        first_oid = self.bare_head_oid(bare, "refs/heads/main", env)

        # Follow-up commit removing the leak must pass without rescanning the older commit.
        self.commit_file(work, env, "notes.txt", "clean now\n", "remove private reference")
        r = subprocess.run(["git", "-C", work, "push", "origin", "main"], env=env, capture_output=True)
        self.assertEqual(r.returncode, 0)
        self.assertNotEqual(self.bare_head_oid(bare, "refs/heads/main", env), first_oid)

    def test_non_github_remote_is_skipped(self):
        bare = os.path.join(self.tmp.name, "local-bare.git")
        work, _, env = self.make_repo_pair("local", bare)
        # Make gh fail to prove non-GitHub remotes skip gh completely.
        env["FAKE_GH_FAIL"] = "1"
        self.commit_file(work, env, "notes.txt", "secret-thing\n", "secret-thing")
        r = subprocess.run(["git", "-C", work, "push", "origin", "main"], env=env, capture_output=True)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(self.bare_ref_exists(bare, "refs/heads/main", env))

    def test_repo_local_pre_push_hook_runs_alongside_global_hook(self):
        work, bare, env = self.make_repo_pair("local-hook", "git@github.com:alice/public-repo.git")
        marker = os.path.join(self.tmp.name, "local-hook-ran")
        local_hook = os.path.join(work, ".git", "hooks", "pre-push")
        with open(local_hook, "w", encoding="utf-8") as f:
            f.write(f"#!/bin/sh\ntouch '{marker}'\n")
        os.chmod(local_hook, 0o755)

        self.commit_file(work, env, "notes.txt", "clean\n", "clean")
        r = subprocess.run(["git", "-C", work, "push", "origin", "main"], env=env, capture_output=True)
        self.assertEqual(r.returncode, 0)
        self.assertTrue(os.path.exists(marker))

    def test_pre_push_gh_failure_fails_closed_and_skip_overrides(self):
        work, bare, env = self.make_repo_pair("fail-skip", "git@github.com:alice/public-repo.git")
        self.commit_file(work, env, "notes.txt", "clean\n", "clean")
        r_fail = subprocess.run(
            ["git", "-C", work, "push", "origin", "main"],
            env={**env, "FAKE_GH_FAIL": "1"},
            capture_output=True,
        )
        self.assertNotEqual(r_fail.returncode, 0)
        self.assertFalse(self.bare_ref_exists(bare, "refs/heads/main", env))

        r_skip = subprocess.run(
            ["git", "-C", work, "push", "origin", "main"],
            env={**env, "FAKE_GH_FAIL": "1", "LEAK_CHECK_SKIP": "1"},
            capture_output=True,
        )
        self.assertEqual(r_skip.returncode, 0)
        self.assertTrue(self.bare_ref_exists(bare, "refs/heads/main", env))

    # --- Claude Code PreToolUse Bash hook behavior ---

    def test_claude_hook_blocks_body_file_with_private_name_and_allows_clean(self):
        work, _, _ = self.make_repo_pair("claude-pr", "https://github.com/alice/public-repo.git")
        dirty = os.path.join(self.tmp.name, "dirty.md")
        clean = os.path.join(self.tmp.name, "clean.md")
        with open(dirty, "w", encoding="utf-8") as f:
            f.write("Evidence from secret-thing.\n")
        with open(clean, "w", encoding="utf-8") as f:
            f.write("Generic evidence.\n")

        self.assertEqual(
            self.run_claude_hook(f"gh pr create --title 'Fix' --body-file {dirty}", cwd=work).returncode,
            2,
        )
        self.assertEqual(
            self.run_claude_hook(f"gh pr create --title 'Fix' -F {dirty}", cwd=work).returncode,
            2,
        )
        self.assertEqual(
            self.run_claude_hook(f"gh pr create --title 'Fix' --body-file {clean}", cwd=work).returncode,
            0,
        )

    def test_claude_hook_handles_heredoc_with_apostrophe_and_cd(self):
        work, _, _ = self.make_repo_pair("claude-cd", "https://github.com/alice/public-repo.git")
        cmd = (
            f"cd {work} && gh pr create --title 'Update' --body \"$(cat <<'EOF'\n"
            "Don't mention secret-thing here.\n"
            "EOF\n)\""
        )
        self.assertEqual(self.run_claude_hook(cmd, cwd=self.tmp.name).returncode, 2)

    def test_claude_hook_respects_repo_flag_and_api_paths_and_files(self):
        payload_file = os.path.join(self.tmp.name, "payload.json")
        with open(payload_file, "w", encoding="utf-8") as f:
            json.dump({"body": "mentions hidden_proj"}, f)

        # -R targeting public blocks, -R targeting private passes.
        self.assertEqual(
            self.run_claude_hook("gh issue comment 1 -R alice/public-repo -b 'see secret-thing'").returncode,
            2,
        )
        self.assertEqual(
            self.run_claude_hook("gh issue comment 1 -R alice/private-repo -b 'see secret-thing'").returncode,
            0,
        )
        # gh api with -F @file and --input file targeting repos/<owner>/<name>.
        self.assertEqual(
            self.run_claude_hook(
                f"gh api repos/alice/public-repo/issues/1/comments -F body=@{payload_file}"
            ).returncode,
            2,
        )
        self.assertEqual(
            self.run_claude_hook(
                f"gh api /repos/alice/public-repo/issues/1/comments --input {payload_file}"
            ).returncode,
            2,
        )
        self.assertEqual(
            self.run_claude_hook(
                "gh api repos/alice/public-repo/issues/1/comments -f body='secret-thing'"
            ).returncode,
            2,
        )

    def test_claude_hook_skips_readonly_gh_and_non_gh_commands(self):
        work, _, _ = self.make_repo_pair("claude-ro", "https://github.com/alice/public-repo.git")
        # Even with gh failing, non-publishing commands must pass immediately.
        for cmd in [
            "echo secret-thing",
            "gh pr view 1",
            "gh api repos/alice/public-repo -q .visibility",
            "git commit -m 'mentions gh pr create secret-thing'",
        ]:
            with self.subTest(cmd=cmd):
                self.assertEqual(
                    self.run_claude_hook(cmd, cwd=work, extra_env={"FAKE_GH_FAIL": "1"}).returncode,
                    0,
                )

    def test_claude_hook_gh_failure_fails_closed_with_exit_2_and_skip_overrides(self):
        work, _, _ = self.make_repo_pair("claude-fail", "https://github.com/alice/public-repo.git")
        self.assertEqual(
            self.run_claude_hook(
                "gh pr create --title 'Clean' --body 'Clean'",
                cwd=work,
                extra_env={"FAKE_GH_FAIL": "1"},
            ).returncode,
            2,
        )
        self.assertEqual(
            self.run_claude_hook(
                "gh pr create --title 'secret-thing' --body 'secret-thing'",
                cwd=work,
                extra_env={"FAKE_GH_FAIL": "1", "LEAK_CHECK_SKIP": "1"},
            ).returncode,
            0,
        )

    def test_claude_hook_catches_in_command_copy_and_pipe(self):
        work, _, _ = self.make_repo_pair("claude-cp", "https://github.com/alice/public-repo.git")
        src = os.path.join(self.tmp.name, "src.md")
        dst = os.path.join(self.tmp.name, "dst.md")
        with open(src, "w", encoding="utf-8") as f:
            f.write("from alpha.beta\n")
        self.assertEqual(
            self.run_claude_hook(f"cp {src} {dst} && gh pr create --body-file {dst}", cwd=work).returncode,
            2,
        )
        self.assertEqual(
            self.run_claude_hook(f"cat {src} | gh pr create --body-file -", cwd=work).returncode,
            2,
        )
        # Subshell cd followed by newline must restore cwd before gh runs.
        self.assertEqual(
            self.run_claude_hook(
                f"(cd {self.tmp.name} && true)\ngh pr create --title 'secret-thing' --body 'ok' 2>&1",
                cwd=work,
            ).returncode,
            2,
        )


if __name__ == "__main__":
    unittest.main()
