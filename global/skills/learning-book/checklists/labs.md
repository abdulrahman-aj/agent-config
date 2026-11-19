# Lab checklist

## Verification

- `make verify` replays every printed command and compares its output and exit status;
  declare the expected status of each intentional failure. On a mismatch, save the
  command, status and raw output: a "flake" was often a real difference nobody kept.
- Replay commands the way the reader's setup does, through `make`, with `MAKELEVEL`
  and `MAKEFLAGS` stripped. A nested make printed "Entering directory" lines that
  failed only through make and looked like a flake.
- Before a release, and after setup changes, verify from a fresh clone and a fresh
  database cluster, following the book's printed setup, companion labs included.
  Leftover state hid a broken setup step. Once, follow the setup prose by hand as a
  reader would.
- Keep the linters and type checkers editors run by default (such as ruff and
  basedpyright standard) at zero, configured at the repository root, and run them and a
  check that quoted code matches its lab file in `make verify`.

## Tests

- Concurrency labs wait on observable state, such as a blocked backend in
  `pg_stat_activity`, never on sleeps or thread liveness. To force an interleaving,
  drive both sessions step by step from one thread.
- A test calls the lab's real function, not its own SQL. Tests that ran their own SQL
  passed on the old, wrong behavior.
- Run the whole suite from a fresh database after each worker batch: files that pass
  alone can fail together.
- When a review reproduces a bug, keep the scenario as a regression test, and consider
  making it an exercise.

## Parallel lab PRs

- After merging one, rebase the others and rerun `make verify`. Shared registrations
  (Makefile targets, verifier patterns) conflict, and shared schemas break silently: a
  column made `NOT NULL` in one lab broke another lab's insert.

## What the book prints

- Print the lines that make the point; the plumbing stays in the lab.
- Don't print a short implementation as "the pattern" when real ones are large and
  subtle (one real stale-while-revalidate library passed 300 lines). Show what the lab
  demonstrates, list the hard parts as what to demand of a library, and point to a
  maintained one.
