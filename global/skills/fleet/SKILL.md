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
* Run a build or test from a git worktree with `heavy -- <command>` (see `heavy --help`). It copies the worktree, uncommitted edits included, to the same path on `msi-dux`, runs the job there with at most three jobs at once, and exits with the job's status. If `msi-dux` doesn't answer, heavy runs the job on the laptop, two at once, but only with `--local-ok`. Pass a shell command line as one quoted word, as in `heavy -- 'cd lab && make'`. `--out <path>` copies a result back.
* A repo can list rsync excludes in `.heavyignore`, and heavy runs `.heavy-cleanup` after each job, for example to stop a database the job started.
* For long jobs, run `agent-wait --start --log <log> -- heavy -- <command>`. Killing the agent-wait group stops the job on `msi-dux` too.
* Run other remote commands with `tailscale ssh abdulrahman@msi-dux "bash -lc '<command>'"`. Its login shell is fish, so `bash -l` loads the login PATH (`~/.local/bin`, Nix). For a long job started that way, run `agent-wait` on `msi-dux` itself.
* `msi-dux` runs T3 as a headless background service. Its desktop app can't start while the service runs, so open its threads from the laptop.
