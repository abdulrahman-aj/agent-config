# Research brief

For a worker gathering sources, cases and lab drafts before a chapter is written. Start
the brief with `common.md`. The writer works from this pack, so a wrong fact here
spreads.

---

Build a research pack for `<CHAPTER>`, topic `<TOPIC>`. Don't write book prose. Write
the pack to `<SCRATCH_DIR>/research/<CHAPTER>.md` and lab drafts under
`<LAB_DIR>/<CHAPTER_FOLDER>/`.

## The pack

1. Exact quotes from `<SOURCE_PATH>` for each idea in the topic: what it is for, how it
   works, when to use it and the author's warnings. Give line numbers.
2. How current tools at `<TOOLS_AND_VERSIONS>` implement or replace each idea, each claim
   with a documentation URL or a lab run that proves it.
3. Real public cases (incidents, bug reports, postmortems) that show a mistake in this
   topic, each with its URL and the facts checked against it. Mark anything unverified.
4. Surprising behaviors worth showing, each proven by a lab run whose output is in the
   pack.

## Lab drafts

- Small scripts, one behavior each, printing one line per outcome so the book can quote
  the output directly.
- Don't change shared lab modules (`<SHARED_MODULES>`); the book's printed output depends
  on them. Put new models in your own module with names that can't collide.

## Rules

- Accuracy over volume. A wrong fact is worse than a missing one.
- Fetch every page you quote; never quote from memory.

## Report additions

Files written, open questions, and everything you could not verify.
