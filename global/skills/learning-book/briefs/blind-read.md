# Blind read brief

For a reader who sees only the frozen PDF, judging flow and teaching. Run it after each
major revision, with a model from a different family than the writer. Read only. Don't
start it with `common.md`: the reader must not see the repository or sources.

How to fill it in:

- Freeze the PDF under a name that includes its source commit, so it can't change
  while the reader works.
- Give only the reader, their goals and the settled decisions. Settled decisions keep
  the reader from spending the turn re-arguing them; anything more makes the read less
  blind.
- To split a long book across readers, give every reader the whole PDF and assign each
  a page range. Read across the range boundaries yourself afterwards.
- For a targeted reread, add the earlier findings and the pages that changed.

---

Read-only review. Don't edit any file and don't delegate. Your final message is the
report.

Read this book as its reader would and report what stops it from reading as one
excellent book. You get only the PDF: `<FROZEN_PDF_PATH>` (`<N>` pages). Don't read the
sources or any repository. Extract and render pages with:

```
nix shell nixpkgs#poppler-utils -c pdftotext -layout -f N -l N <pdf> -
nix shell nixpkgs#poppler-utils -c pdftoppm -r 70 -png -f N -l N <pdf> <out>
```

The reader: `<WHO THEY ARE AND WHAT THEY KNOW>`. Their goals, in order: `<GOALS>`.
Your pages: `<RANGE, or the whole book>`.

Look for:

1. Order: a term or idea used before it is taught, an exercise that comes before the
   rules it needs, an answer that needs untaught material.
2. Coherence: chapters that contradict each other, the same thing explained twice, a
   running example that changes without notice, a section that reads bolted on, a
   reference that lands on the wrong page.
3. Pacing: sections too long or too thin for what they teach, material in the wrong
   chapter.
4. Prose that slows the reader: padding, recaps, mannered phrasing, one concept under
   several names, text that sounds machine-written.
5. Teaching: recall questions that test trivia, exercises that don't exercise the
   point, output that doesn't show what the text claims.
6. Layout: diagrams you can't read at page size, tables squeezed into narrow columns,
   headings stranded at a page bottom, blank or half-empty pages.

Settled decisions, don't re-argue them: `<LIST>`.

## Report

Findings most severe first, each with PDF page (and printed page number if different),
quoted phrase, the problem and a concrete fix. Separate "must fix" (the reader is
confused, misled or slowed badly) from "taste". List the pages you read closely and
those you skimmed.
