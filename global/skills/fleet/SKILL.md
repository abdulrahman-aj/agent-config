---
name: fleet
description: Machine specs, SSH and VM rules for zenbook-dux and msi-dux. Load before running builds, VMs, long-running jobs or commands on msi-dux.
---

# Fleet

| Machine | Hardware | Use for | Access |
|---|---|---|---|
| `zenbook-dux` (laptop) | 22 cores, 14 GiB RAM | Orchestration and light work, no VMs | Local, primary T3 host; shows `msi-dux` threads |
| `msi-dux` (PC) | 16 cores, 30 GiB RAM, 2 GPUs | All VM work and long-running jobs, up to three 8 GiB VMs | T3 environment `msi-dux`, or `tailscale ssh abdulrahman@msi-dux` |

* Run builds, VMs and other long-running work on `msi-dux`, because it stays up when the laptop lid closes. Keep the laptop for work specific to it, such as dotfiles tests or its own services.
* The laptop sets `AGENT_HEAVY_JOBS=deny`, and heavy make targets (such as arch-niri-dux builds and VMs) refuse to run while it is set. Check free RAM on `msi-dux` before starting a VM.
* Run a build or test from a git worktree with `heavy -- <command>` (see `heavy --help`). On a host with `AGENT_HEAVY_JOBS=deny`, it finds an eligible online Linux peer in Tailscale, stages the worktree under `~/.cache/heavy/work` there (uncommitted edits included), runs the job with a RAM-based slot cap, and exits with the job's status; if no peer answers, it falls back locally with the deny lifted for that job. On a non-denying host, it always runs locally. Pass a shell command line as one quoted word, as in `heavy -- 'cd lab && make'`. `--out <path>` copies a result back.
* A repo can list rsync excludes in `.heavyignore`, and heavy runs `.heavy-cleanup` after each job, for example to stop a database the job started.
* For long jobs, run `agent-wait start LOG -- heavy -- <command>`, then `agent-wait wait LOG`. `agent-wait stop LOG` stops a remote job too.
* Run remote commands with `tailscale ssh abdulrahman@msi-dux '<command>'`. They run in a Bash login shell, so `~/.local/bin`, Nix and mise tools are on PATH.
* For long jobs there, run `agent-wait start LOG -- CMD`, `agent-wait wait LOG`, and `agent-wait stop LOG` on `msi-dux` itself (see `agent-wait --help`).
* `msi-dux` runs T3 as a headless background service. Its desktop app can't start while the service runs, so open its threads from the laptop.
