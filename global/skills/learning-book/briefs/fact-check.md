# Fact-check brief

For a model from a different family than the writer, checking claims against sources.
Read only, so it needs only the book, database and report parts of `common.md`.

How to fill it in:

- Scope it to one chapter, or to a diff (`git diff <OLD> <NEW> -- <BOOK_DIR>`) after a fix
  round. A whole book is too much for one turn.
- List the tools and versions the book names, and any claims you already doubt.
- Send fixes back to the same checker until a round comes back clean.

---

Fact-check `<SCOPE>` of the book. Read only: don't edit, commit or push. Your final
message is the report.

Check every claim in scope:

1. Each quote of `<SOURCE_AUTHOR>` is word for word in `<SOURCE_PATH>`, and each
   paraphrase is faithful in context. Give line numbers.
2. Each claim about a tool, library, standard or event: confirm it by running code,
   reading the source (`file:line`) or fetching the official documentation (URL) at the
   version the book names: `<TOOLS_AND_VERSIONS>`.
3. Each printed command and output: rerun it with `<VERIFY_CHAPTER_COMMAND>` and compare
   printed code with the lab file it comes from.
4. Each recall answer and case verdict: is it right? Try the code ones.
5. Universals ("all", "every", "never", "only"): look for a counterexample.
6. Text that is misleading or overstated even if literally true, and positions stated as
   fact.
7. Contradictions with text elsewhere in the book.

`<SPECIFIC CLAIMS TO CHECK, if any>`

Don't stop at the first problems. Cover the whole scope, and say which pages or lines
you could not reach.

## Report

Numbered problems first, each with: a few quoted words and `file:line`, a verdict (WRONG,
MISLEADING or UNVERIFIABLE), the evidence (output, source link or line), and a fix. Then
a short list of claims you checked and found correct.
