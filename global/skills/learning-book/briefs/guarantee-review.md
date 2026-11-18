# Guarantee review brief

For a strong reasoning model within the agreed budget, checking whether the book's
guarantees hold. Read only. Start the brief with `common.md`, keeping the book, lab,
long-job, cleanup and report parts and dropping ownership.

When to use it:

- Before a risky lab or worked design is built: ask what interleaving, crash or retry
  would break the planned design.
- Once labs run: reproduce those scenarios against the real code.
- After each fix round: send the diff and the reviewer's own findings back to the same
  reviewer. Fixes create new races near the old ones.

A whole book takes several turns. Plan them in one thread, give each turn its range, and
track coverage until every range has a report.

---

Read-only correctness review of `<SCOPE>`. Don't edit, commit or push, and don't
delegate. Your final message is the report.

The book: `<ONE PARAGRAPH: reader, goals, scope, stack and versions>`. PDF, if one
exists: `<PDF_PATH>` (cite its pages). Sources at revision `<REVISION>`.
`<FOR A DESIGN NOT YET BUILT: the plan section to review>`
`<FOR A RECHECK: your earlier findings, which ones were fixed, and the changed scope>`

## What to check

Every guarantee the book or its labs claim, such as isolation, locking, idempotency,
ordering, delivery, cache freshness, or a change that doesn't block. For each, ask what
interleaving, crash or retry would break it, and try that against the lab or an
isolated probe. Include worked designs and sample pages, not only labs.

Also check printed code and output, technical claims about `<TOOLS_AND_VERSIONS>`, and
whether new text contradicts unchanged text.

For a design not yet built, report the breaking scenario and the observable result
you expect; once it runs, report the probe and the actual result.

## Stop rule

A finding counts only with a reproduction (a lab run or probe, with its output) or a
cited primary source showing the reader is misled. Report BLOCKER and MAJOR only. Prose
and flow are out of scope. Say "none" if nothing meets the bar.

## Report

Findings most severe first: tag, location (PDF page, or plan section) and quoted
phrase, `file:line` where it applies, the problem,
the reproduction or source, and the simplest correct fix. Then the ranges you did not
cover and the claims you could not run.
