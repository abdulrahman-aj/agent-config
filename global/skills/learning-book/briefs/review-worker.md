# Reviewing a worker's result

A checklist for whoever briefed the worker. Workers report success they didn't verify,
so check the work, not the report.

1. Read the diff to checks, tests, the verifier and build tools first. Revert any change
   that makes a check pass instead of making the work correct.
2. Rerun every negative control yourself. It must revert only the mechanism under test
   and fail for the reason the test claims.
3. Delete tests that assert printed output; the verifier already covers transcripts.
4. Rerun the chapter's printed commands with the verifier, then the whole test suite in
   a fresh database. Root-cause every failure; "flaky under load" is not a cause.
5. Read the prose diff line by line, not as a skim:
   - sentences copied from the brief or spec;
   - hedges that weaken a claim the book can support;
   - explanations that were cut, and positions that were dropped;
   - mannered lines, recaps, and new terms for existing concepts;
   - wrong technical asides, which cluster in new text.
6. Ask whether the fix is the simplest correct one, and whether it reintroduces the bug
   in a new form.
7. Build the assembled book. Check every code fence is closed, then read each changed
   section with its neighbors for flow, section order and the chapter's goals.
8. Check the report's "edits needed elsewhere" and apply the ones you agree with.
