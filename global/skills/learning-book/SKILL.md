---
name: learning-book
description: Write a personal learning book and typeset it as a print-quality PDF. Use when someone wants long material they will study and act on (a book, a course, an owner's manual for a system); not for short docs, READMEs or single pages.
---

# Learning book

The reader takes a typeset PDF more seriously than a web page, and stops trusting the
whole book after one wrong fact or one paragraph of filler. The content process below
cuts what the reader won't use, and the template typesets the rest like a modern
technical book.

## 1. Scope it with a grilling session

Load the `grill-me` skill and run it before planning anything. A book's frontier
questions:

- Who reads it, and what do they already know well? (Never teach that.)
- What will stick with the reader, and what will they do with it? Get concrete
  takeaways, each phrased as something the reader can do afterwards.
- Which prerequisites do they lack, and where does each first become necessary?
- Reading budget: pages and hours, exercises included.
- Exercises: where the reader runs them (their own machine, read-only? a disposable VM or
  scratch repository?) and what must never be touched.
- Case studies: which real events (PRs, incidents, mistakes) the book can use.
- Where the source and PDF live. Keep both outside any repository unless asked, for
  example under `~/.local/share/<project>/book/`.
- Title, subtitle, and the ultimate goal in one sentence.

## 2. Plan the arc

Write the chapter list before any prose, each chapter with the takeaway that justifies
it. A chapter or section that serves no takeaway is cut; no university-style material
that gets taught and forgotten. Teach a prerequisite just in time, inside the first
chapter that needs it, never as a standalone primer. Define each term once, at first use,
and refer back only to ideas already taught. Spend pages where the difficulty is.

Each chapter usually runs: what you'll be able to do, the background it needs, the
material itself, a "try it" exercise, a real case, recall questions. That is a guide, not
a template: vary the shape when the content calls for it.

- **Read, try, recall.** Exercises use exact commands with real output. A case states
  what happened and asks the reader to judge before the verdict. Recall questions test
  judgment ("here is a diff: merge or not, and why?", "what would you check first?"),
  never trivia ("which file holds X?") unless knowing it changes a decision. Answers go
  at the chapter end.
- **Take positions.** For each design choice, give the reasoning, say what you would pick
  and which trade-offs that accepts.

## 3. Trust rules

What makes the reader stop taking a book seriously, and what to do instead:

1. One wrong fact or failing command. Run every command and check every claim against
   the source; quote real output, trimmed but not edited.
2. AI prose tells: same-shaped sections, "it's worth noting", "crucially", reflexive
   triplets, bold everywhere, recap boxes. Run the `unslop` skill over every chapter.
3. Fake depth: analogies that break under a follow-up question, decorative diagrams. Draw
   a diagram only for a real mechanism.
4. Talking down. Don't define what the reader already knows.
5. Success stories only. Show the real mistakes, with what they cost and what changed.
6. No positions. See section 2.
7. Recall that tests trivia. See section 2.
8. Padding. No intros that announce the chapter, no summaries that repeat it.
9. Synonyms for one concept. One term per concept, used consistently; collect them in
   the glossary.
10. Victory laps. When the book covers a practice or a system you built, show its costs
    and open problems next to its wins.

Before typesetting, a model from a different family than the writer fact-checks every
claim, path and command against the source. Fix or cut what fails.

## 4. Typeset

Write the book directly in Typst as `book.typ` against this skill's `template.typ`. Its
header comment lists the whole interface; `sample/book.typ` uses every part of it and is
the model to copy. Diagrams are SVG files next to `book.typ`; name fonts in them as
`'Source Sans 3'`, `'Source Serif 4'` or `'JetBrains Mono'`, quoted.

```bash
python3 <this skill>/build.py path/to/book.typ   # writes path/to/book.pdf
```

The build fetches Typst, fonts and poppler from nixpkgs (no system installs), copies the
template next to `book.typ`, nudges chapter spacing so no chapter ends on a near-empty
page, and runs `check.py`. It fails on unresolved answers, pointers that land on the
wrong page, and text outside the margins. It cannot see inside diagrams; the visual pass
below covers those. It reports short pages with a likely reason;
treat every "unexpected" one as a layout bug to fix.

If others will build the book, copy `build.py`, `check.py` and `template.typ` into its
repository (for example `tools/typeset/`, with a note naming the skill commit) and add a
`make pdf` that runs `nix shell nixpkgs#python3 -c python3 tools/typeset/build.py
book/book.typ`. `build.py` uses the template next to itself, so the copy needs no edits.
Test it from a fresh clone.

## 5. Look at it

Render every page and look at each one:

```bash
nix shell nixpkgs#poppler-utils -c pdftoppm -r 80 -png book.pdf out/page
```

Look for overflowing diagram labels, tables squeezed into hyphenated stacks, boxes split
badly across pages, and headings stranded at a page bottom. Then start a blind reviewer
from a different model family (see the model table in the global agent instructions).
Give it only the PDF, the page PNGs and this skill's bar, then fix what you agree with.
