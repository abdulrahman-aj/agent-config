---
name: learning-book
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
is for as a group, such as "developers who maintain a service," from the first draft.

## 2. Plan and write

List the chapters and what the reader will be able to do after each one. Cut material
that serves none of those goals. Teach prerequisites just before the reader needs
them. Define each term at first use and keep its name consistent. Use the glossary for
terms the reader will look up again.

Give readers a chance to try the material and recall it. Show what happened in a real
case and ask the reader to judge before giving the verdict. Ask recall questions that
test decisions and put the answers at the chapter end. Explain what you would choose
and which trade-offs you would accept. When covering a system you built, include the
mistakes, costs, and open problems.

Run every command and verify claims against sources. Quote real output. Trim it when
needed and preserve the text of the lines you quote. Describe unverified output
without quoting it. Use primary sources for definitions and state the book's own
implementation choices as choices. Run `unslop` over every chapter. Draw a diagram
only for a real mechanism, never as decoration.

Readers stop trusting a book that defines what they already know, opens chapters by
announcing them, closes them with recaps, or asks recall questions that test trivia.

## 3. Labs

- For each guarantee, run the scenario that would break it without the mechanism.
  Include concurrent writers when claiming convergence.
- Make `make verify` replay the printed commands and compare output and exit status.
  Run it from a fresh clone using the book's printed setup. Labs print one line per
  outcome so the book can quote the output directly.
- Check quoted code blocks against the lab files. Include linter and type checker
  configuration the reader's editor can use, and fix their findings.
- Test the lab's real code and show that the test fails with the mechanism removed.
  Do not assert stdout in tests. Investigate flaky results.

## 4. Typeset

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

## 5. Review

Start correctness review early. Check claims, definitions, and tool mappings against
primary sources. Reproduce commands and test whether the guarantees hold. Give each
finding a reproduction or source. After fixes, send the reviewer the findings and the
fix diff, and repeat until clean.

Render every page and inspect it for clipped diagram labels, narrow table columns,
awkward box splits, and stranded headings.

```bash
mkdir -p out
nix shell nixpkgs#poppler-utils -c pdftoppm -r 80 -png book.pdf out/page
```

Freeze the PDF for a blind read. Give the reviewer the PDF, page images, and the
review criteria. Track which pages they covered and check every proposed fix. Finish
when both the correctness review and the blind read are clean.

## 6. Brief workers

Specify the content the reader should see rather than giving edit notes they might
copy into the prose. Draw diagrams from real lab output and check each rendering
against it. After parallel workers finish, build the assembled book and verify the
section order and chapter takeaways.
