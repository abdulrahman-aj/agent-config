---
name: learning-book
disable-model-invocation: true
description: Write a personal learning book and typeset it as a PDF. Use when someone wants long material they will study and act on, such as a book, a course, or an owner's manual; not for short docs, READMEs or single pages.
---

# Learning book

## 1. Scope it

Load the `grill-me` skill before planning. Find out what the reader already knows,
what they should be able to do afterwards in priority order, and how many pages and
hours they can spend including exercises. Agree which real cases to use, where the
reader runs exercises, and what the exercises must leave untouched. Agree whether the
book is read on screen or printed, which sets margins and chapter starts. Set the
title, subtitle, and goal.

Write the reader, their goals, the scope and any coverage promise (such as "replaces
book X") in a plan file. It is the one source for every brief. When it changes, update
the title page, front matter, exercises and capstone wherever the old promise appears.

By default give each book its own private repository with `book/` for the sources and
`lab/` for runnable exercises. Land changes through PRs. Agree where the PDF goes and
which source material may be included. If the book might be shared, describe who it
is for as a group, such as "developers who maintain a service," from the first draft,
and quote other books only briefly, inside your own explanation.

## 2. Plan and write

List the chapters and what the reader will be able to do after each one. The reader's
background decides the examples and how much each idea needs explaining. It never
decides coverage: a topic inside the agreed scope stays, even if the reader half knows
it, when they need it for the work the book prepares them for. Cut repetition and
padding, not needed topics. Teach prerequisites just before the reader needs them.
Define each term at first use and keep its name consistent. Use the glossary for
terms the reader will look up again.

If the book promises to replace or cover a source, list the source's ideas section by
section and record where the book teaches each one, with its reasoning and limits.
Mark each covered, thin, or out of scope, and repeat the audit after a restructure.

Admit a new tool or topic only when you can name the reader's decision it teaches and
what the existing material cannot show. Check any claim about maturity or adoption.
List useful topics that lose on scope in a "what this book leaves out" page, each
with why it matters and one checked source.

Plan the structure with the chapter list. Decide the parts, the reading paths for
different goals, the lookup pages (a symptom index, a catalogue) with their own
headings and contents entries, and which mechanisms get a diagram. Each one added
later costs a pass over every chapter. Walk each reading path and check that it
supplies the prerequisites it skips. If the book rates or classifies things, write
the rule that decides each verdict before the first entry, then check every entry
against it. Label every navigation element: a table gets a title, and a link's text
names where it goes. An unlabeled link reads as part of whatever sits next to it.

Before drafting in parallel, build one representative chapter end to end: prose, a
runnable exercise with its answer, a fact-check and a rendered PDF. Review it with the
user, fix what the other chapters would inherit, and use it as the writers' model.

Give readers a chance to try the material and recall it. Show what happened in a real
case and ask the reader to judge before giving the verdict. Ask recall questions that
test decisions, not trivia, and put the answers at the chapter end. Explain what you
would choose, which trade-offs you would accept, and when you would choose
differently.

Check flow at two costs. After every batch of changes, read each changed section with
the sections around it. After drafting a part, and before each whole-book blind read,
read the whole book in order. Each chapter picks up what the previous one taught. A
running example keeps its names and schema unless the text announces the change. An
exercise comes after the rules it needs. A case is told in one place. No passage
relies on an idea taught later; a pointer forward is fine when the reader can keep
going without following it. Before a whole-book read, list the key terms with the
section that teaches each, and search earlier pages for uses.

Start each chapter with its material, not an announcement of it, and end without a
recap. Skip definitions of what the reader already knows. Draw a diagram only for a
real mechanism. Run `unslop` over every chapter.

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
6. A model from a different family than the writer fact-checks each chapter before
   you accept it, and each fix round's diff after. A strong reasoning model, within
   the agreed budget, challenges risky designs before they are built and checks the
   guarantees once labs run. Every finding comes with a reproduction or a source.
   Rechecks go to the same reviewer with its earlier findings; an independent read
   gets a fresh one. Stop when no supported blocker or major finding remains in the
   changed scope and every planned range has been covered.
7. Show the real mistakes, with what they cost. When the book covers a system you
   built, its costs and open problems sit next to its wins.

## 4. Labs

- A lab that proves a guarantee (section 3, rule 5) runs the breaking scenario. When it
  claims convergence, that includes concurrent writers. When a review reproduces a
  bug, keep the scenario as a regression test, and consider turning it into an
  exercise.
- Make `make verify` replay the printed commands and compare output and exit status.
  Before a release, run it from a fresh clone with fresh lab state, following the
  book's printed setup through the documented entry point. On a mismatch, save the
  command, exit status and raw output. Labs print one line per outcome so the book can
  quote the output directly.
- Name lab folders by topic (`ch05-lazy-load`, not `ch05`).
- Keep the linters and type checkers that editors run by default at zero findings,
  such as ruff and basedpyright in standard mode for Python. Put their configuration
  at the repository root, where an editor opening the repository finds it. Run them
  and the formatter check in `make verify`, and check that every code block the book
  quotes still matches its lab file.
- Decide the split early. The book gives setup once, then shows the plain command the
  reader runs and the one output that settles each point. The lab carries run modes,
  variants and detail, in docstrings and a `lab/README`. Add a markdown file per lab
  only for depth the book lacks.
- Don't print a short implementation as "the pattern" when it hides failure modes that
  matter in production. Show what the lab demonstrates, list the hard parts as what to
  demand of a library, and point to a maintained one.
- Make concurrency labs deterministic. Wait on observable state, such as a blocked
  backend in `pg_stat_activity`, never on sleeps or thread timing. To force an
  interleaving, drive both sessions step by step from one thread.
- Test the lab's real code and show that the test fails with the mechanism removed.
  Do not assert stdout in tests. Root-cause every flaky result.

## 5. Typeset

Write `book.typ` against this skill's `template.typ`. The template header lists the
interface and `sample/book.typ` shows how to use it. Keep SVG diagrams next to
`book.typ` and quote font names in them, such as `'Source Sans 3'`, `'Source Serif 4'`
or `'JetBrains Mono'`.

Label sections you link to with `== Heading <sec-topic>`. In prose, link with
`#link(<sec-topic>)[Heading]`. In glossary entries, pass `<sec-topic>` as the target.

```bash
python3 <this skill>/build.py path/to/book.typ   # writes path/to/book.pdf
```

The build gets Typst, fonts, and Poppler from nixpkgs and copies the template next to
`book.typ`. It tries to reduce short chapter endings. It checks answer page numbers
and links, section labels, and horizontal text overflow in the body area. Review the
page-fill report and inspect rendered pages for clipping, vertical overflow, and
diagram problems. When you change the template or checker, confirm that a deliberately
broken link, label or pin fails the build.

If others will build the book, copy `build.py`, `check.py`, and `template.typ` into
`tools/typeset/` as a set and record the skill commit. Commit a flake lock with a root
input named `nixpkgs`. For example, with the flake in `lab/`, have `make pdf` run this
from the repository root and test it from a fresh clone.

```bash
nix shell --inputs-from ./lab nixpkgs#python3 -c python3 tools/typeset/build.py --inputs-from ./lab book/book.typ
```

## 6. Look at it

Render every page and inspect it at the size it will be read for clipped diagram
labels, narrow table columns, awkward box splits, stranded headings, blank pages and
loose spacing.

```bash
mkdir -p out
nix shell nixpkgs#poppler-utils -c pdftoppm -r 80 -png book.pdf out/page
```

Freeze the PDF under a name that includes its source commit for a blind read. Give
the reviewer only the PDF, a way to render pages, and the review criteria. Track which
pages they covered and check every proposed fix. Finish when both the fact-check
rounds and the blind read are clean.

Reviews check that the book is right, not that it teaches. To test teaching, give a
reader a new task for the top goal, with a checkable result, such as a codebase with
planted bugs. Record where they succeed and where they get stuck, and revise the
teaching there.

## 7. Brief workers

You own the assembled book. Workers and reviewers propose; you check each result
against the book, choose the fix that is best for the reader, and record the findings
you decline and why. Never choose a fix because it is less work.

Build every brief from the templates in `briefs/`. Each one carries the traps that
workers fell into on an earlier book, so a brief written from scratch repeats them.
Start with `briefs/common.md`, add the role's template, and fill the fields in angle
brackets that apply at this stage. Delete fields and rules that don't apply, and write
"none yet" where an input doesn't exist. Literal code such as `<sec-topic>` is not a
field.

| Role | Template | When |
|---|---|---|
| Research a chapter's sources, cases and lab drafts | `research.md` | Before writing a chapter |
| Write a chapter, section or entry | `writer.md` | Drafting and additions |
| Fact-check claims against sources | `fact-check.md` | Each chapter, then each fix round's diff |
| Check that guarantees hold | `guarantee-review.md` | Before risky designs are built, once labs run, then each round's diff |
| Fix review findings | `fixer.md` | After every review |
| Draw diagrams | `diagram.md` | When a mechanism needs one |
| Read the frozen PDF cold | `blind-read.md` | Each major revision |

Give each worker files no other worker owns. Split a long review into page ranges in
one thread and track coverage until every range has a report; a worker's turn ending
is not the review ending. When a worker reports, go through `briefs/review-worker.md`
before accepting anything, and after parallel workers finish, build the assembled
book and check each changed chapter's flow (section 2).
