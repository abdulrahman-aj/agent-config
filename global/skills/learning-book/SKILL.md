---
name: learning-book
disable-model-invocation: true
description: Write a personal learning book and typeset it as a PDF. Use when someone wants long material they will study and act on, such as a book, a course, or an owner's manual; not for short docs, READMEs or single pages.
---

# Learning book

## 1. Scope it

Load the `grill-me` skill before planning. Find out what the reader already knows,
what they should be able to do afterwards, and how many pages and hours they can spend
including exercises. Agree which real cases to use, where the reader runs exercises,
and what the exercises must leave untouched. Set the title, subtitle, and goal.

By default give each book its own private repository with `book/` for the sources and
`lab/` for runnable exercises. Land changes through PRs. Agree where the PDF goes and
which source material may be included. If the book might be shared, describe who it
is for as a group, such as "developers who maintain a service," from the first draft,
and quote other books only briefly, inside your own explanation.

## 2. Plan and write

List the chapters and what the reader will be able to do after each one. Cut material
that serves none of those goals. Teach prerequisites just before the reader needs
them. Define each term at first use and keep its name consistent. Use the glossary for
terms the reader will look up again.

Plan the structure with the chapter list. Decide the parts, the reading paths for
different goals, the lookup pages (a symptom index, a catalogue) with their own
headings and contents entries, and which mechanisms get a diagram. Each one added
later costs a pass over every chapter. If the book rates or classifies things, write
the rule that decides each verdict before the first entry, then check every entry
against it. Label every navigation element: a table gets a title, and a link's text
names where it goes. An unlabeled link reads as part of whatever sits next to it.

Give readers a chance to try the material and recall it. Show what happened in a real
case and ask the reader to judge before giving the verdict. Ask recall questions that
test decisions, not trivia, and put the answers at the chapter end. Explain what you
would choose and which trade-offs you would accept.

Check flow at two costs. After every batch of changes, read each changed section with
the sections around it. After drafting a part, and before each blind read, read the
whole book in order. Each chapter picks up what the previous one taught. A running
example keeps its names and schema unless the text announces the change. An exercise
comes after the rules it needs. A case is told in one place. No passage relies on an
idea taught later.

Start each chapter with its material, not an announcement of it, and end without a
recap. Skip definitions of what the reader already knows. Draw a diagram only for a
real mechanism. Run `unslop` over every chapter.

## 3. Trust

One wrong fact makes the reader doubt every other page, so every claim gets checked.

1. Run every command the book prints and quote its real output. Trim long output, but
   never edit a line you keep. If you haven't run it, describe it without quoting it.
2. Check every claim against a primary source: the specification, the official
   documentation at the version the book names, the original paper or book. A blog
   post or a model's memory is a lead, not a source.
3. Check definitions against the original author, and the tools you map them to
   against their current documentation. A definition that bakes in one
   implementation, such as who commits or which library, is wrong for the next
   reader. State the book's own choices as choices.
4. Distrust "all", "every", "never" and "only". Look for the counterexample.
5. A guarantee (a lock holds, a retry is safe, a cache stays fresh) needs a
   reproduction that would fail without the mechanism, not an argument. This includes
   the guarantees in a worked design or a sample page, not only in the labs.
6. A model from a different family than the writer fact-checks the whole book
   before typesetting. A strong reasoning model checks the guarantees early. Every
   finding comes with a reproduction or a source, and fixes go back to the same
   reviewer until a round comes back clean.
7. Show the real mistakes, with what they cost. When the book covers a system you
   built, its costs and open problems sit next to its wins.

## 4. Labs

- A lab that proves a guarantee (section 3, rule 5) runs the breaking scenario. When it
  claims convergence, that includes concurrent writers.
- Make `make verify` replay the printed commands and compare output and exit status.
  Run it from a fresh clone using the book's printed setup. Labs print one line per
  outcome so the book can quote the output directly.
- Name lab folders by topic (`ch05-lazy-load`, not `ch05`).
- Keep the linters and type checkers that editors run by default at zero findings,
  such as ruff and basedpyright in standard mode for Python. Put their configuration
  at the repository root, where an editor opening the repository finds it. Run them
  and the formatter check in `make verify`, and check that every code block the book
  quotes still matches its lab file.
- Decide the split early. The book carries the argument and the one output that
  settles each point. The lab carries run modes, variants and detail, in docstrings
  and a `lab/README`. Add a markdown file per lab only for depth the book lacks.
- Make concurrency labs deterministic. Wait on observable state, such as a blocked
  backend in `pg_stat_activity`, never on sleeps or thread timing. To force an
  interleaving, drive both sessions step by step from one thread.
- Test the lab's real code and show that the test fails with the mechanism removed.
  Do not assert stdout in tests. Investigate flaky results.

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
diagram problems.

If others will build the book, copy `build.py`, `check.py`, and `template.typ` into
`tools/typeset/` and record the skill commit. Commit a flake lock with a root input
named `nixpkgs`. For example, with the flake in `lab/`, have `make pdf` run this from
the repository root and test it from a fresh clone.

```bash
nix shell --inputs-from ./lab nixpkgs#python3 -c python3 tools/typeset/build.py --inputs-from ./lab book/book.typ
```

## 6. Look at it

Render every page and inspect it for clipped diagram labels, narrow table columns,
awkward box splits, and stranded headings.

```bash
mkdir -p out
nix shell nixpkgs#poppler-utils -c pdftoppm -r 80 -png book.pdf out/page
```

Freeze the PDF for a blind read. Give the reviewer the PDF, page images, and the
review criteria. Track which pages they covered and check every proposed fix. Finish
when both the fact-check rounds and the blind read are clean.

Reviews check that the book is right, not that it teaches. To test teaching, give a
reader a task the book should prepare them for, such as a codebase with planted bugs,
and see what they find.

## 7. Brief workers

Specify the content the reader should see rather than giving edit notes they might
copy into the prose. Draw diagrams from real lab output and check each rendering
against it. After parallel workers finish, build the assembled book and check each
changed chapter's flow (section 2), section order and goals.

Tell workers in the brief never to edit checks, tests or tools to make their output
pass, and review diffs to those files before the prose. After every fix round, read
the prose diff for new hedges ("may", "in some cases") that weaken a claim the book
can support, and restore explanations that were cut to satisfy a finding.
