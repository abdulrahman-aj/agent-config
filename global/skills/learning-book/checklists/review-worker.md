# Reviewing a worker's result

A checklist for whoever briefed the worker. Workers report success they didn't verify,
so check the work, not the report. Skip the steps that don't apply to what changed.

1. Read changes to checks, tests, the verifier and build tools first. Reject any that
   make a check pass instead of making the work correct. In a shared checkout, undo
   only that worker's change.
2. Rerun every negative control yourself. It must revert only the mechanism under test
   and fail for the reason the test claims.
3. Remove tests that duplicate the verifier by asserting printed transcripts. Keep
   tests of behavior.
4. When labs changed, rerun the changed demonstrations with the verifier, then the
   whole test suite from fresh state once per batch. Root-cause every failure; "flaky
   under load" is not a cause.
5. Read the prose diff line by line, not as a skim:
   - sentences copied from the brief or spec;
   - hedges that weaken a claim the book can support;
   - explanations that were cut, and positions that were dropped;
   - mannered lines, recaps, and new terms for existing concepts;
   - paragraphs that open the same way, and sections with the same shape;
   - new technical claims without a source or run, which cluster in new text.
6. Ask whether the fix is the simplest correct one, and whether it reintroduces the bug
   in a new form. Rerun the original failure and nearby variants.
7. When prose or figures changed, check every code fence and block is closed. Once the
   whole batch has finished, build and read it with `flow.md`.
8. Check the report's "edits needed elsewhere" and apply the ones you agree with.
