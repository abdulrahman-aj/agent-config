---
name: automate-friction
description: Use when automating repeated manual work or reducing noisy command output.
---

- Review recent work for repeated commands, noisy output, and manual steps.
- Name the observed friction and choose the smallest useful fix.
- Reuse the project's tooling and conventions; ask before adding dependencies or changing shared workflows.
- Keep successful output concise, failure diagnostics complete, and live output available.
- For noisy commands, consider the bundled `scripts/quiet`; the `Makefile` is an optional integration example.
- Verify the fix preserves behavior and reduces the observed friction.
- Document recurring conventions in `AGENTS.md` when useful.
