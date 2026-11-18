# Common rules for every worker

Paste this block at the top of every brief, then fill the fields in angle brackets
that apply. Delete fields and rules that can't apply at this stage (for example, the
lab rules in a book without a lab, or the PDF before one exists). The blind reader
gets none of the repository fields; see `blind-read.md`.

---

## The book

- Repository: `<REPO>`, branch or revision `<BRANCH>`. Prose is in `<BOOK_DIR>`, labs in
  `<LAB_DIR>`, tests in `<TEST_DIR>`.
- Reader, goals and scope: read `<PLAN_FILE>` first. Every sentence you add serves one
  of its goals.
- Current PDF, for page references: `<PDF_PATH>`.
- Primary sources and how to read them: `<SOURCES>`. Read large texts with `grep -n`
  and `sed -n` ranges; never print them whole and never copy them into the repository.

## Ownership

- Edit only these files: `<YOUR_FILES>`. If a change belongs in another file, don't
  make it. List it in your report with the exact text.
- Never edit checks, the verifier, build tools, or tests you weren't asked to write,
  to make your output pass. Change them only if this brief assigns that work. If one
  looks wrong, stop and report it.
- Don't commit, push, or rebuild the PDF unless this brief says so.

## Running the lab

```
<LAB_SETUP: the command that gives you your own isolated database or environment>
```

- Use your own database for every run, so you never collide with other workers. When
  a probe depends on server-wide state (system views, replication, global settings),
  use your own server.
- Recheck a chapter's printed commands with `<VERIFY_CHAPTER_COMMAND>`.
- Run the whole test suite once from fresh state before you report, because tests
  can pass alone and fail together.

## Standards

- Every printed command and output comes from a real run you did. Trim output, but
  never edit a line you keep. If you didn't run something, describe it without quoting
  output.
- Every claim about a tool, standard or author is checked against a primary source:
  official documentation at the version the book names, the specification, the
  original text. Your memory and blog posts are leads, not sources. Put the source in
  your report.
- A claimed guarantee (a lock holds, a retry is safe, a cache stays fresh) needs a test
  that runs the interleaving that would break it and checks database or observable
  state. Never assert exact output strings in tests.
- In labs, wait on observable state (a row, a lock in a system view), never on sleeps
  or thread timing. Scope environment changes to the test or subprocess that needs
  them; never set them at module level.
- No Python or other scripting languages embedded in shell scripts; write a separate
  file.
- Prose: match the voice of `<MODEL_CHAPTER>`. Plain and direct, takes positions. No em
  dashes or en dashes used as dashes. No filler, recaps or announcements. One term per
  concept, matching the book's glossary. They/them for people.

## Running long jobs

Don't end your turn while a job you started is still running; nobody will see it
finish. `<WAIT_STEPS: the literal commands to start a long job and wait for it>`

## Delegation and cleanup

- Don't delegate. `<OR: you may delegate only to these models, which cost the same as
  you or less: ...>`
- Put scratch files under `<SCRATCH_DIR>`. When done, delete probes and temporary
  copies, drop your databases and stop any server you started. Keep any handoff file
  this brief asks for.

## Report

End your turn with one message containing everything:

1. What you changed, as `file:line`, and why each change is correct.
2. The verification you ran and its result (verify counts, test pass or fail).
3. Edits needed in files you don't own, with exact text.
4. Anything in the brief you disagree with, with evidence.
5. Anything still running or unfinished.
