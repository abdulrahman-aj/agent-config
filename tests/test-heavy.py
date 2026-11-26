#!/usr/bin/env python3
"""Behavior tests for home/.local/bin/heavy: real processes and exit codes.

Peer discovery runs through a fake `tailscale` on PATH, and the remote path runs
through tests/fake-ssh with per-peer homes on this machine, so routing, copy,
remote script, copy-back and remote interrupts are exercised without a tailnet.
"""

import json
import os
import signal
import subprocess
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HEAVY = os.path.join(HERE, "..", "home", ".local", "bin", "heavy")
FAKE_SSH = os.path.join(HERE, "fake-ssh")
FAILED = 255


def host_slots():
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    return max(1, int(line.split()[1]) // (10 * 1024 * 1024))
    except OSError:
        pass
    return 1


SLOTS = host_slots()


def alive(pid):
    """True while pid runs; a zombie counts as gone."""
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rpartition(")")[2].split()[0] not in ("Z", "X")
    except OSError:
        return False


class HeavyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = os.path.join(self.tmp.name, "local")
        self.peers_dir = os.path.join(self.tmp.name, "peers")
        self.bin_dir = os.path.join(self.tmp.name, "bin")
        self.repo = os.path.join(self.home, "repo")
        self.remote_home = os.path.join(self.peers_dir, "peer-a")
        self.remote_repo = os.path.join(self.remote_home, "repo")
        os.makedirs(self.repo)
        os.makedirs(self.remote_home)
        os.makedirs(self.bin_dir)
        self.ts_json = os.path.join(self.tmp.name, "tailscale.json")
        fake_ts = os.path.join(self.bin_dir, "tailscale")
        with open(fake_ts, "w") as f:
            f.write(f"#!/usr/bin/env bash\ncat {self.ts_json}\n")
        os.chmod(fake_ts, 0o755)
        self.set_peers(("peer-a", True, "linux"))
        self.git("init", "-q")
        self.write("tracked.txt", "first\n")
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("HEAVY_", "AGENT_HEAVY"))}
        self.env.update(
            HOME=self.home,
            PATH=f"{self.bin_dir}:{self.env.get('PATH', '')}",
            HEAVY_LOCK_DIR=os.path.join(self.tmp.name, "locks"),
            HEAVY_SSH=FAKE_SSH,
            HEAVY_FAKE_PEERS=self.peers_dir,
        )
        self.procs = []

    def tearDown(self):
        for proc in self.procs:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
        self.tmp.cleanup()

    def set_peers(self, *specs):
        """Write fake tailscale status JSON from (name, online, os) tuples."""
        peers = {}
        for i, (name, online, os_name) in enumerate(specs):
            peers[f"k{i}"] = {
                "HostName": name,
                "DNSName": f"{name}.example.ts.net.",
                "OS": os_name,
                "Online": online,
            }
        with open(self.ts_json, "w") as f:
            json.dump({"BackendState": "Running", "Peer": peers}, f)

    def make_peer(self, name, deny_via=None):
        """Create a fake peer home; deny_via='envd' writes environment.d, 'profile' writes .profile."""
        home = os.path.join(self.peers_dir, name)
        os.makedirs(home, exist_ok=True)
        if deny_via == "envd":
            self.write(".config/environment.d/60-agent-heavy-jobs.conf", "AGENT_HEAVY_JOBS=deny\n", root=home)
        elif deny_via == "profile":
            self.write(".profile", "export AGENT_HEAVY_JOBS=deny\n", root=home)
        return home

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def write(self, name, text, root=None):
        path = os.path.join(root or self.repo, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def start(self, command, *flags, remote=False, **env):
        if remote:
            env.setdefault("AGENT_HEAVY_JOBS", "deny")
            env.setdefault("HEAVY_LOCK_DIR", os.path.join(self.tmp.name, "remote-locks"))
        proc = subprocess.Popen([HEAVY, *flags, "--", command], cwd=self.repo, env={**self.env, **env},
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.procs.append(proc)
        return proc

    def run_heavy(self, command, *flags, remote=False, **env):
        return self.start(command, *flags, remote=remote, **env).wait(timeout=60)

    def wait_for(self, path, seconds=20):
        deadline = time.monotonic() + seconds
        while not os.path.exists(path):
            self.assertLess(time.monotonic(), deadline, f"{path} never appeared")
            time.sleep(0.05)

    def lines(self, name, root=None):
        try:
            with open(os.path.join(root or self.repo, name)) as f:
                return len(f.readlines())
        except FileNotFoundError:
            return 0

    # Routing

    def test_non_denying_host_runs_locally_even_when_a_peer_is_up(self):
        self.assertEqual(self.run_heavy("touch ran-here"), 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "ran-here")))
        self.assertFalse(os.path.exists(self.remote_repo))

    def test_denying_host_picks_eligible_peer_and_skips_denying_or_offline_ones(self):
        self.make_peer("peer-1", deny_via="envd")
        self.make_peer("peer-2", deny_via="profile")
        peer3 = self.make_peer("peer-3")
        peer4 = self.make_peer("peer-4")
        # peer-0 is listed in tailscale but has no dir under peers_dir (unreachable over ssh).
        self.set_peers(
            ("peer-0", True, "linux"),
            ("peer-off", False, "linux"),
            ("peer-win", True, "windows"),
            ("peer-1", True, "linux"),
            ("peer-2", True, "linux"),
            ("peer-4", True, "linux"),
            ("peer-3", True, "linux"),
        )
        self.assertEqual(self.run_heavy("touch ran-remote", remote=True), 0)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "ran-remote")))
        self.assertFalse(os.path.exists(os.path.join(self.peers_dir, "peer-1", "repo")))
        self.assertFalse(os.path.exists(os.path.join(self.peers_dir, "peer-2", "repo")))
        self.assertTrue(os.path.exists(os.path.join(peer3, "repo", "ran-remote")))
        self.assertFalse(os.path.exists(os.path.join(peer4, "repo")))

    def test_denying_host_falls_back_locally_with_deny_lifted_when_no_peer_is_eligible(self):
        self.make_peer("peer-deny", deny_via="envd")
        self.set_peers(("peer-deny", True, "linux"), ("peer-down", False, "linux"))
        check = 'test -z "${AGENT_HEAVY_JOBS:-}" && touch ran-fallback'
        self.assertEqual(self.run_heavy(check, AGENT_HEAVY_JOBS="deny"), 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "ran-fallback")))

    def test_denying_host_falls_back_locally_when_tailscale_has_no_peers(self):
        self.set_peers()
        check = 'test -z "${AGENT_HEAVY_JOBS:-}" && touch ran-fallback'
        result = subprocess.run([HEAVY, "--", check], cwd=self.repo,
                                env={**self.env, "AGENT_HEAVY_JOBS": "deny"},
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "ran-fallback")))
        self.assertTrue(any(line.startswith("heavy:") for line in result.stderr.splitlines()))

    # Local path

    def test_exit_status_passes_through_and_the_job_runs_once(self):
        for code in (0, 3, 75, 255):
            with self.subTest(code=code):
                os.makedirs(self.repo, exist_ok=True)
                count = f"runs-{code}"
                self.assertEqual(self.run_heavy(f"echo run >> {count}; exit {code}"), code)
                self.assertEqual(self.lines(count), 1)  # 75 isn't "slot busy": no rerun

    def test_several_words_are_an_argv_and_one_word_is_a_command_line(self):
        proc = subprocess.Popen([HEAVY, "--", "touch", "my file"], cwd=self.repo, env=self.env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.procs.append(proc)
        self.assertEqual(proc.wait(timeout=60), 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "my file")))
        self.assertEqual(self.run_heavy("touch a && touch b"), 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "b")))

    def test_a_job_past_the_cap_waits_for_a_slot(self):
        hold = "touch started-$N; while [ ! -e release ]; do sleep 0.05; done"
        holders = [self.start(hold.replace("$N", str(n))) for n in range(SLOTS)]
        for n in range(SLOTS):
            self.wait_for(os.path.join(self.repo, f"started-{n}"))
        extra = self.start("touch started-extra")
        time.sleep(1.5)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "started-extra")))
        open(os.path.join(self.repo, "release"), "w").close()
        self.assertEqual([p.wait(timeout=30) for p in holders + [extra]], [0] * (SLOTS + 1))
        self.assertTrue(os.path.exists(os.path.join(self.repo, "started-extra")))

    def test_a_signal_kills_the_job_group_and_runs_cleanup(self):
        self.write(".heavy-cleanup", "touch cleaned\n")
        for signum in (signal.SIGTERM, signal.SIGINT):
            with self.subTest(signal=signum.name):
                for name in ("grandchild", "cleaned"):
                    if os.path.exists(os.path.join(self.repo, name)):
                        os.remove(os.path.join(self.repo, name))
                proc = self.start("sleep 300 & echo $! > grandchild; wait")
                self.wait_for(os.path.join(self.repo, "grandchild"))
                with open(os.path.join(self.repo, "grandchild")) as f:
                    pid = int(f.read())
                proc.send_signal(signum)
                self.assertEqual(proc.wait(timeout=30), 128 + signum)
                self.assertFalse(alive(pid))
                self.assertTrue(os.path.exists(os.path.join(self.repo, "cleaned")))

    # Remote path, through fake-ssh

    def test_remote_copy_has_uncommitted_edits_minus_heavyignore(self):
        self.write("tracked.txt", "edited\n")
        self.write("untracked.txt", "new\n")
        self.write(".heavyignore", "skip/\n")
        self.write("skip/big", "x\n")
        check = "grep -q edited tracked.txt && test -e untracked.txt && test ! -e skip"
        self.assertEqual(self.run_heavy(check, remote=True), 0)

    def test_remote_exit_status_passes_through(self):
        for code in (0, 75, 255):
            with self.subTest(code=code):
                self.assertEqual(self.run_heavy(f"exit {code}", remote=True), code)

    def test_remote_status_survives_output_without_a_final_newline(self):
        self.assertEqual(self.run_heavy("printf partial; printf more >&2; exit 3", remote=True), 3)

    def test_out_copies_back_what_the_job_made_or_updated(self):
        job = "mkdir -p build && touch build/made ..dots && echo more >> tracked.txt"
        rc = self.run_heavy(job, "--out", "build", "--out", "tracked.txt", "--out", "missing",
                            "--out", "..dots", remote=True)
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "build", "made")))
        self.assertTrue(os.path.exists(os.path.join(self.repo, "..dots")))
        self.assertEqual(self.lines("tracked.txt"), 2)

    def test_a_signal_stops_the_remote_job_group_and_runs_cleanup(self):
        self.write(".heavy-cleanup", "touch cleaned\n")
        proc = self.start("sleep 300 & echo $! > grandchild; wait", remote=True)
        self.wait_for(os.path.join(self.remote_repo, "grandchild"))
        with open(os.path.join(self.remote_repo, "grandchild")) as f:
            pid = int(f.read())
        proc.send_signal(signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=30), 128 + signal.SIGTERM)
        self.assertFalse(alive(pid))
        self.assertTrue(os.path.exists(os.path.join(self.remote_repo, "cleaned")))

    def test_a_group_kill_stops_the_remote_job_and_heavy_reports_it(self):
        """agent-wait stops a job by killing heavy's whole process group."""
        self.write(".heavy-cleanup", "touch cleaned\n")
        proc = subprocess.Popen([HEAVY, "--", "sleep 300 & echo $! > grandchild; wait"], cwd=self.repo,
                                env={**self.env, "AGENT_HEAVY_JOBS": "deny"}, start_new_session=True,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.procs.append(proc)
        self.wait_for(os.path.join(self.remote_repo, "grandchild"))
        with open(os.path.join(self.remote_repo, "grandchild")) as f:
            pid = int(f.read())
        os.killpg(proc.pid, signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=30), 128 + signal.SIGTERM)
        self.assertFalse(alive(pid))
        self.assertTrue(os.path.exists(os.path.join(self.remote_repo, "cleaned")))

    def test_a_linked_worktree_runs_without_touching_a_peers_real_checkout(self):
        worktree = os.path.join(self.home, "linked")
        self.git("worktree", "add", "-q", worktree)
        self.write("tracked.txt", "edited in the worktree\n", root=worktree)
        # The peer already holds a real checkout at ~/repo that heavy didn't create.
        self.write("precious", "keep\n", root=self.remote_repo)
        check = "grep -q edited tracked.txt && git status --short | grep -q tracked.txt"
        proc = subprocess.Popen([HEAVY, "--", check], cwd=worktree,
                                env={**self.env, "AGENT_HEAVY_JOBS": "deny"},
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.procs.append(proc)
        self.assertEqual(proc.wait(timeout=60), 0)
        self.assertTrue(os.path.exists(os.path.join(self.remote_repo, "precious")))

    def pid_in(self, path):
        self.wait_for(path)
        with open(path) as f:
            return int(f.read())

    def test_a_grandchild_that_ignores_term_is_killed_after_grace_on_a_signal(self):
        job = "(trap '' TERM; sleep 60) & echo $! > {}; wait"
        remote = self.start(job.format("g-remote"), remote=True)
        remote_pid = self.pid_in(os.path.join(self.remote_repo, "g-remote"))
        local = self.start(job.format("g-local"))
        local_pid = self.pid_in(os.path.join(self.repo, "g-local"))
        for proc in (remote, local):
            proc.send_signal(signal.SIGTERM)
        self.assertEqual([p.wait(timeout=40) for p in (remote, local)], [128 + signal.SIGTERM] * 2)
        self.assertFalse(alive(remote_pid))
        self.assertFalse(alive(local_pid))

    def test_a_grandchild_that_ignores_term_is_killed_after_grace_on_a_normal_exit(self):
        job = "(trap '' TERM; sleep 60) & echo $! > {}; exit 4"
        remote = self.start(job.format("g-remote"), remote=True)
        local = self.start(job.format("g-local"))
        self.assertEqual([p.wait(timeout=40) for p in (remote, local)], [4, 4])
        self.assertFalse(alive(self.pid_in(os.path.join(self.remote_repo, "g-remote"))))
        self.assertFalse(alive(self.pid_in(os.path.join(self.repo, "g-local"))))

    def run_in(self, cwd, command):
        proc = subprocess.Popen([HEAVY, "--", command], cwd=cwd,
                                env={**self.env, "AGENT_HEAVY_JOBS": "deny"},
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.procs.append(proc)
        return proc

    def test_a_main_checkout_and_its_worktree_share_a_peer_in_either_order(self):
        worktree = os.path.join(self.home, "linked")
        self.git("worktree", "add", "-q", worktree)
        for order in ([self.repo, worktree], [worktree, self.repo]):
            with self.subTest(first=os.path.basename(order[0])):
                state = os.path.join(self.remote_home, ".local", "state")
                cache = os.path.join(self.remote_home, ".cache")
                subprocess.run(["rm", "-rf", self.remote_repo, os.path.join(self.remote_home, "linked"), state, cache],
                               check=True)
                self.assertEqual([self.run_in(cwd, "git status --short").wait(timeout=60) for cwd in order],
                                 [0, 0])

    def test_a_main_checkout_and_its_worktree_run_concurrently(self):
        worktree = os.path.join(self.home, "linked")
        self.git("worktree", "add", "-q", worktree)
        procs = [self.run_in(cwd, "git status --short && sleep 1") for cwd in (self.repo, worktree)]
        self.assertEqual([p.wait(timeout=60) for p in procs], [0, 0])

    def test_remote_refuses_to_overwrite_a_directory_it_did_not_copy(self):
        self.write("precious", "keep\n", root=self.remote_repo)
        self.assertEqual(self.run_heavy("touch ran", remote=True), FAILED)
        self.assertTrue(os.path.exists(os.path.join(self.remote_repo, "precious")))
        self.assertFalse(os.path.exists(os.path.join(self.remote_repo, "ran")))


if __name__ == "__main__":
    unittest.main()
