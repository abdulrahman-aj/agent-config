# Writer brief

For new chapters, sections or catalogue entries. Start the brief with `common.md`.

How to fill it in:

- Write the spec as the content the reader should see: the claims, the example, the
  position and its cost. Never write edit notes ("replace X with three sharper
  questions"); workers copy them into the prose.
- Name the neighbors: the section before and after, and what each already teaches.
- Give the sources you already found, so the worker doesn't start from memory.

---

Write `<WHAT>` for the book. You own `<YOUR_FILES>`.

## Read first

1. `<PLAN_FILE>`: the reader, the goals and where this piece fits.
2. The neighbors: `<FILE:SECTION before>` and `<FILE:SECTION after>`. Your text picks up
   what they teach and must not repeat it or rely on anything taught later.
3. The book's markup, by example: `<MODEL_FILE>`. Copy its patterns for terminal blocks,
   exercises, recall questions and answers.
4. The glossary, `<GLOSSARY_FILE>`. Use its terms; don't define a term the book already
   defined.

## The content

`<SPEC: for each section, the point it makes, the example it uses, the output that
settles it, the position the book takes and what that costs. Sources for each claim.>`

## Rules for this piece

- Every quoted output comes from a probe or lab run against your database, pasted trimmed
  but unedited. Delete probe scripts afterwards.
- Give each new section heading a label, `<sec-topic>`, and link to other sections by
  label, not by chapter number in prose.
- Recall questions test a decision ("here is a diff: merge it or not?"), not trivia.
  Answers go at the chapter end.
- Keep printed code to the idea. If the full lab code is longer than the point needs,
  print the lines that make the point and leave the rest in the lab.
- Before you finish, check that every code fence and Typst block you opened is closed,
  and that no sentence from this brief appears in the prose.
- If you build the PDF and it fails in a file you don't own, another worker is mid-edit.
  Wait and retry; never touch that file.

## Report additions

Give a section list with a page estimate, and the source for every claim you added.
