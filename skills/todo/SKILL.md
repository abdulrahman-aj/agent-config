---
name: todo
description: Use when selecting and executing tasks from the project's TODO.md.
---

- `/todo` — work the next unchecked task (or next logical group).
- `/todo <hint>` — find the task best matching the hint, confirm the match, then work it.
- `/todo add <description>` — append under the most relevant section (ask if unclear); confirm.

If `TODO.md` doesn't exist or has no unchecked tasks, say so and stop.

**NEVER skip these steps:**
1. Implement and verify while leaving the task listed.
2. After verification, ask the user to confirm completion; only then remove it.

Removing tasks requires explicit user approval.
