#!/usr/bin/env python3
"""Behavior tests for home/.local/bin/heavy: real processes and exit codes."""

import fcntl
import hashlib
import json
import os
import signal
import socket
import subprocess
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HEAVY = os.path.join(HERE, "..", "home", ".local", "bin", "heavy")
FAKE_SSH = os.path.join(HERE, "fake-ssh")
FAILED = 255
SUFFIX = "example.ts.net"
PEER_A = f"peer-a.{SUFFIX}"


def host_slots():
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    return max(1, int(line.split()[1]) // (10 * 1024 * 1024))
    except OSError:
        pass
    return 1


def stage_dir(peer_home, root):
    try:
        with open("/etc/machine-id") as f:
            host_id = f.read().strip()
    except OSError:
        host_id = ""
    sid = hashlib.sha256(f"{host_id or socket.gethostname()}\0{os.path.realpath(root)}".encode()).hexdigest()[:12]
    return os.path.join(peer_home, ".cache", "heavy", "work", sid)


def alive(pid):
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rpartition(")")[2].split()[0] not in ("Z", "X")
    except OSError:
        return False


SLOTS = host_slots()


class HeavyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = os.path.join(self.tmp.name, "local")
        self.peers_dir = os.path.join(self.tmp.name, "peers")
        self.bin_dir = os.path.join(self.tmp.name, "bin")
        self.repo = os.path.join(self.home, "repo")
        self.remote_home = os.path.join(self.peers_dir, PEER_A)
        for d in (self.repo, self.remote_home, self.bin_dir):
            os.makedirs(d)
        self.remote_tree = os.path.join(stage_dir(self.remote_home, self.repo), "tree")
        self.ts_json = os.path.join(self.tmp.name, "tailscale.json")
        fake_ts = os.path.join(self.bin_dir, "tailscale")
        with open(fake_ts, "w") as f:
            f.write(f"#!/usr/bin/env bash\ncat {self.ts_json}\n")
        os.chmod(fake_ts, 0o755)
        self.set_peers((PEER_A, True, "linux"))
        self.git("init", "-q")
        self.write("tracked.txt", "first\n")
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("HEAVY_", "AGENT_HEAVY"))}
        self.env.update(HOME=self.home, PATH=f"{self.bin_dir}:{self.env.get('PATH', '')}",
                        HEAVY_LOCK_DIR=os.path.join(self.tmp.name, "locks"),
                        HEAVY_SSH=FAKE_SSH, HEAVY_FAKE_PEERS=self.peers_dir)
        self.procs = []

    def tearDown(self):
        for p in self.procs:
            if p.poll() is None:
                p.kill()
                p.wait()
        self.tmp.cleanup()

    def set_peers(self, *specs):
        peers = {}
        for i, spec in enumerate(specs):
            dns, online, os_name = spec[:3]
            uid = spec[3] if len(spec) > 3 else 100
            full = dns if "." in dns else f"{dns}.{SUFFIX}"
            peers[f"k{i}"] = {"HostName": full.split(".")[0], "DNSName": f"{full}.",
                              "OS": os_name, "Online": online, "UserID": uid}
        with open(self.ts_json, "w") as f:
            json.dump({"BackendState": "Running", "MagicDNSSuffix": SUFFIX,
                       "Self": {"UserID": 100}, "Peer": peers}, f)

    def make_peer(self, dns, deny_via=None):
        home = os.path.join(self.peers_dir, dns if "." in dns else f"{dns}.{SUFFIX}")
        os.makedirs(home, exist_ok=True)
        if deny_via == "envd":
            self.write(".config/environment.d/60-agent-heavy-jobs.conf", "AGENT_HEAVY_JOBS=deny\n", root=home)
        elif deny_via == "profile":
            self.write(".profile", "export AGENT_HEAVY_JOBS=deny\n", root=home)
        elif deny_via == "after-probe":
            self.write(".deny-after-probe", "1\n", root=home)
        return home

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def write(self, name, text, root=None):
        path = os.path.join(root or self.repo, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def start(self, command, *flags, remote=False, cwd=None, **env):
        if remote:
            env.setdefault("AGENT_HEAVY_JOBS", "deny")
            env.setdefault("HEAVY_LOCK_DIR", os.path.join(self.tmp.name, "remote-locks"))
        p = subprocess.Popen([HEAVY, *flags, "--", command], cwd=cwd or self.repo,
                             env={**self.env, **env}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.procs.append(p)
        return p

    def run_heavy(self, command, *flags, remote=False, cwd=None, **env):
        return self.start(command, *flags, remote=remote, cwd=cwd, **env).wait(timeout=60)

    def wait_for(self, path, seconds=20):
        deadline = time.monotonic() + seconds
        while not os.path.exists(path):
            self.assertLess(time.monotonic(), deadline, f"{path} never appeared")
            time.sleep(0.05)

    def pid_in(self, path):
        self.wait_for(path)
        with open(path) as f:
            return int(f.read())

    # Routing

    def test_non_denying_host_runs_locally_even_when_a_peer_is_up(self):
        self.assertEqual(self.run_heavy("touch ran-here"), 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "ran-here")))
        self.assertFalse(os.path.exists(self.remote_tree))

    def test_denying_host_picks_own_eligible_peer_and_skips_others(self):
        self.make_peer("peer-1", deny_via="envd")
        self.make_peer("peer-2", deny_via="profile")
        self.make_peer("peer-other-user")
        self.make_peer("peer-ext.other.ts.net")
        peer3 = self.make_peer("peer-3")
        self.make_peer("peer-4")
        self.set_peers(
            ("peer-0", True, "linux"), ("peer-off", False, "linux"), ("peer-win", True, "windows"),
            ("peer-other-user", True, "linux", 999), ("peer-ext.other.ts.net", True, "linux"),
            ("peer-1", True, "linux"), ("peer-2", True, "linux"),
            ("peer-4", True, "linux"), ("peer-3", True, "linux"),
        )
        self.assertEqual(self.run_heavy("touch ran-remote", remote=True), 0)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "ran-remote")))
        self.assertTrue(os.path.exists(os.path.join(stage_dir(peer3, self.repo), "tree", "ran-remote")))
        for skipped in ("peer-1", "peer-2", "peer-other-user", "peer-4"):
            self.assertFalse(os.path.exists(stage_dir(os.path.join(self.peers_dir, f"{skipped}.{SUFFIX}"), self.repo)))

    def test_deny_rechecked_at_job_start_moves_to_next_peer_or_falls_back(self):
        peer1 = self.make_peer("peer-1", deny_via="after-probe")
        peer2 = self.make_peer("peer-2")
        self.set_peers(("peer-1", True, "linux"), ("peer-2", True, "linux"))
        self.assertEqual(self.run_heavy("touch ran-job", remote=True), 0)
        self.assertFalse(os.path.exists(os.path.join(stage_dir(peer1, self.repo), "tree", "ran-job")))
        self.assertTrue(os.path.exists(os.path.join(stage_dir(peer2, self.repo), "tree", "ran-job")))
        self.make_peer("peer-only", deny_via="after-probe")
        self.set_peers(("peer-only", True, "linux"))
        self.assertEqual(self.run_heavy('test -z "${AGENT_HEAVY_JOBS:-}" && touch ran-fb', remote=True), 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "ran-fb")))

    def test_denying_host_falls_back_locally_with_deny_lifted_when_no_peer_answers(self):
        self.set_peers()
        res = subprocess.run([HEAVY, "--", 'test -z "${AGENT_HEAVY_JOBS:-}" && touch ran-fallback'],
                             cwd=self.repo, env={**self.env, "AGENT_HEAVY_JOBS": "deny"},
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "ran-fallback")))
        self.assertTrue(any(line.startswith("heavy:") for line in res.stderr.splitlines()))

    # Local path

    def test_exit_status_argv_and_no_rerun_on_75(self):
        for code in (0, 3, 75, 255):
            with self.subTest(code=code):
                self.assertEqual(self.run_heavy(f"echo run >> runs-{code}; exit {code}"), code)
                with open(os.path.join(self.repo, f"runs-{code}")) as f:
                    self.assertEqual(len(f.readlines()), 1)
        p = subprocess.Popen([HEAVY, "--", "touch", "my file"], cwd=self.repo, env=self.env,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.procs.append(p)
        self.assertEqual(p.wait(timeout=60), 0)
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

    def test_unwritable_slot_lock_is_fatal_not_busy(self):
        ro_locks = os.path.join(self.tmp.name, "ro-locks")
        os.makedirs(ro_locks)
        slot1 = os.path.join(ro_locks, "slot-1.lock")
        open(slot1, "w").close()
        os.chmod(slot1, 0o444)
        self.assertEqual(self.run_heavy("touch ran", HEAVY_LOCK_DIR=ro_locks), FAILED)
        self.assertEqual(self.run_heavy("touch ran", remote=True, HEAVY_LOCK_DIR=ro_locks), FAILED)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "ran")))

    def test_a_signal_kills_the_job_group_and_runs_cleanup(self):
        self.write(".heavy-cleanup", "touch cleaned\n")
        for signum in (signal.SIGTERM, signal.SIGINT):
            with self.subTest(signal=signum.name):
                for name in ("grandchild", "cleaned"):
                    p = os.path.join(self.repo, name)
                    if os.path.exists(p):
                        os.remove(p)
                proc = self.start("sleep 300 & echo $! > grandchild; wait")
                pid = self.pid_in(os.path.join(self.repo, "grandchild"))
                proc.send_signal(signum)
                self.assertEqual(proc.wait(timeout=30), 128 + signum)
                self.assertFalse(alive(pid))
                self.assertTrue(os.path.exists(os.path.join(self.repo, "cleaned")))

    # Remote path

    def test_remote_copy_excludes_exit_status_and_partial_output(self):
        self.write("tracked.txt", "edited\n")
        self.write("untracked.txt", "new\n")
        self.write(".heavyignore", "skip/\n")
        self.write("skip/big", "x\n")
        self.assertEqual(self.run_heavy("grep -q edited tracked.txt && test -e untracked.txt && test ! -e skip",
                                        remote=True), 0)
        for code in (0, 75, 255):
            with self.subTest(code=code):
                self.assertEqual(self.run_heavy(f"exit {code}", remote=True), code)
        self.assertEqual(self.run_heavy("printf partial; printf more >&2; exit 3", remote=True), 3)

    def test_out_copies_back_files_and_never_overwrites_git(self):
        worktree = os.path.join(self.home, "linked")
        self.git("worktree", "add", "-q", worktree)
        with open(os.path.join(worktree, ".git")) as f:
            orig_git = f.read()
        job = 'mkdir -p "my dir" && touch "my dir/made file" ..dots && echo more >> tracked.txt'
        self.assertEqual(self.run_heavy(job, "--out", ".", "--out", "my dir/made file", "--out", ".git",
                                        "--out", "..", "--out", "missing", remote=True, cwd=worktree), 0)
        self.assertTrue(os.path.exists(os.path.join(worktree, "my dir", "made file")))
        self.assertTrue(os.path.exists(os.path.join(worktree, "..dots")))
        with open(os.path.join(worktree, "tracked.txt")) as f:
            self.assertEqual(len(f.readlines()), 2)
        with open(os.path.join(worktree, ".git")) as f:
            self.assertEqual(f.read(), orig_git)

    def test_a_signal_and_group_kill_stop_remote_job_group_and_run_cleanup(self):
        self.write(".heavy-cleanup", "touch cleaned\n")
        for group_kill in (False, True):
            with self.subTest(group_kill=group_kill):
                for name in ("grandchild", "cleaned"):
                    p = os.path.join(self.remote_tree, name)
                    if os.path.exists(p):
                        os.remove(p)
                proc = subprocess.Popen([HEAVY, "--", "sleep 300 & echo $! > grandchild; wait"], cwd=self.repo,
                                        env={**self.env, "AGENT_HEAVY_JOBS": "deny",
                                             "HEAVY_LOCK_DIR": os.path.join(self.tmp.name, "remote-locks")},
                                        start_new_session=group_kill,
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.procs.append(proc)
                pid = self.pid_in(os.path.join(self.remote_tree, "grandchild"))
                (os.killpg if group_kill else os.kill)(proc.pid, signal.SIGTERM)
                self.assertEqual(proc.wait(timeout=30), 128 + signal.SIGTERM)
                self.assertFalse(alive(pid))
                self.assertTrue(os.path.exists(os.path.join(self.remote_tree, "cleaned")))

    def test_a_grandchild_that_ignores_term_is_killed_after_grace(self):
        for kind, job, expected in [
            ("signal", "(trap '' TERM; sleep 60) & echo $! > {}; wait", 128 + signal.SIGTERM),
            ("normal", "(trap '' TERM; sleep 60) & echo $! > {}; exit 4", 4),
        ]:
            with self.subTest(kind=kind):
                remote = self.start(job.format(f"gr-{kind}"), remote=True)
                local = self.start(job.format(f"gl-{kind}"))
                rpid = self.pid_in(os.path.join(self.remote_tree, f"gr-{kind}"))
                lpid = self.pid_in(os.path.join(self.repo, f"gl-{kind}"))
                if kind == "signal":
                    remote.send_signal(signal.SIGTERM)
                    local.send_signal(signal.SIGTERM)
                self.assertEqual([p.wait(timeout=40) for p in (remote, local)], [expected, expected])
                self.assertFalse(alive(rpid))
                self.assertFalse(alive(lpid))

    def test_main_and_two_linked_worktrees_run_concurrently_with_isolated_refs(self):
        wt1, wt2 = os.path.join(self.home, "wt1"), os.path.join(self.home, "wt2")
        self.git("worktree", "add", "-q", wt1)
        self.git("worktree", "add", "-q", wt2)
        self.write("precious", "keep\n", root=os.path.join(self.remote_home, "repo"))
        p_main = self.start("git status --short && sleep 0.5", remote=True, cwd=self.repo)
        p_wt1 = self.start("git update-ref refs/heads/only-in-wt1 HEAD && sleep 0.5 && "
                           "git show-ref --verify refs/heads/only-in-wt1 && "
                           "! git show-ref --verify refs/heads/only-in-wt2", remote=True, cwd=wt1)
        p_wt2 = self.start("git update-ref refs/heads/only-in-wt2 HEAD && sleep 0.5 && "
                           "git show-ref --verify refs/heads/only-in-wt2 && "
                           "! git show-ref --verify refs/heads/only-in-wt1", remote=True, cwd=wt2)
        self.assertEqual([p.wait(timeout=60) for p in (p_main, p_wt1, p_wt2)], [0, 0, 0])
        self.assertTrue(os.path.exists(os.path.join(self.remote_home, "repo", "precious")))

    def test_staging_refuses_symlinked_parents_or_paths_outside_staging_root(self):
        outside = os.path.join(self.tmp.name, "outside")
        self.write("precious", "keep\n", root=outside)
        os.makedirs(os.path.join(self.remote_home, ".cache", "heavy"), exist_ok=True)
        work_link = os.path.join(self.remote_home, ".cache", "heavy", "work")
        os.symlink(outside, work_link)
        self.assertEqual(self.run_heavy("touch ran", remote=True), FAILED)
        self.assertTrue(os.path.exists(os.path.join(outside, "precious")))
        self.assertFalse(os.path.exists(os.path.join(outside, "ran")))
        os.unlink(work_link)
        sdir = stage_dir(self.remote_home, self.repo)
        os.makedirs(sdir, exist_ok=True)
        os.symlink(outside, os.path.join(sdir, "tree"))
        self.assertEqual(self.run_heavy("touch ran", remote=True), FAILED)
        self.assertTrue(os.path.exists(os.path.join(outside, "precious")))
        self.assertFalse(os.path.exists(os.path.join(outside, "ran")))

    def test_queued_job_skips_peer_if_deny_turns_on_while_waiting_for_slot(self):
        peer1, peer2 = self.make_peer("peer-1"), self.make_peer("peer-2")
        self.set_peers(("peer-1", True, "linux"), ("peer-2", True, "linux"))
        wt = os.path.join(self.home, "queued-wt")
        self.git("worktree", "add", "-q", wt)
        rlocks = os.path.join(self.tmp.name, "queued-rlocks")
        os.makedirs(rlocks)
        held = []
        for n in range(1, SLOTS + 1):
            f = open(os.path.join(rlocks, f"slot-{n}.lock"), "w")
            fcntl.flock(f, fcntl.LOCK_EX)
            held.append(f)
        try:
            proc = self.start("touch ran-queued", remote=True, cwd=wt, HEAVY_LOCK_DIR=rlocks)
            # Rewritten .git proves the job passed the pre-slot deny check and reached the slot wait.
            git_file = os.path.join(stage_dir(peer1, wt), "tree", ".git")
            deadline = time.monotonic() + 20
            while True:
                if os.path.exists(git_file):
                    with open(git_file) as f:
                        if ".cache/heavy/work/" in f.read():
                            break
                self.assertLess(time.monotonic(), deadline, "queued job never reached slot wait")
                time.sleep(0.05)
            self.write(".config/environment.d/60-agent-heavy-jobs.conf", "AGENT_HEAVY_JOBS=deny\n", root=peer1)
        finally:
            for f in held:
                f.close()
        self.assertEqual(proc.wait(timeout=30), 0)
        self.assertFalse(os.path.exists(os.path.join(stage_dir(peer1, wt), "tree", "ran-queued")))
        self.assertTrue(os.path.exists(os.path.join(stage_dir(peer2, wt), "tree", "ran-queued")))

    def test_retry_waits_for_remote_cleanup_after_client_kill(self):
        proof = os.path.join(self.tmp.name, "cleanup-saw-marker")
        release = os.path.join(self.tmp.name, "release-cleanup")
        self.write("marker", "keep\n")
        self.write(".heavy-cleanup", f"touch cleanup-started\nwhile [ ! -e {release} ]; do sleep 0.05; done\n"
                                     f"test -e marker && touch {proof}\n")
        first = self.start("sleep 300 & echo $! > started; wait", remote=True)
        self.wait_for(os.path.join(self.remote_tree, "started"))
        first.kill()
        first.wait(timeout=10)
        self.wait_for(os.path.join(self.remote_tree, "cleanup-started"))
        os.remove(os.path.join(self.repo, "marker"))
        retry = self.start("touch retry-ran", remote=True)
        time.sleep(1.0)
        self.assertTrue(os.path.exists(os.path.join(self.remote_tree, "marker")))
        self.assertFalse(os.path.exists(os.path.join(self.remote_tree, "retry-ran")))
        open(release, "w").close()
        self.assertEqual(retry.wait(timeout=30), 0)
        self.assertTrue(os.path.exists(proof))
        self.assertTrue(os.path.exists(os.path.join(self.remote_tree, "retry-ran")))
        self.assertFalse(os.path.exists(os.path.join(self.remote_tree, "marker")))


if __name__ == "__main__":
    unittest.main()
