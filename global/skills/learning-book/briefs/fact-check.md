# Fact-check brief

For a model from a different family than the writer, checking claims against sources.
Read only. Start the brief with `common.md`, keeping the book, lab, long-job, cleanup
and report parts and dropping ownership.

How to fill it in:

- Scope it to one chapter, or to a revision range after a fix round. A whole book is
  too much for one turn.
- A diff of the prose alone can hide what it breaks. Include changed labs, and the
  unchanged passages that depend on what changed.
- List the tools and versions the book names, and any claims you already doubt.

---

Fact-check `<SCOPE>` of the book. Read only: don't edit, commit or push. Your final
message is the report.

Check every claim in scope:

1. Each quote or paraphrase of a source is faithful, word for word where quoted, and
   in context. Give its location in the source.
2. Each claim about a tool, library, standard or event: confirm it by running code,
   reading the source (`file:line`) or fetching the official documentation (URL) at the
   version the book names: `<TOOLS_AND_VERSIONS>`.
3. Each printed command and output: rerun it with `<VERIFY_CHAPTER_COMMAND>`, and
   compare printed code with the lab file it comes from.
4. Each definition, including the book's own terms ("stock", "baseline"): does it
   match the original author or common usage, and does each example have the defining
   property? Compare definitions and verdicts across the chapter, catalogue,
   glossary and exercises.
5. Each recall answer and case verdict: is it right? Try the code ones.
6. Universals ("all", "every", "never", "only"): look for a counterexample.
7. Text that is misleading or overstated even if literally true, positions stated as
   fact, and contradictions with text elsewhere in the book.

`<SPECIFIC CLAIMS TO CHECK, if any>`

Don't stop at the first problems. Cover the whole scope, and say which pages or lines
you could not reach.

## Report

Numbered problems first, each with: a few quoted words and `file:line`, a verdict (WRONG,
MISLEADING or UNVERIFIABLE), the evidence (output, source link or line), and a fix. Then
a short list of claims you checked and found correct.
