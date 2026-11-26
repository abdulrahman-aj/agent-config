#!/usr/bin/env python3
"""Behavior tests for home/.local/bin/heavy: real processes and exit codes."""

import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import tempfile
import time
import unittest

HERE = Path(__file__).resolve().parent
HEAVY = str(HERE.parent / "home/.local/bin/heavy")
FAKE_SSH = str(HERE / "fake-ssh")
FAILED = 255
SUFFIX = "example.ts.net"
PEER_A = f"peer-a.{SUFFIX}"


def host_slots():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemTotal:"):
            return max(1, int(line.split()[1]) // (10 * 1024 * 1024))
    return 1


def stage_dir(peer_home, root):
    mid = Path("/etc/machine-id")
    host_id = mid.read_text().strip() if mid.is_file() else ""
    sid = hashlib.sha256(f"{host_id or socket.gethostname()}\0{Path(root).resolve()}".encode()).hexdigest()[:12]
    return Path(peer_home) / ".cache/heavy/work" / sid


def alive(pid):
    try:
        return Path(f"/proc/{pid}/stat").read_text().rpartition(")")[2].split()[0] not in ("Z", "X")
    except OSError:
        return False


SLOTS = host_slots()


class HeavyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root_tmp = Path(self.tmp.name)
        self.home = self.root_tmp / "local"
        self.peers_dir = self.root_tmp / "peers"
        self.bin_dir = self.root_tmp / "bin"
        self.repo = self.home / "repo"
        self.remote_home = self.peers_dir / PEER_A
        for d in (self.repo, self.remote_home, self.bin_dir):
            d.mkdir(parents=True)
        self.remote_tree = stage_dir(self.remote_home, self.repo) / "tree"
        self.ts_json = self.root_tmp / "tailscale.json"
        fake_ts = self.bin_dir / "tailscale"
        fake_ts.write_text(f"#!/usr/bin/env bash\ncat {self.ts_json}\n")
        fake_ts.chmod(0o755)
        self.set_peers((PEER_A, True, "linux"))
        self.git("init", "-q")
        self.write("tracked.txt", "first\n")
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("HEAVY_", "AGENT_HEAVY"))}
        self.env.update(HOME=str(self.home), PATH=f"{self.bin_dir}:{self.env.get('PATH', '')}",
                        HEAVY_LOCK_DIR=str(self.root_tmp / "locks"),
                        HEAVY_SSH=FAKE_SSH, HEAVY_FAKE_PEERS=str(self.peers_dir))
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
        self.ts_json.write_text(json.dumps({"BackendState": "Running", "MagicDNSSuffix": SUFFIX,
                                            "Self": {"UserID": 100}, "Peer": peers}))

    def make_peer(self, dns, deny_via=None):
        home = self.peers_dir / (dns if "." in dns else f"{dns}.{SUFFIX}")
        home.mkdir(parents=True, exist_ok=True)
        files = {
            "envd": (".config/environment.d/60-agent-heavy-jobs.conf", "AGENT_HEAVY_JOBS=deny\n"),
            "profile": (".profile", "export AGENT_HEAVY_JOBS=deny\n"),
            "after-probe": (".deny-after-probe", "1\n"),
        }
        if deny_via in files:
            self.write(*files[deny_via], root=home)
        return home

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def write(self, name, text, root=None):
        p = Path(root or self.repo) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def start(self, command, *flags, remote=False, cwd=None, new_session=False, **env):
        if remote:
            env.setdefault("AGENT_HEAVY_JOBS", "deny")
            env.setdefault("HEAVY_LOCK_DIR", str(self.root_tmp / "remote-locks"))
        p = subprocess.Popen([HEAVY, *flags, "--", command], cwd=cwd or self.repo,
                             env={**self.env, **env}, start_new_session=new_session,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.procs.append(p)
        return p

    def run_heavy(self, command, *flags, remote=False, cwd=None, **env):
        return self.start(command, *flags, remote=remote, cwd=cwd, **env).wait(timeout=60)

    def wait_for(self, path, seconds=20):
        deadline = time.monotonic() + seconds
        while not Path(path).exists():
            self.assertLess(time.monotonic(), deadline, f"{path} never appeared")
            time.sleep(0.05)

    def pid_in(self, path):
        self.wait_for(path)
        return int(Path(path).read_text())

    def make_slow_ssh(self, name, hook):
        p = self.root_tmp / name
        p.write_text(f"#!/usr/bin/env bash\n{hook}\nexec {FAKE_SSH} \"$@\"\n")
        p.chmod(0o755)
        return str(p)

    # Routing

    def test_non_denying_host_runs_locally_even_when_a_peer_is_up(self):
        self.assertEqual(self.run_heavy("touch ran-here"), 0)
        self.assertTrue((self.repo / "ran-here").exists())
        self.assertFalse(self.remote_tree.exists())

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
        self.assertFalse((self.repo / "ran-remote").exists())
        self.assertTrue((stage_dir(peer3, self.repo) / "tree/ran-remote").exists())
        for skipped in ("peer-1", "peer-2", "peer-other-user", "peer-4"):
            self.assertFalse(stage_dir(self.peers_dir / f"{skipped}.{SUFFIX}", self.repo).exists())

    def test_deny_rechecked_at_job_start_moves_to_next_peer_or_falls_back(self):
        peer1, peer2 = self.make_peer("peer-1", deny_via="after-probe"), self.make_peer("peer-2")
        self.set_peers(("peer-1", True, "linux"), ("peer-2", True, "linux"))
        self.assertEqual(self.run_heavy("touch ran-job", remote=True), 0)
        self.assertFalse((stage_dir(peer1, self.repo) / "tree/ran-job").exists())
        self.assertTrue((stage_dir(peer2, self.repo) / "tree/ran-job").exists())
        self.make_peer("peer-only", deny_via="after-probe")
        self.set_peers(("peer-only", True, "linux"))
        self.assertEqual(self.run_heavy('test -z "${AGENT_HEAVY_JOBS:-}" && touch ran-fb', remote=True), 0)
        self.assertTrue((self.repo / "ran-fb").exists())

    def test_denying_host_falls_back_locally_with_deny_lifted_when_no_peer_answers(self):
        self.set_peers()
        res = subprocess.run([HEAVY, "--", 'test -z "${AGENT_HEAVY_JOBS:-}" && touch ran-fallback'],
                             cwd=self.repo, env={**self.env, "AGENT_HEAVY_JOBS": "deny"},
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(res.returncode, 0)
        self.assertTrue((self.repo / "ran-fallback").exists())
        self.assertTrue(any(line.startswith("heavy:") for line in res.stderr.splitlines()))

    # Local path

    def test_exit_status_argv_and_no_rerun_on_75(self):
        for code in (0, 3, 75, 255):
            with self.subTest(code=code):
                self.assertEqual(self.run_heavy(f"echo run >> runs-{code}; exit {code}"), code)
                self.assertEqual(len((self.repo / f"runs-{code}").read_text().splitlines()), 1)
        p = subprocess.Popen([HEAVY, "--", "touch", "my file"], cwd=self.repo, env=self.env,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.procs.append(p)
        self.assertEqual(p.wait(timeout=60), 0)
        self.assertTrue((self.repo / "my file").exists())
        self.assertEqual(self.run_heavy("touch a && touch b"), 0)
        self.assertTrue((self.repo / "b").exists())

    def test_a_job_past_the_cap_waits_for_a_slot(self):
        hold = "touch started-$N; while [ ! -e release ]; do sleep 0.05; done"
        holders = [self.start(hold.replace("$N", str(n))) for n in range(SLOTS)]
        for n in range(SLOTS):
            self.wait_for(self.repo / f"started-{n}")
        extra = self.start("touch started-extra")
        time.sleep(1.5)
        self.assertFalse((self.repo / "started-extra").exists())
        (self.repo / "release").touch()
        self.assertEqual([p.wait(timeout=30) for p in holders + [extra]], [0] * (SLOTS + 1))
        self.assertTrue((self.repo / "started-extra").exists())

    def test_unwritable_slot_lock_is_fatal_not_busy(self):
        ro_locks = self.root_tmp / "ro-locks"
        ro_locks.mkdir()
        slot1 = ro_locks / "slot-1.lock"
        slot1.touch()
        slot1.chmod(0o444)
        self.assertEqual(self.run_heavy("touch ran", HEAVY_LOCK_DIR=str(ro_locks)), FAILED)
        self.assertEqual(self.run_heavy("touch ran", remote=True, HEAVY_LOCK_DIR=str(ro_locks)), FAILED)
        self.assertFalse((self.repo / "ran").exists())

    def test_a_signal_kills_the_job_group_and_runs_cleanup(self):
        self.write(".heavy-cleanup", "touch cleaned\n")
        for signum in (signal.SIGTERM, signal.SIGINT):
            with self.subTest(signal=signum.name):
                for name in ("grandchild", "cleaned"):
                    (self.repo / name).unlink(missing_ok=True)
                proc = self.start("sleep 300 & echo $! > grandchild; wait")
                pid = self.pid_in(self.repo / "grandchild")
                proc.send_signal(signum)
                self.assertEqual(proc.wait(timeout=30), 128 + signum)
                self.assertFalse(alive(pid))
                self.assertTrue((self.repo / "cleaned").exists())

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
        wt = self.home / "linked"
        self.git("worktree", "add", "-q", str(wt))
        orig_git = (wt / ".git").read_text()
        job = 'mkdir -p "my dir" && touch "my dir/made file" ..dots && echo more >> tracked.txt'
        self.assertEqual(self.run_heavy(job, "--out", ".", "--out", "my dir/made file", "--out", ".git",
                                        "--out", "..", "--out", "missing", remote=True, cwd=wt), 0)
        self.assertTrue((wt / "my dir/made file").exists() and (wt / "..dots").exists())
        self.assertEqual(len((wt / "tracked.txt").read_text().splitlines()), 2)
        self.assertEqual((wt / ".git").read_text(), orig_git)

    def test_a_signal_and_group_kill_stop_remote_job_group_and_run_cleanup(self):
        self.write(".heavy-cleanup", "touch cleaned\n")
        for group_kill in (False, True):
            with self.subTest(group_kill=group_kill):
                for name in ("grandchild", "cleaned"):
                    (self.remote_tree / name).unlink(missing_ok=True)
                proc = self.start("sleep 300 & echo $! > grandchild; wait", remote=True, new_session=group_kill)
                pid = self.pid_in(self.remote_tree / "grandchild")
                (os.killpg if group_kill else os.kill)(proc.pid, signal.SIGTERM)
                self.assertEqual(proc.wait(timeout=30), 128 + signal.SIGTERM)
                self.assertFalse(alive(pid))
                self.assertTrue((self.remote_tree / "cleaned").exists())

    def test_a_grandchild_that_ignores_term_is_killed_after_grace(self):
        for kind, job, expected in [
            ("signal", "(trap '' TERM; sleep 60) & echo $! > {}; wait", 128 + signal.SIGTERM),
            ("normal", "(trap '' TERM; sleep 60) & echo $! > {}; exit 4", 4),
        ]:
            with self.subTest(kind=kind):
                remote, local = self.start(job.format(f"gr-{kind}"), remote=True), self.start(job.format(f"gl-{kind}"))
                rpid, lpid = self.pid_in(self.remote_tree / f"gr-{kind}"), self.pid_in(self.repo / f"gl-{kind}")
                if kind == "signal":
                    remote.send_signal(signal.SIGTERM)
                    local.send_signal(signal.SIGTERM)
                self.assertEqual([p.wait(timeout=40) for p in (remote, local)], [expected, expected])
                self.assertFalse(alive(rpid) or alive(lpid))

    def test_main_and_two_linked_worktrees_run_concurrently_with_isolated_refs(self):
        wt1, wt2 = self.home / "wt1", self.home / "wt2"
        self.git("worktree", "add", "-q", str(wt1))
        self.git("worktree", "add", "-q", str(wt2))
        self.write("precious", "keep\n", root=self.remote_home / "repo")
        p_main = self.start("git status --short && sleep 0.5", remote=True, cwd=self.repo)
        p_wt1 = self.start("git update-ref refs/heads/only-in-wt1 HEAD && sleep 0.5 && "
                           "git show-ref --verify refs/heads/only-in-wt1 && "
                           "! git show-ref --verify refs/heads/only-in-wt2", remote=True, cwd=wt1)
        p_wt2 = self.start("git update-ref refs/heads/only-in-wt2 HEAD && sleep 0.5 && "
                           "git show-ref --verify refs/heads/only-in-wt2 && "
                           "! git show-ref --verify refs/heads/only-in-wt1", remote=True, cwd=wt2)
        self.assertEqual([p.wait(timeout=60) for p in (p_main, p_wt1, p_wt2)], [0, 0, 0])
        self.assertTrue((self.remote_home / "repo/precious").exists())

    def test_staging_refuses_symlinked_parents_or_paths_outside_staging_root(self):
        outside = self.root_tmp / "outside"
        self.write("precious", "keep\n", root=outside)
        (self.remote_home / ".cache/heavy").mkdir(parents=True, exist_ok=True)
        work_link = self.remote_home / ".cache/heavy/work"
        work_link.symlink_to(outside)
        self.assertEqual(self.run_heavy("touch ran", remote=True), FAILED)
        self.assertTrue((outside / "precious").exists() and not (outside / "ran").exists())
        work_link.unlink()
        sdir = stage_dir(self.remote_home, self.repo)
        sdir.mkdir(parents=True, exist_ok=True)
        (sdir / "tree").symlink_to(outside)
        self.assertEqual(self.run_heavy("touch ran", remote=True), FAILED)
        self.assertTrue((outside / "precious").exists() and not (outside / "ran").exists())

    def test_queued_job_skips_peer_if_deny_turns_on_while_waiting_for_slot(self):
        peer1, peer2 = self.make_peer("peer-1"), self.make_peer("peer-2")
        self.set_peers(("peer-1", True, "linux"), ("peer-2", True, "linux"))
        wt = self.home / "queued-wt"
        self.git("worktree", "add", "-q", str(wt))
        rlocks = self.root_tmp / "queued-rlocks"
        rlocks.mkdir()
        held = []
        for n in range(1, SLOTS + 1):
            f = (rlocks / f"slot-{n}.lock").open("w")
            fcntl.flock(f, fcntl.LOCK_EX)
            held.append(f)
        try:
            proc = self.start("touch ran-queued", remote=True, cwd=wt, HEAVY_LOCK_DIR=str(rlocks))
            git_file = stage_dir(peer1, wt) / "tree/.git"
            deadline = time.monotonic() + 20
            while not (git_file.exists() and ".cache/heavy/work/" in git_file.read_text()):
                self.assertLess(time.monotonic(), deadline, "queued job never reached slot wait")
                time.sleep(0.05)
            self.write(".config/environment.d/60-agent-heavy-jobs.conf", "AGENT_HEAVY_JOBS=deny\n", root=peer1)
        finally:
            for f in held:
                f.close()
        self.assertEqual(proc.wait(timeout=30), 0)
        self.assertFalse((stage_dir(peer1, wt) / "tree/ran-queued").exists())
        self.assertTrue((stage_dir(peer2, wt) / "tree/ran-queued").exists())

    def test_retry_waits_for_remote_cleanup_after_client_kill(self):
        proof, release = self.root_tmp / "cleanup-saw-marker", self.root_tmp / "release-cleanup"
        self.write("marker", "keep\n")
        self.write(".heavy-cleanup", f"touch cleanup-started\nwhile [ ! -e {release} ]; do sleep 0.05; done\n"
                                     f"test -e marker && touch {proof}\n")
        first = self.start("sleep 300 & echo $! > started; wait", remote=True)
        self.wait_for(self.remote_tree / "started")
        first.kill()
        first.wait(timeout=10)
        self.wait_for(self.remote_tree / "cleanup-started")
        (self.repo / "marker").unlink()
        retry = self.start("touch retry-ran", remote=True)
        time.sleep(1.0)
        self.assertTrue((self.remote_tree / "marker").exists() and not (self.remote_tree / "retry-ran").exists())
        release.touch()
        self.assertEqual(retry.wait(timeout=30), 0)
        self.assertTrue(proof.exists() and (self.remote_tree / "retry-ran").exists())
        self.assertFalse((self.remote_tree / "marker").exists())

    def test_cancel_during_upload_reaps_rsync_before_releasing_staging_lock(self):
        started, reaped = self.root_tmp / "up-started", self.root_tmp / "up-reaped"
        slow_ssh = self.make_slow_ssh(
            "slow-up",
            f'if [[ "$*" == *"--server"* && "$*" != *"--sender"* ]] && [ ! -e {started} ]; then '
            f'trap "" USR1; trap "sleep 0.4; touch {reaped}; exit 143" TERM; '
            f'touch {started}; while :; do sleep 0.05; done; fi',
        )
        first = self.start("touch first-ran", remote=True, HEAVY_SSH=slow_ssh)
        self.wait_for(started)
        first.send_signal(signal.SIGTERM)
        retry = self.start(f"test -e {reaped} && touch retry-ran", remote=True)
        self.assertEqual(first.wait(timeout=30), 128 + signal.SIGTERM)
        self.assertEqual(retry.wait(timeout=30), 0)
        self.assertTrue(reaped.exists() and (self.remote_tree / "retry-ran").exists())
        self.assertFalse((self.remote_tree / "first-ran").exists())

    def test_group_sigkill_during_upload_kills_rsync_so_retry_files_survive(self):
        started, release, pid_file = self.root_tmp / "gk-started", self.root_tmp / "gk-release", self.root_tmp / "gk-pid"
        self.write("old-file", "old\n")
        slow_ssh = self.make_slow_ssh(
            "slow-gk",
            f'if [[ "$*" == *"--server"* && "$*" != *"--sender"* ]]; then echo $$ > {pid_file}; touch {started}; '
            f'while [ ! -e {release} ]; do sleep 0.05; done; fi',
        )
        first = self.start("touch first-ran", remote=True, new_session=True, HEAVY_SSH=slow_ssh)
        ssh_pid = self.pid_in(pid_file)
        self.wait_for(started)
        os.killpg(first.pid, signal.SIGKILL)
        first.wait(timeout=10)
        self.assertFalse(alive(ssh_pid))
        (self.repo / "old-file").unlink()
        self.write("retry-file", "keep\n")
        release.touch()
        self.assertEqual(self.run_heavy("test -e retry-file && test ! -e old-file && touch retry-ran", remote=True), 0)
        self.assertTrue((self.remote_tree / "retry-file").exists() and (self.remote_tree / "retry-ran").exists())

    def test_sigkill_heavy_pid_only_during_upload_does_not_clobber_retry(self):
        sdir = stage_dir(self.remote_home, self.repo)
        for hold_upload_lock in (False, True):
            with self.subTest(hold_upload_lock=hold_upload_lock):
                tag = "held" if hold_upload_lock else "late"
                started, release = self.root_tmp / f"sk-{tag}-s", self.root_tmp / f"sk-{tag}-r"
                pid_file = self.root_tmp / f"sk-{tag}-p"
                self.write("old-file", "old\n")
                (self.repo / "retry-file").unlink(missing_ok=True)
                lock_cmd = f"exec 6>{sdir}/upload.lock; flock 6; " if hold_upload_lock else ""
                slow_ssh = self.make_slow_ssh(
                    f"slow-sk-{tag}",
                    f'if [[ "$*" == *"--server"* && "$*" != *"--sender"* ]]; then '
                    f'echo $$ > {pid_file}; {lock_cmd}touch {started}; '
                    f'while [ ! -e {release} ]; do sleep 0.05; done; '
                    f'exec 6>&-; fi',
                )
                first = self.start("touch first-ran", remote=True, HEAVY_SSH=slow_ssh)
                ssh_pid = self.pid_in(pid_file)
                self.wait_for(started)
                first.kill()  # SIGKILL heavy's PID only: rsync + slow_ssh survive
                first.wait(timeout=10)
                self.assertTrue(alive(ssh_pid))
                (self.repo / "old-file").unlink()
                self.write("retry-file", "keep\n")
                retry = self.start("test -e retry-file && test ! -e old-file && touch retry-ran", remote=True)
                if hold_upload_lock:
                    time.sleep(0.5)
                    self.assertIsNone(retry.poll())  # waits for surviving receiver's upload.lock
                    release.touch()
                    self.assertEqual(retry.wait(timeout=30), 0)
                else:
                    self.assertEqual(retry.wait(timeout=30), 0)
                    release.touch()  # surviving old rsync arrives late and must be rejected
                deadline = time.monotonic() + 10
                while alive(ssh_pid) and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertTrue((self.remote_tree / "retry-file").exists())
                self.assertFalse((self.remote_tree / "old-file").exists())

    def test_closed_stderr_exits_0_not_120(self):
        for remote in (False, True):
            with self.subTest(remote=remote):
                env = {**self.env}
                if remote:
                    env.update(AGENT_HEAVY_JOBS="deny", HEAVY_LOCK_DIR=str(self.root_tmp / "remote-locks"))
                p = subprocess.Popen([HEAVY, "--", "sleep 0.2"], cwd=self.repo, env=env,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                self.procs.append(p)
                p.stderr.readline()
                p.stderr.close()
                self.assertEqual(p.wait(timeout=30), 0)

    def test_out_copy_back_holds_staging_lock_against_next_run(self):
        started, release = self.root_tmp / "cb-started", self.root_tmp / "cb-release"
        slow_ssh = self.make_slow_ssh(
            "slow-cb",
            f'if [[ "$*" == *"--sender"* ]]; then touch {started}; while [ ! -e {release} ]; do sleep 0.05; done; fi',
        )
        first = self.start("echo first-bytes > artifact", "--out", "artifact", remote=True, HEAVY_SSH=slow_ssh)
        self.wait_for(started)
        second = self.start("echo second-bytes > artifact", remote=True)
        time.sleep(1.0)
        release.touch()
        self.assertEqual([first.wait(timeout=30), second.wait(timeout=30)], [0, 0])
        self.assertEqual((self.repo / "artifact").read_text(), "first-bytes\n")
        self.assertEqual((self.remote_tree / "artifact").read_text(), "second-bytes\n")


if __name__ == "__main__":
    unittest.main()
