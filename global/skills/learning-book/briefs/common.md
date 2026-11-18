# Common rules for every worker

Paste this block at the top of every brief, after filling each `<PLACEHOLDER>`. Delete a
rule only when it cannot apply (for example, the database rules in a book without a lab).

---

## The book

- Repository: `<REPO>`, branch `<BRANCH>`. Prose is in `<BOOK_DIR>`, labs in `<LAB_DIR>`,
  tests in `<TEST_DIR>`.
- Reader and goals: read `<PLAN_FILE>` first. Every sentence you add serves one of its
  goals.
- Current PDF, for page references: `<PDF_PATH>`.
- Source material: `<SOURCE_PATH>`. Read it in place with `grep -n` and `sed -n` ranges;
  never print it whole and never copy it into the repository.

## Ownership

Other workers may edit this checkout at the same time.

- Edit only these files: `<YOUR_FILES>`. If a change belongs in another file, don't make
  it. List it in your report with the exact text.
- Never edit checks, tests you were not asked to write, the verifier, or build tools to
  make your output pass. If one of them looks wrong, stop and report it.
- Don't commit, push, or rebuild the PDF unless this brief says so.

## Your own database

Use your own database for every run, so you never collide with other workers:

```
<DB_SETUP_COMMAND with <YOUR_DB>>
```

Recheck a chapter's printed commands with `<VERIFY_CHAPTER_COMMAND>`. Run the whole test
suite once in a fresh database before you report, because tests can pass alone and fail
together.

## Standards

- Every printed command and output comes from a real run you did. Trim output, but never
  edit a line you keep. If you did not run something, describe it without quoting output.
- Every claim about a tool, standard or author is checked against a primary source:
  official documentation at the version the book names, the specification, the original
  text. Your memory and blog posts are leads, not sources. Put the source in your report.
- A claimed guarantee (a lock holds, a retry is safe, a cache stays fresh) needs a test
  that runs the interleaving that would break it and checks database or observable state.
  Never assert exact output strings in tests.
- In labs, wait on observable state (a row, a lock in a system view), never on sleeps or
  thread timing. Never set environment variables at module level in a test file.
- No Python or other scripting languages embedded in shell scripts; write a separate file.
- Prose: plain, direct, first person, takes positions. No em dashes or en dashes used as
  dashes. No filler, recaps or announcements. One term per concept, matching the book's
  glossary. They/them for people.

## Running long jobs

Don't end your turn while a job you started is still running; nobody will see it finish.
`<WAIT_INSTRUCTIONS, for example: start with agent-wait --start --log <log> -- <command>,
then repeat agent-wait --pid <pid> --log <log> until it stops exiting 124>`

## Cost and cleanup

- Delegate only to models that cost the same as you or less, or not at all: `<ALLOWED>`.
- Put scratch files under `<SCRATCH_DIR>/<YOUR_NAME>/`. Delete them, drop your databases
  and stop any server you started before you report.

## Report

End your turn with one message containing everything:

1. What you changed, as `file:line`, and why each change is correct.
2. Every command you ran and its result (verify counts, test pass or fail).
3. Edits needed in files you don't own, with exact text.
4. Anything in the brief you disagree with, with evidence.
