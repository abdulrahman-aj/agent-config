# Writer brief

For new chapters, sections or catalogue entries. Start the brief with `common.md`.

How to fill it in:

- Write the spec as the content the reader should see: the claims, the example, the
  position and its cost. Never write edit notes ("replace X with three sharper
  questions"); workers copy them into the prose.
- Name the neighbors: the section before and after, and what each teaches. Where they
  aren't drafted yet, give their descriptions from the plan.
- Give the sources you already found, so the worker doesn't start from memory.

---

Write `<WHAT>` for the book. You own `<YOUR_FILES>`.

## Read first

1. `<PLAN_FILE>`: the reader, the goals and where this piece fits.
2. The neighbors: `<BEFORE>` and `<AFTER>`. Your text picks up what they teach and must
   not repeat it or rely on anything taught later.
3. The model chapter, `<MODEL_CHAPTER>` (the skill's `sample/book.typ` until the book
   has an approved one). Copy its markup for terminal blocks, exercises, recall
   questions and answers.
4. The glossary, `<GLOSSARY_FILE>`, if there is one. Use its terms; don't redefine a
   term the book already defined. Report new terms with one-line definitions.

## The content

`<SPEC: for each section, the point it makes, the example it uses, the output that
settles it, the position the book takes, what that costs and when you would choose
differently. Sources for each claim.>`

## Rules for this piece

- Every quoted output comes from a run in the lab environment, pasted trimmed but
  unedited. Delete probe scripts afterwards.
- Give each new section heading a label such as `<sec-topic>`, and link to other
  sections by label.
- Recall questions test a decision ("here is a diff: merge it or not?"), not trivia.
  Answers go at the chapter end.
- Keep printed code to the idea. Print the lines that make the point and leave the
  rest in the lab. If a short implementation would hide failure modes that matter in
  production, say what it demonstrates and what a real one must handle.
- Before you finish, check that every code fence and Typst block you opened is closed,
  and that no sentence from this brief appears in the prose.
- If a build you are allowed to run fails in a file you don't own, report the error.
  Retry only if you know another worker is mid-edit there; never touch that file.

## Report additions

Give a section list with a page estimate, and the source for every claim you added.
