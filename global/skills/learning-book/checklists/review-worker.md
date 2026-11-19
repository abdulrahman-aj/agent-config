# Reviewing a worker's result

Workers report success they didn't verify. Check the work, not the report.

1. Read changes to checks, tests, the verifier and build tools first. Reject any that
   make a check pass instead of making the work correct.
2. Rerun every negative control yourself. It must revert only the mechanism under test
   and fail for the reason claimed. One crash test still passed with the kill removed,
   because a client-side close released the lock first.
3. Delete tests that assert printed transcripts; the verifier covers those.
4. Rerun changed demonstrations with the verifier. Root-cause every failure: "flaky
   under load" hid two real bugs in one round.
5. Read new prose line by line. Cheaper writers produced mannered lines, recap
   paragraphs and confident wrong asides; look also for sentences copied from the
   brief, hedges on supportable claims, dropped explanations, and structure filled to
   fit. Then run `unslop` over every new passage, your own included.
6. Ask whether the fix is the simplest correct one and whether it reintroduces the bug
   in a new form. Rerun the original failure and nearby variants.
7. Check every code fence and block is closed, then build once the batch finishes.
8. Apply the "edits needed elsewhere" from the report that you agree with.
