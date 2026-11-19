# Research brief

For a worker gathering sources, cases and lab drafts before a chapter is written. Start
the brief with `common.md`. The writer works from this pack, so a wrong fact here
spreads.

If the chapter needs a ranking or a choice between options, give the criteria and your
reasons for them in the brief, and name no candidates. A candidate named even as an
example tilts the result toward it.

---

Build a research pack for `<CHAPTER>`, topic `<TOPIC>`. Don't write book prose. Write
the pack to `<HANDOFF_PATH>` and leave it there for the writer.

## The pack

1. For each idea in the topic, what the primary source says it is for, how it works,
   when to use it and its warnings, with the precise location (line, page, section).
   Quote exactly only where the wording matters.
2. How current tools at `<TOOLS_AND_VERSIONS>` implement or replace each idea, each
   claim with a documentation URL or a lab run that proves it.
3. Real public cases (incidents, bug reports, postmortems) that show a mistake in this
   topic, each with its URL and the facts checked against it. Mark anything unverified.
4. Surprising behaviors worth showing, each proven by a run whose output is in the pack.

## Lab drafts

Only if this brief assigns them, in `<YOUR_LAB_PATHS>`:

- Small scripts, one behavior each, printing one line per outcome so the book can quote
  the output directly.
- Don't change shared lab modules (`<SHARED_MODULES>`); the book's printed output
  depends on them. Put new models in your own module with names that can't collide.

## Rules

- Accuracy over volume. A wrong fact is worse than a missing one.
- Fetch every page you quote; never quote from memory.

## Report additions

Files written, open questions, and everything you could not verify.
