# Fix-round brief

For a worker fixing review findings. Start the brief with `common.md`.

How to fill it in:

- Give each finding verbatim with its location and whatever evidence the reviewer
  gave. Group findings by file so two workers never own the same file.
- Say which findings you already checked and agree with, and which the worker should
  check first.
- When another worker's change affects this one, say what it changes, in one sentence.

---

Fix these review findings in `<YOUR_FILES>`. Check each one before fixing it: a finding
is a claim, and reviewers are sometimes wrong. If you disagree, don't fix it; report
why, with evidence.

`<FINDINGS: id, location, what is wrong, the reviewer's evidence, the fix direction you
agree with>`

## How to fix

- Choose the smallest correct fix that keeps the teaching. A single atomic statement
  beats a retry loop around several. Prefer replacing text to adding it, and keep the
  chapter about the same length.
- Check your fix for the same class of bug, not only the reported instance. A fix that
  reintroduces the bug in a new form is common.
- Keep the author's voice. Don't hedge a claim the book can support ("may", "in some
  cases"), and don't cut an explanation to make a finding go away. If a paragraph has
  to go, say in the report what it taught and where that now lives.
- After narrowing a claim, reread the whole paragraph and its neighbors: fix dangling
  referents and choppy sentences, and rewrap to the source's line width.
- Never resolve an unverified failure demonstration by deleting it. Make it replay, or
  report the blocker.
- Every new technical claim in your fix needs its own source or run.

## Proving a fix to a guarantee

1. Add a regression test that calls the lab's real function, not its own copy of the
   logic, and runs the interleaving the finding describes. Observe the outcome before
   teardown, retries or cleanup could produce it.
2. Run a negative control in an isolated copy or environment: revert only the mechanism
   under test and show the test fails for the reason it claims. A control that still
   passes, or fails for another reason, proves nothing. Leave heavy directories (virtual
   environments, database files, node_modules) out of any copy, and delete it after.
3. When the lab's output changed, paste the fresh output into the book and rerun
   `<VERIFY_CHAPTER_COMMAND>`. Rerun the affected tests.

## Report additions

For each finding: fixed, or not fixed and why. For each guarantee: the test name and the
negative control's failing output.
