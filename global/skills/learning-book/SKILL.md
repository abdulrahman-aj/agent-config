---
name: learning-book
disable-model-invocation: true
description: Write a personal learning book and typeset it as a PDF. Use when someone wants long material they will study and act on, such as a book, a course, or an owner's manual; not for short docs, READMEs or single pages.
---

# Learning book

You know how to write, teach and review. Earlier books still went wrong in the ways
below, each an instance of one of these principles.

## Principles

1. **You own the book.** Workers and reviewers propose; nothing counts until you have
   checked it. Workers report success they didn't verify, so check the work, not the
   report: read their changes to checks and tests first, and their prose line by line;
   cheaper writers leave mannered lines, recaps, hedged claims, dropped explanations and
   confident wrong asides. Choose each fix on what is best for the reader, never on what
   is less work, and record the findings you decline.
2. **Nothing is true until it ran.** Print only output from a real run, trimmed but
   never edited, including fragments in sentences and illustrative lines such as a
   plan's `Filter:`; labs print one line per outcome so nothing needs editing. Check
   claims against primary sources at the version the book names, and definitions against
   the original author. A guarantee needs a reproduction that fails without the
   mechanism, in worked designs as well as labs; a convergence claim also runs
   concurrent writers on the source side. A finding needs a reproduction or a source.
3. **Strong models gate, cheaper ones filter.** Orchestrate with the strongest model the
   user allows (Opus or Sol). A cheaper orchestrator followed every rule and still
   produced a generic outline and a sample chapter that missed its takeaway. Cheaper
   fact-checkers passed sections in which Sol then found must-fix errors, every round,
   clustered in the newest prose; so the strong model checks each risky design before it
   is built, gates every new section and guarantee, and rechecks each fix round with its
   own earlier findings, because fixes break things nearby. For judgment work (which
   ideas recur, what to name them) run a strong pass beside the cheap one, not after it:
   a cheap sweep anchors the answer.
4. **Fix the class, not the instance.** When a review finds a problem, name its class,
   search the book for siblings, and change the process that let it in.
5. **The scope decides coverage.** One scope statement lives in the plan and the front
   matter, which describes the book as it is and never promises unwritten chapters. The
   reader's background sets examples and depth, never which needed topics stay; the page
   budget is a ceiling, and pagination is fixed in the layout, never with content;
   framing that drifts narrower ("the service" in a book about a whole app) is a scope
   bug.
6. **Content before form.** A table, parallel list or heading chosen because it looks
   rigorous gets filled to fit. Keep a column or item only if deleting it loses an
   answer to a reader's question.
7. **A worker repeats whatever its brief allows.** Briefs carry the traps below.
8. **Isolate workers and verify the way the reader will.**

## Scope and plan

Load `grill-me`. Settle the reader's knowledge, goals in order, page and hour budget,
real cases, where exercises run and what they must not touch, screen or print, and the
models allowed per role. The reader usually doesn't know the field, so survey it
yourself and propose a chapter-level table of contents with each chapter's takeaway,
budget and what you leave out; the grill ends when they approve it. Record it all in a
plan file that every brief points at.

Give each book a private repository with `book/` and `lab/`, landing changes through
PRs; the PDF ships as a release asset, and source material never enters the repository.
If the book might be shared, describe the reader as a group and quote other books only
briefly, inside your own explanation.

Before drafting, since anything added later costs a pass over every chapter:

- Name what this book teaches that existing material doesn't; an outline that fits an
  older book has missed the point. A book that replaces a source audits the source's
  ideas section by section (covered, thin, out of scope), again after a restructure.
- Transferable lessons state the principle before the lab and show a second stack where
  it behaves differently. Admit a tool only for a decision existing material can't show;
  losers go on a "what this book leaves out" page with a checked source.
- Label every heading you will link to from the start (retrofitting 34 cost a pass), and
  point glossary and catalogue entries at sections. Name verdict labels after their test
  (Apply, Obsolete), and write each verdict's rule before the first entry. Each entry
  says when the verdict holds and what evidence would flip it; a column of bare "Apply"
  reads as a prescription.
- Decide the teaching devices book-wide before drafting; per-chapter choices drift.
  A prediction prompt that worked lets the output follow it directly, with nothing
  above the output hinting at the answer, including a comment in the snippet; blind
  readers flagged every prompt whose answer was already stated above it. A section's rule is its plain first sentence, never a labelled opener
  repeated in every section.
- Recurring ideas get a map that a script checks: each is first met without a name,
  then named, then called back, in that chapter order. Each callback gives a reason;
  more than about four callbacks in one chapter, across all ideas, read as slogans.
- The book gives setup once, then the command and the output that settles each point;
  the lab holds modes and detail. Each lab's docstring gives its command and book
  section, `lab/README` holds shared setup, folders are named by topic. Add a markdown
  file per lab only for depth the book lacks. Before moving a case to the lab, ask
  whether a chapter goal needs it; after moving it, diff the guards left in the book
  against the original (a trim once dropped two) and reread every later sentence that
  relied on it.
- Build one sample chapter end to end and review it with the user before the rest.

Run `unslop` over every new passage before committing it.

## Briefs

Write each brief yourself. These went wrong when a brief didn't say otherwise:

- Edit notes in a spec ("replace X with three sharper questions") end up in the prose.
  Write the spec as content, and search new prose for sentences from the brief.
- A candidate named in a ranking brief, even as an example, wins. Give criteria only.
- Parallel workers place sections where their brief suits. Name each section's
  neighbors.
- Workers don't know the user's style rules: no em dashes, no other languages embedded
  in shell scripts, they/them, no filler or recaps. List them in every brief.
- Workers edit checks or tests to pass, add tests that assert printed transcripts,
  delete a failure demonstration they couldn't replay, and fix heavily (a
  savepoint-and-retry loop where one `INSERT ... ON CONFLICT` did). Forbid the first
  three, have a hard demonstration replay or be reported, and ask for the smallest
  correct fix, checked for the same bug in a new form.
- Narrowed claims get spliced in without rereading. Require a reread of the paragraph
  and its neighbors.
- A provider's safety filter blocks security labs, and workers quietly drop them first.
  Name them neutrally, avoid trigger words, and route them to a model that accepts them,
  in a fresh context.
- Cheaper workers end their turn while builds run. Tell them to wait; verify anyway.
- A whole-book review doesn't fit one turn: split it into page ranges at a pinned
  revision, ask for ranges not covered, and continue in one thread until all are done.


## Isolation and verification

- Each worker owns its files. Each lab worker gets a git worktree under a short path
  (`~/Work/<repo>-wt12`; PostgreSQL sockets fail past 107 bytes), its own database, and
  its own server when it reads server-wide state. Concurrent edits in one checkout broke
  the build mid-edit; other workers' open transactions stalled a snapshot horizon.
- Stop processes by PID: `pkill -f <worktree>` also kills its PostgreSQL. Scratch copies
  for negative controls filled `/tmp`; leave out `.venv`, database and companion
  directories, and delete the copy afterwards.
- No module-level environment changes in tests: one redirected every later test's
  subprocesses. Run the whole suite from a fresh database after each batch.
- `make verify` replays every printed command, compares output and exit status, and
  saves the raw output of each mismatch. Replay through `make` with `MAKELEVEL` and
  `MAKEFLAGS` stripped, or nested make output looks like a flake. Root-cause every
  flake.
- Concurrency labs wait on observable state (`pg_stat_activity`), never sleeps or thread
  liveness; drive both sessions from one thread to force an interleaving. Tests call the
  lab's real function, and a negative control reverts only the mechanism and fails for
  the claimed reason, observed before teardown or retries could produce the outcome.
  Rerun every control yourself: one passed with the kill removed because a client close
  freed the lock. Set up the case only the claimed mechanism stops: a "one live ticket"
  test that a per-order index would also pass proves nothing.
- Each listing contains the case its section is about (a retry loop was once printed
  without its `40001` arm). Never split one function across snippet regions: the second
  half loses its indentation. Rebuild the PDF after any change to region code, since a rename
  can push a line past the margin.
- Editor-default linters (ruff, basedpyright standard) stay at zero from the repository
  root, and `make verify` checks that quoted code matches its lab file. After merging
  one lab PR, rebase the others and rerun: shared Makefile targets and schemas break.
- Before a release, verify from a fresh clone and database cluster through the book's
  printed setup, companion labs included; leftover state hid a broken step.
- Don't print a short implementation as "the pattern" when real ones are large and
  subtle; print the idea, not the plumbing, list what to demand of a library, and point
  to a maintained one.

## Review and flow

Review three ways: a different family fact-checks each chapter and fix diff; the strong
model gates as in principle 3; a blind reader from another family reads the frozen PDF
after each major revision, and finds what informed readers miss (an unannounced schema
switch, an exercise before its rules). The book is done when every range is reviewed, no
supported blocker or major finding remains, and the blind read has no "must fix".

Reviewers optimize what they are asked to check, so correctness rounds pull a book
toward a spec. When a reviewer finds a gap in a worked example, narrow the claim before
extending the example. When each round's findings land in the previous round's
additions, re-cut the scope instead of fixing again.

Compare two versions blind: random labels, no description of the change, randomized
order, ties allowed. A primed comparison once returned a unanimous verdict that proved
nothing. For book-wide defects, add one fresh-context Opus reader: it caught two that twelve
cheap readers missed. Opus subagents can't write files, so ask for the report in the
reply. Ask cheap goal readers to quote the passage that should have taught what they
call missing, after searching the book for it: three in four such claims were answered a
page earlier.

After every batch, check every code fence is closed, build, and read each changed
section with its neighbors; before each blind read, read the whole book. Check that the
running example keeps its names, each case is told once and each idea explained once
under one name, framings match the plan's scope, exercises follow their rules, and the
reader can do each chapter goal from the text.

Commit before starting a reviewer, since a reviewer reading a live branch sees
half-applied fixes. Keep each worker's full task ID in `book/out/reviews/task-ids.md`: truncated IDs left
two finished reviews unread for hours.

If another agent started you, every turn you end wakes it: end one only for a real
question or a finished stage, and block on your workers with the harness's wait.

## Typeset

Write `book.typ` against this skill's `template.typ`; its header lists the interface and
`sample/book.typ` uses all of it. Keep SVG diagrams next to `book.typ` with quoted font
names (`'Source Sans 3'`, `'Source Serif 4'`, `'JetBrains Mono'`). The template is
screen-first; for print, change the copy beside `build.py` (the build overwrites the one
next to `book.typ`) and check binding margins. Label sections `== Heading <sec-topic>`
and link with `#link(<sec-topic>)[Heading]`. In tables, `auto` only for short-label
columns and `fr` for text: an `auto` column sizes to its longest cell and squeezes the
rest. Keep long inline code out of `#question` prompts: the stretched line pushes the
answer link onto a line of its own, where the check can't match it.

```bash
python3 <this skill>/build.py path/to/book.typ   # writes path/to/book.pdf
```

The build fetches Typst, fonts and Poppler from nixpkgs, reduces short chapter endings,
and fails on broken answer pages, links, labels, horizontal overflow, primes printed
for apostrophes after digits, and a stray `.:` left by a cut sentence; it can't see
vertical overflow or inside diagrams. After changing the template or checker, confirm a
deliberately broken link still fails. Render every page and look at reading size (a
squeezed table passed a 50 dpi contact sheet):

```bash
nix shell nixpkgs#poppler-utils -c pdftoppm -r 80 -png book.pdf out/page
```

Reviews check that the book is right, not that it teaches; to test teaching, give a
reader a checkable task for the top goal and revise where they get stuck.

Freeze each checkpoint PDF as `book/out/reviews/review-<commit>.pdf` (gitignored) and
give the user a link. If others will build the book, copy `build.py`, `check.py` and
`template.typ` into `tools/typeset/`, record the skill commit, commit a flake lock with
root input `nixpkgs`, and test from a fresh clone:

```bash
nix shell --inputs-from ./lab nixpkgs#python3 -c python3 tools/typeset/build.py --inputs-from ./lab book/book.typ
```
