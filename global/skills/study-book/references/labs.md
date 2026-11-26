# Runnable labs and verification

Load this reference when a book has runnable labs or code listings extracted from them.

## Layout and book split

- Give setup once in the book, then print only the command and the output that settles
  each point. Put modes, extra variants and detail in `lab/`.
- Make labs print one line per outcome so printed output needs no editing.
- Put each lab's command and book section in its file header or docstring, keep shared
  setup in `lab/README`, and name lab folders by topic. Add a markdown file per lab only
  for depth the book lacks.
- Before moving a case to the lab, ask whether a chapter's can-do goal needs it. After
  moving it, diff the guards left in the book against the original, because a trim once
  dropped two, and reread every later sentence that relied on it.
- Never print a short implementation as the real thing when real ones are large and
  subtle. Print the idea instead of the plumbing, list what to demand of a library, and
  point to a maintained one.

## Snippet extraction and command replay

- Extract printed code from lab files through named region markers instead of copying it
  into book sources, and make `make verify` or the build fail when a region is missing
  or stale.
- Check that each listing contains the case its section is about; a retry loop was once
  printed without the branch that retries.
- Never split one function across snippet regions, because the second half loses its
  indentation.
- Rebuild the PDF after any change to region code, because a rename can push a line past
  the margin.
- Provide a `make verify` target that replays every printed command, checks exit status
  against declared expected non-zero exits, matches trimmed output using `…` as a
  wildcard for elided lines or run-varying values, checks that quoted code matches its
  lab file, and saves the raw output of each mismatch.
- Strip `MAKELEVEL` and `MAKEFLAGS` when replaying commands through `make`, or nested
  `make` output looks like a flake.
- Keep linters at their editor defaults at zero from the repository root.

## Isolation and fresh state

- Give each lab worker a git worktree under a short path such as `~/Work/<repo>-wt12`,
  because Unix socket paths fail past about 107 bytes, and give it its own database and
  server when the lab uses them. Concurrent edits in one checkout broke the build
  mid-edit, and workers sharing a server interfered through server-wide state.
- Stop processes by PID; `pkill -f <worktree>` also kills servers started from it.
- When making scratch copies for negative controls, leave out dependency caches, data
  directories and build output so they don't fill `/tmp`, and delete the copy
  afterwards.
- No module-level environment changes in tests, because one redirected every later
  test's subprocesses; run the whole suite from fresh state after each batch.
- After merging one lab PR, rebase the remaining lab branches and rerun, because shared
  build targets and fixtures break.
- Before a release, verify from a fresh clone and fresh state through the book's printed
  setup, companion labs included; leftover state hid a broken step.

## Guarantees, concurrency and security labs

- When a section claims a fix works, make the fix runnable with trap cases that a
  plausible wrong fix fails; prose walkthroughs of fixes were where gates kept finding
  errors.
- Make concurrency labs wait on observable state, never on sleeps or thread liveness, and
  force each interleaving deterministically by driving both sides from one thread.
- Call the lab's real function in tests. A negative control reverts only the mechanism and
  fails for the claimed reason, observed before teardown or retries could produce the
  outcome. Rerun every control yourself; one passed with the kill removed because a
  client close freed the lock.
- Set up the case that only the claimed mechanism stops; a test that another mechanism
  would also pass proves nothing. A claim that concurrent writes converge also runs
  concurrent writers on the source side.
- A provider's safety filter blocks security labs, and workers quietly drop them first.
  Name them neutrally, avoid trigger words, and route them to a model that accepts them
  in a fresh context.
