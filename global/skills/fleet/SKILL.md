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
* Run remote commands with `tailscale ssh abdulrahman@msi-dux "bash -lc '<command>'"`. Its login shell is fish, so `bash -l` loads the login PATH (`~/.local/bin`, Nix).
* For long jobs there, run `agent-wait` on `msi-dux` itself (see `agent-wait --help`).
* `msi-dux` runs T3 as a headless background service. Its desktop app can't start while the service runs, so open its threads from the laptop.
