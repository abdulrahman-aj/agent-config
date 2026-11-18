# Fix-round brief

For a worker fixing review findings. Start the brief with `common.md`.

How to fill it in:

- Give each finding verbatim with its page, the reviewer's evidence and the source link.
  Group findings by file so two workers never own the same file.
- Say which findings you already checked and agree with, and which the worker should
  check first.
- When another worker's change affects this one, say what it changes, in one sentence.

---

Fix these review findings in `<YOUR_FILES>`. Check each one before fixing it: a finding
is a claim, and reviewers are sometimes wrong. If you disagree, don't fix it; report
why, with evidence.

`<FINDINGS: id, page, file:line, what is wrong, the reviewer's evidence, source links,
the fix direction you agree with>`

## How to fix

- Find the simplest correct fix. One SQL statement beats a retry loop. Prefer replacing
  text to adding it, and keep the chapter about the same length.
- Check your fix for the same class of bug, not only the reported instance. A fix that
  reintroduces the bug in a new form is common.
- Keep the author's voice. Don't hedge a claim the book can support ("may", "in some
  cases"), and don't cut an explanation to make a finding go away. If a paragraph has to
  go, say in the report what it taught and where that now lives.

## Proving a fix to a guarantee

1. Add a regression test that calls the lab's real function, not its own copy of the
   SQL, and runs the interleaving the finding describes.
2. Run a negative control: copy the lab to `<SCRATCH_DIR>/<YOUR_NAME>/nc/` without
   `<HEAVY_DIRS, for example .venv, the database directory, node_modules>`, revert only
   the mechanism under test, and show the test fails for the right reason. A control
   that still passes, or fails for another reason, proves nothing.
3. Delete the copy and stop its database when done.
4. Paste fresh lab output into the book, rerun `<VERIFY_CHAPTER_COMMAND>`, then the whole
   suite in a fresh database.

## Report additions

For each finding: fixed, or not fixed and why. For each guarantee: the test name and the
negative control's failing output.
