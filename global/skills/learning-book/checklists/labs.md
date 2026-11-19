# Lab checklist

Use this before setting up or drafting the first lab, and before accepting any lab change.

## Verification

- `make verify` replays the printed commands and compares output and exit status. Labs
  print one line per outcome so the book can quote output directly.
- A fresh-clone run (`release.md` says when) uses fresh lab state and follows the
  book's printed setup through the documented entry point, companion labs included.
- Give replayed commands the environment a reader has after setup, and declare the
  expected exit status of each intentional failure.
- On a mismatch, save the command, exit status and raw output.
- The verifier replays commands, not the instructions around them. Follow the printed
  setup prose literally once, as a reader would, and fix any step that contradicts
  another.

## Code quality

- Keep the linters and type checkers that editors run by default at zero findings, such
  as ruff and basedpyright in standard mode for Python.
- Put their configuration at the repository root, where an editor opening the
  repository finds it.
- Run them and the formatter check in `make verify`, and check that every code block
  the book quotes still matches its lab file.

## Guarantees and tests

- A lab that proves a guarantee runs the breaking scenario. When it claims
  convergence, that includes concurrent writers.
- Make concurrency labs deterministic. Wait on observable state, such as a blocked
  backend in `pg_stat_activity`, never on sleeps or thread timing. To force an
  interleaving, drive both sessions step by step from one thread.
- Test the lab's real code and show that the test fails with the mechanism removed.
- The verifier checks printed transcripts. Tests assert behavior, including output only
  where output is the interface.
- Root-cause every flaky result.
- When a review reproduces a bug, keep the scenario as a regression test, and consider
  turning it into an exercise.

## Parallel work

- Give each worker writing prose or labs its own git worktree under a short path, such
  as `~/Work/<repo>-wt12`. A PostgreSQL socket path longer than 107 bytes fails, and
  deep scratch directories cross that.
- Stop a worker's processes by PID, never with `pkill -f <worktree path>`: the pattern
  also matches that worktree's database server.
- After merging one PR, rebase the others and rerun `make verify`. Shared registrations
  (Makefile targets, verifier patterns) conflict, and shared schemas break silently: a
  column made NOT NULL in one lab breaks another lab's insert.

## What the book prints

- Keep printed code to the idea; the rest stays in the lab.
- Don't print a short implementation as "the pattern" when it hides failure modes that
  matter in production. Show what the lab demonstrates, list the hard parts as what to
  demand of a library, and point to a maintained one.
