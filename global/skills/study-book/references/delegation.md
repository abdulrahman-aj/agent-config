# Delegation, parallel batches and sweeps

Load this reference when briefing workers, running parallel batches, or running
book-wide sweeps and blind comparisons.

## Briefs

- Give each worker clear file ownership so parallel edits never collide.
- Write specs as content, never as edit notes such as "replace X with three sharper
  questions", because edit notes end up in the prose. Search new prose for sentences
  copied from the brief.
- Give criteria only in ranking or selection briefs; a candidate named even as an
  example wins.
- Name each section's neighbors when parallel workers draft or edit sections, or workers
  place sections where their brief suits.
- Tell prose workers to follow the plan's style rules, load `unslop` and write no
  recaps, because they skip style rules otherwise.
- Forbid workers from editing checks or tests to pass and from deleting a failure
  demonstration they couldn't replay. Require a hard demonstration to replay or be
  reported, and ask for the smallest correct fix, checked for the same bug in a new
  form; workers otherwise fix heavily, such as adding a retry loop where one atomic
  statement did.
- Require workers who narrow a claim to reread the paragraph and its neighbors, because
  narrowed claims get spliced in without checking surrounding sentences.
- Split a whole-book review into page ranges at a pinned revision, because it doesn't
  fit one turn, and ask for the ranges not covered.
- Ask cheap goal readers to search the book and quote the passage that should have
  taught what they call missing; three in four such claims were answered a page earlier.

## Exhaustive sweeps and blind comparisons

- For sweeps that must catch every instance, such as stale cross-references,
  cross-chapter contradictions or claims that hold on one engine only, use cheap readers
  only to propose candidates.
- Require each candidate to cite file and line with a quote that a script checks, and
  forbid parallel workers from reading sibling findings files, because one worker copied
  another's findings when both wrote to the same directory.
- Measure recall on known hits hidden from the sweepers, and have a strong model verify
  what survives. Below full recall, change the sweep, using smaller windows or a second
  starting point such as the tool's own list of known pitfalls, and rerun; one sweep
  found two of six known hits. Even full recall yields leads, not proof that nothing is
  left.
- Compare two versions blind using random labels, no description of the change,
  randomized order and ties allowed. A primed comparison once returned a unanimous
  verdict that proved nothing.
