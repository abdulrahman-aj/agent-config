# Guarantee review brief

For the strongest reasoning model available, checking whether the book's guarantees
actually hold. Run it early, after the first labs exist, and again on each round's diff.
Read only.

How to fill it in:

- A whole book takes several turns. Plan them in one thread: first report, then the rest
  of the pages, then any audit against the source. Ask for explicit "not covered" ranges.
- Give it the lab commands so every finding can come with a reproduction.
- After fixes, send it the diff and its own findings to recheck, in the same thread. Fixes
  create new races near the old ones.

---

Read-only correctness review of `<SCOPE>`. Don't edit, commit or push, and don't
delegate. Your final message is the report.

The book: `<ONE PARAGRAPH: reader, goals, scope, stack and versions>`. PDF:
`<PDF_PATH>` (cite its pages). Sources: `<REPO>`, branch `<BRANCH>`.

## What to check

Every guarantee the book or its labs claim: locks, isolation, idempotency, ordering,
exactly-once or at-least-once delivery, cache freshness, migrations that don't block.
For each, ask what interleaving, crash or retry would break it, and try that interleaving
against the lab. Include the worked designs and sample pages, not only the labs.

Also check printed SQL and output, technical claims about `<TOOLS_AND_VERSIONS>`, and
whether new text contradicts unchanged text.

## Stop rule

A finding counts only with a reproduction (a lab run or probe script, with its output) or
a cited primary source showing the reader is misled. Report BLOCKER and MAJOR only. Prose
and flow are out of scope. Say "none" if nothing meets the bar.

## Running the lab

```
<DB_SETUP_COMMAND with your own database>
```

Throwaway files go under `<SCRATCH_DIR>/<YOUR_NAME>/`; delete them when done.

## Report

Findings most severe first: tag, PDF page and quoted phrase, `file:line`, the problem, the
reproduction or source, and the simplest correct fix. Then the page ranges you did not
cover, and at most five lines on what you could not check.
