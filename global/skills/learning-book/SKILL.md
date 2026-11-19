---
name: learning-book
disable-model-invocation: true
description: Write a personal learning book and typeset it as a PDF. Use when someone wants long material they will study and act on, such as a book, a course, or an owner's manual; not for short docs, READMEs or single pages.
---

# Learning book

This file is the process. The files it names hold the detail. Open each one at its
trigger below and follow the steps for that trigger.

| Stage | Open |
|---|---|
| Before setting up or drafting the first lab, and before accepting a lab change | `checklists/labs.md` |
| After every batch of changes, after drafting a part, and before a whole-book blind read | `checklists/flow.md` |
| Briefing a worker | Section 7, then that role's part of `traps.md` |
| Accepting any worker's result | `checklists/review-worker.md` |
| Before sending the user a checkpoint PDF, and before a release | `checklists/release.md` |

## 1. Scope it

Load the `grill-me` skill before planning. Find out what the reader already knows,
what they should be able to do afterwards in priority order, and how many pages and
hours they can spend including exercises. Agree which real cases to use, where the
reader runs exercises, and what the exercises must leave untouched. Agree whether the
book is read on screen or printed. Ask which models you may use, for which roles, and
the budget. Set the title, subtitle, and goal.

The reader often doesn't know what the field holds, so don't ask them to design the
book. After the first round, survey the territory yourself: the canonical sources, what
changed recently, what practitioners struggle with. Then show the reader a map of it
with a proposed chapter-level table of contents: each chapter's title, its takeaway,
why it's in, its page budget, and what you would leave out and why. The grill ends when
the reader has approved that table of contents. Sections come later, after research.

Write the reader, their goals, the scope, any coverage promise (such as "replaces
book X"), and the allowed models and budget in a plan file. It is the one source for
every brief.

By default give each book its own private repository with `book/` for the sources and
`lab/` for runnable exercises. Land changes through PRs. Agree where the PDF goes and
which source material may be included. If the book might be shared, describe who it
is for as a group, such as "developers who maintain a service," from the first draft,
and quote other books only briefly, inside your own explanation.

## 2. Plan and write

Start from the table of contents the grill ended on, and settle the following before
any drafting; each item added later costs a pass over every chapter.

**Coverage.** The page budget is a ceiling. Never add a section to reach a page count
or to move a block onto another page; fix pagination in the layout.

- The reader's background decides the examples and how much each idea needs
  explaining, never coverage. A topic inside the agreed scope stays when the reader
  needs it for the work the book prepares them for, even if they half know it. Cut
  repetition and padding, not needed topics.
- Name what this book teaches that existing material doesn't, and check that each
  chapter delivers part of it. An outline that would fit an older book on the topic
  has missed the point.
- If the book promises to replace or cover a source, list the source's ideas section
  by section with where the book teaches each, its reasoning and limits, marked
  covered, thin or out of scope. Repeat the audit after a restructure.
- If the lessons should transfer across stacks, state each principle before its lab,
  and show a second stack where it behaves differently.
- Admit a new tool or topic only when you can name the reader's decision it teaches
  and what the existing material can't show. Check claims about maturity or adoption.
- List useful topics that lose on scope on a "what this book leaves out" page, each
  with why it matters and one checked source.

**Structure.** Scale it to the book: a short book read straight through needs no parts,
reading paths or lookup pages.

- Decide the parts, the reading paths for different goals, and the lookup pages (a
  symptom index, a catalogue), each with its own heading and contents entry. Walk each
  path and check it supplies the prerequisites it skips.
- Decide which mechanisms get a diagram. Only real mechanisms do.
- If the book rates or classifies things, write the rule for each verdict before the
  first entry, and check every entry against it.
- Give every table a title, every link text that names where it goes (an unlabeled link reads as part
of whatever sits next to it), and every heading
  you will link to a label from the start.

**Lab and book.** The book gives setup once, then the plain command the reader runs
and the output that settles each point. The lab carries run modes, variants and
detail: each lab's docstring gives its command, variants and book section, `lab/README` holds shared setup, and folders are named by topic (`ch05-lazy-load`, not
`ch05`). Add a markdown file per lab only for depth the book lacks.

**When the plan changes**, update the plan file first, then the title page, front
matter, exercises and capstone wherever the old promise appears. Keep one scope
statement in the plan and say the same in the front matter, which describes the book as
it is and never promises chapters that aren't written.

**Sample chapter.** Build one representative chapter end to end: prose, a runnable
exercise with its answer, a fact-check and a rendered PDF. Review it with the user, fix
what the other chapters would inherit, and make it the writers' model. Draft the rest
only after that.

Teach prerequisites just before the reader needs them. Define each term at first use
and keep its name consistent. Use the glossary for terms the reader will look up again.

Give readers a chance to try the material and recall it. Show what happened in a real
case and ask the reader to judge before giving the verdict. Ask recall questions that
test decisions, not trivia, and put the answers at the chapter end. Explain what you
would choose, which trade-offs you would accept, and when you would choose
differently.

Start each chapter with its material, not an announcement of it, and end without a
recap. Skip definitions of what the reader already knows. Run `unslop` over every
chapter. Check flow with `checklists/flow.md`.

## 3. Trust

One wrong fact makes the reader doubt every other page, so every claim gets checked.

1. Run every command the book prints and quote its real output. Trim long output, but
   never edit a line you keep. If you haven't run it, describe it without quoting it.
   This includes output fragments quoted inside sentences.
2. Check every claim against a primary source: the specification, the official
   documentation at the version the book names, the original paper or book. A blog
   post or a model's memory is a lead, not a source.
3. Check definitions against the original author, and the tools you map them to
   against their current documentation. A definition that bakes in one
   implementation, such as who commits or which library, is wrong for the next
   reader. An example must have the defining property of what it illustrates. State
   the book's own choices as choices.
4. Distrust "all", "every", "never" and "only". Look for the counterexample.
5. A guarantee (a lock holds, a retry is safe, a cache stays fresh) needs a
   reproduction that would fail without the mechanism, not an argument. This includes
   the guarantees in a worked design or a sample page, not only in the labs.
6. Review in three ways, each briefed as section 7 describes:
   - a model from a different family than the writer fact-checks each chapter before
     you accept it, and each fix round's diff after;
   - a strong reasoning model, within the agreed budget, challenges risky designs
     before they are built, checks the guarantees once labs run, and fact-checks each
     new section before merge. On one book, cheaper fact-checkers passed sections in
     which the strong model then found must-fix errors every round;
   - a blind reader from a different family reads the frozen PDF after each major
     revision.

   Every correctness finding comes with a reproduction or a source. Rechecks go to the
   same reviewer with its earlier findings and the changed scope; an independent read
   gets a fresh one. The book is done when every planned range has been covered, no
   supported blocker or major finding remains, and the blind read has no "must fix"
   left.
7. Show the real mistakes, with what they cost. When the book covers a system you
   built, its costs and open problems sit next to its wins.

## 4. Labs

Labs prove guarantees by running the scenario that breaks them, and the book's printed
commands are replayed against them. Everything else is in `checklists/labs.md`.

## 5. Typeset

Write `book.typ` against this skill's `template.typ`. The template header lists the
interface and `sample/book.typ` shows how to use it. Keep SVG diagrams next to
`book.typ` and quote font names in them, such as `'Source Sans 3'`, `'Source Serif 4'`
or `'JetBrains Mono'`.

The template is screen-first. For a printed edition, change the copy beside `build.py`
(the build overwrites the one next to `book.typ`) and check binding margins and chapter
starts in the sample.

In tables, use `auto` only for columns of short labels and give text columns `fr`
weights: an `auto` column sizes to its longest cell and squeezes the others into
one-word lines.

Label sections you link to with `== Heading <sec-topic>`. In prose, link with
`#link(<sec-topic>)[Heading]`. In glossary entries, pass `<sec-topic>` as the target.

```bash
python3 <this skill>/build.py path/to/book.typ   # writes path/to/book.pdf
```

The build gets Typst, fonts, and Poppler from nixpkgs and copies the template next to
`book.typ`. It tries to reduce short chapter endings. It checks answer page numbers
and links, section labels, and horizontal text overflow in the body area. It cannot see
vertical overflow or problems inside diagrams; section 6 covers those. When you change
the template or checker, confirm that a deliberately broken link, label or pin fails
the build.

## 6. Look at it

Render every page and inspect it at the size it will be read for clipped diagram
labels, vertical overflow, narrow table columns, awkward box splits, stranded
headings, blank pages and loose spacing. Review the build's page-fill report.

```bash
mkdir -p out
nix shell nixpkgs#poppler-utils -c pdftoppm -r 80 -png book.pdf out/page
```

Reviews check that the book is right, not that it teaches. To test teaching, give a
reader a new task for the top goal, with a checkable result, such as a codebase with
planted bugs. Record where they succeed and where they get stuck, and revise the
teaching there.

## 7. Brief workers

Run the book with the strongest model the user allows, such as Opus or Sol. A pilot
with a cheaper orchestrator followed every rule and still missed the editorial calls:
a generic outline, structure out of proportion to the book, a sample chapter that
didn't deliver its own takeaway. Cheaper models do well as workers under review.

You own the assembled book. Workers and reviewers propose; you check each result
against the book, choose the fix that is best for the reader, and record the findings
you decline and why. Never choose a fix because it is less work for you; between
equally good fixes, take the simpler. Raise real budget or scope changes with the user.

Write each brief yourself: the task, the files the worker owns, its inputs (plan
file, PDF, sources, the command that replays its chapter), how to wait on long jobs,
and the report you want. Then add the traps for its role from `traps.md`.

| Role | When |
|---|---|
| Research a chapter's sources, cases and lab drafts | Before writing a chapter |
| Write a chapter, section or entry | Drafting and additions |
| Fact-check claims against sources | Each chapter, then each fix round's diff |
| Check that guarantees hold | Before risky designs are built, once labs run, then each round's diff |
| Fix review findings | After a review, for the findings you accept |
| Draw diagrams | When a mechanism needs one |
| Read the frozen PDF cold | Each major revision |

Some providers' safety filters block security teaching, such as a lab that shows a
privilege escalation. A worker may also quietly drop such a demonstration. Name those
labs and their files neutrally, describe the technique in the brief without trigger
words, and give that work to a model that accepts it.

Give each worker files no other worker owns, and give each worker that runs a lab its
own git worktree under a short path, such as `~/Work/<repo>-wt12`: a PostgreSQL socket
path longer than 107 bytes fails, and deep scratch directories exceed it. Stop a
worker's processes by PID, never with `pkill -f <worktree path>`, which also matches
that worktree's database server. Split a long review into page ranges, pin
the revision, and track coverage until every range has a report; a worker's turn
ending is not the review ending.

Waiting is a tree: you wait on your workers, and whoever started you waits on you.
If you were started by another agent, every turn you end wakes it, so end a turn only
for a real question (scope, behavior, cost, reversibility) or a stage ready for
review. While workers run, block on them with your harness's wait (in T3,
`t3_thread_wait` with `untilDelegatedWorkSettled`, repeated on timeout), even when a
tool suggests ending your turn. With parallel workers, wait on each in turn; one that
already finished returns at once. To act on early finishers, cycle through them with a short wait timeout. Decide everything else yourself.
