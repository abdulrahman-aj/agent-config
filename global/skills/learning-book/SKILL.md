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
| Planning, before any drafting, and whenever the plan changes | `checklists/plan.md` |
| Before setting up or drafting the first lab, and before accepting a lab change | `checklists/labs.md` |
| After every batch of changes, after drafting a part, and before a whole-book blind read | `checklists/flow.md` |
| Briefing a worker | Section 7's role table and assembly rules |
| Accepting any worker's result | `checklists/review-worker.md` |
| Before sending the user a checkpoint PDF, and before a release | `checklists/release.md` |

## 1. Scope it

Load the `grill-me` skill before planning. Find out what the reader already knows,
what they should be able to do afterwards in priority order, and how many pages and
hours they can spend including exercises. Agree which real cases to use, where the
reader runs exercises, and what the exercises must leave untouched. Agree whether the
book is read on screen or printed. Set the title, subtitle, and goal.

Write the reader, their goals, the scope and any coverage promise (such as "replaces
book X") in a plan file. It is the one source for every brief.

By default give each book its own private repository with `book/` for the sources and
`lab/` for runnable exercises. Land changes through PRs. Agree where the PDF goes and
which source material may be included. If the book might be shared, describe who it
is for as a group, such as "developers who maintain a service," from the first draft,
and quote other books only briefly, inside your own explanation.

## 2. Plan and write

List the chapters and what the reader will be able to do after each one. Then work
through `checklists/plan.md`, which ends with an outline review and one sample chapter
built end to end. Draft the rest only after the user has reviewed that sample.

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
6. Review in three ways, each with its brief from section 7:
   - a model from a different family than the writer fact-checks each chapter before
     you accept it, and each fix round's diff after;
   - a strong reasoning model, within the agreed budget, challenges risky designs
     before they are built and checks the guarantees once labs run;
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

You own the assembled book. Workers and reviewers propose; you check each result
against the book, choose the fix that is best for the reader, and record the findings
you decline and why. Never choose a fix because it is less work for you; between
equally good fixes, take the simpler. Raise real budget or scope changes with the user.

Build every brief from the templates in `briefs/`. Each one carries the traps that
workers fell into on an earlier book, so a brief written from scratch repeats them.
Start with `briefs/common.md` and add the role's brief. The blind read is the
exception: it uses `blind-read.md` alone. Fill the fields in angle brackets that apply
at this stage, delete fields and rules that don't apply, and write "none yet" where an
input doesn't exist. Literal code such as `<sec-topic>` is not a field.

| Role | Brief | When |
|---|---|---|
| Research a chapter's sources, cases and lab drafts | `research.md` | Before writing a chapter |
| Write a chapter, section or entry | `writer.md` | Drafting and additions |
| Fact-check claims against sources | `fact-check.md` | Each chapter, then each fix round's diff |
| Check that guarantees hold | `guarantee-review.md` | Before risky designs are built, once labs run, then each round's diff |
| Fix review findings | `fixer.md` | After a review, for the findings you accept |
| Draw diagrams | `diagram.md` | When a mechanism needs one |
| Read the frozen PDF cold | `blind-read.md` | Each major revision |

Give each worker files no other worker owns. Split a long review into page ranges, pin
the revision, and track coverage until every range has a report; a worker's turn
ending is not the review ending.
