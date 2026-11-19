---
name: learning-book
disable-model-invocation: true
description: Write a personal learning book and typeset it as a PDF. Use when someone wants long material they will study and act on, such as a book, a course, or an owner's manual; not for short docs, READMEs or single pages.
---

# Learning book

You know how to write and teach. This file holds what earlier books got wrong anyway,
and the build. Open each checklist at its trigger:

| When | Open |
|---|---|
| Before the first lab, and before accepting a lab change | `checklists/labs.md` |
| Accepting any worker's result | `checklists/review-worker.md` |
| After every batch of changes, and before a whole-book blind read | `checklists/flow.md` |
| Before sending a checkpoint PDF, and before a release | `checklists/release.md` |

## 1. Scope

Load `grill-me` before planning. Settle what the reader already knows, their goals in
order, the page and hour budget, the real cases to use, where exercises run and what
they must not touch, screen or print, and which models may do which roles at what
budget.

The reader usually doesn't know what the field holds, so don't ask them to design the
book. After the first round, survey the field yourself and propose a chapter-level
table of contents: each chapter's takeaway, why it's in, its page budget, and what you
leave out. The grill ends when the reader approves it.

Write a plan file with the reader, goals, models and one scope statement; every brief
points at it. The front matter states the same scope and describes the book as it is,
never promising unwritten chapters. Prose drifts narrower than the scope ("the service"
in a book about a whole app), so judge framings against that statement.

Give each book a private repository with `book/` and `lab/`, and land changes through
PRs. If the book might be shared, describe its reader as a group and quote other books
only briefly, inside your own explanation.

## 2. Plan

Settle these before drafting; each one added later costs a pass over every chapter.

- **Coverage comes from the scope.** The reader's background decides examples and
  depth, never which needed topics stay. The page budget is a ceiling: never add a
  section to fill pages or to move a block, and fix pagination in the layout.
- **Say what's new.** Name what this book teaches that existing material doesn't. An
  outline that would fit an older book on the topic has missed the point.
- **Audit promises.** A book that replaces a source lists the source's ideas section by
  section, each marked covered, thin or out of scope, and redoes the audit after a
  restructure. Lessons meant to transfer across stacks state the principle before the
  lab and show a second stack where it behaves differently.
- **Leave things out on the page.** Admit a tool only for a reader decision the existing
  material can't show. Topics that lose on scope go on a "what this book leaves out"
  page, each with one checked source.
- **Content before form.** A table, then/now pair, parallel list or heading chosen
  because it looks rigorous gets filled to fit. Keep a column or item only if deleting it
  loses an answer to a reader's question. Name verdict labels after their test (Apply,
  Built in, Obsolete), not as praise; write the rule for each verdict before the first
  entry.
- **Label early.** Give every heading you will link to a label from the start.
  Retrofitting 34 labels cost a full pass.
- **Lab and book.** The book gives setup once, then the command the reader runs and the
  output that settles the point; the lab carries modes, variants and detail. Name lab
  folders by topic (`ch05-lazy-load`). Add a markdown file per lab only for depth the
  book lacks.
- **Sample chapter.** Build one chapter end to end (prose, exercise, fact-check, PDF),
  review it with the user, and draft the rest from it.

Teach a prerequisite inside the first chapter that needs it. Show a real case and let
the reader judge before the verdict. Recall questions test decisions, with answers at
the chapter end. Take positions and name what they cost. Run `unslop` over every new
passage before you commit it.

## 3. Trust

One wrong fact makes the reader doubt every page.

1. Print only output from a real run, trimmed but never edited. That covers fragments
   quoted in sentences and illustrative lines such as a plan's `Filter:`. Labs print
   one line per outcome so the book never needs to edit output.
2. Check claims against primary sources at the version the book names, and definitions
   against the original author. A definition that bakes in one implementation is wrong
   for the next reader. State the book's own choices as choices.
3. A guarantee needs a reproduction that fails without the mechanism, in worked designs
   and sample pages as well as labs. A convergence claim includes concurrent writers.
4. Review three ways:
   - a different model family fact-checks each chapter and each fix round's diff;
   - the strongest allowed model (Opus or Sol) checks guarantees before risky designs
     are built and once they run, and gates every new section. Cheaper checkers passed
     sections in which Sol then found must-fix errors, every round, and the findings
     clustered in the newest prose. Fixes create new races near the old ones, so
     rechecks go to the same reviewer with its earlier findings;
   - a blind reader from another family reads the frozen PDF after each major revision.
     It finds what informed readers miss: an unannounced schema switch, an exercise
     before its rules, a story split across a chapter.
5. Show real mistakes and what they cost. When the book covers a system you built, its
   costs sit next to its wins.

## 4. Typeset

Write `book.typ` against this skill's `template.typ`. The template header lists the
interface and `sample/book.typ` uses all of it. Keep SVG diagrams next to `book.typ`
with quoted font names: `'Source Sans 3'`, `'Source Serif 4'`, `'JetBrains Mono'`.
The template is screen-first; for print, change the copy beside `build.py` and check
binding margins.

Label sections as `== Heading <sec-topic>` and link with `#link(<sec-topic>)[Heading]`.
In tables, use `auto` only for short-label columns and give text columns `fr` weights:
an `auto` column sizes to its longest cell and squeezes the rest into one-word lines.

```bash
python3 <this skill>/build.py path/to/book.typ   # writes path/to/book.pdf
```

The build fetches Typst, fonts and Poppler from nixpkgs, reduces short chapter endings,
and fails on broken answer pages, links and labels and on horizontal overflow. It can't
see vertical overflow or inside diagrams. After changing the template or checker,
confirm a deliberately broken link, label or pin still fails the build.

Render every page and look at it at reading size; a squeezed table passed a 50 dpi
contact sheet. Check the build's page-fill report.

```bash
nix shell nixpkgs#poppler-utils -c pdftoppm -r 80 -png book.pdf out/page
```

Reviews check that the book is right, not that it teaches. To test teaching, give a
reader a checkable task for the top goal, such as a codebase with planted bugs, and
revise where they get stuck.

## 5. Run workers

Orchestrate with the strongest model the user allows. A cheaper orchestrator followed
every rule and still produced a generic outline, structure out of proportion to the
book, and a sample chapter that missed its own takeaway. You own the assembled book:
choose each fix on what is best for the reader, never on what is less work, and record
the findings you decline.

What workers got wrong, and what each brief therefore says:

- **Spec as edits.** Workers copy edit notes ("replace X with three sharper questions")
  into the prose. Write the spec as the content the reader should see, and search new
  prose for sentences from the brief.
- **Anchoring.** A candidate named in a ranking brief, even as an example, tilts the
  result toward it. Give criteria, name no candidates.
- **Placement.** Parallel workers put their sections where their own brief suits, not
  where the chapter's argument needs them. Name each section's neighbors.
- **Style rules.** A companion lab's script embedded Python because its brief didn't
  forbid it. Every brief, lab ones included, carries the code and prose style rules.
- **Passing by editing.** Workers edit checks or tests to make their output pass, and
  add tests that assert printed transcripts the verifier already checks. Forbid both
  unless the brief assigns test work.
- **Deleting what's hard.** Told to back every output with a run, a worker deleted a
  failure demonstration instead of making it replay. Say: make it replay or report it.
- **Heavy fixes.** A savepoint-and-retry allocator replaced what one `INSERT ... ON
  CONFLICT ... RETURNING` did. Ask for the smallest correct fix, and check it for the
  same bug in a new form.
- **Splicing.** Narrowed claims were spliced in without rereading: dangling referents,
  choppy sentences, overlong lines. The fixer rereads the paragraph and its neighbors.
- **Safety filters.** A provider's filter blocked a privilege-escalation lab, and a
  worker had quietly dropped the demonstration before that. Name such labs neutrally,
  describe the technique without trigger words, and route it to a model that accepts it.
- **Unfinished turns.** Cheaper workers ended their turn while their builds and
  sub-agents still ran. Tell them to wait, and verify their work yourself.

Isolation, all from real breakage:

- Give each worker files nobody else owns, and each lab worker its own git worktree
  under a short path such as `~/Work/<repo>-wt12`: a PostgreSQL socket path over 107
  bytes fails. Concurrent workers in one checkout broke the build mid-edit.
- Give each worker its own database, and its own server when a probe reads server-wide
  state. Open transactions from other workers stalled a cluster-wide snapshot horizon.
- A test module that set `os.environ` at import redirected every later test's
  subprocesses. Forbid module-level environment changes.
- Stop processes by PID; `pkill -f <worktree path>` also kills that worktree's
  PostgreSQL. Negative-control copies filled the `/tmp` quota: leave out `.venv`,
  database and companion directories, and delete the copy afterwards.

A whole-book review doesn't fit one turn. Split it into page ranges at a pinned
revision, ask for the ranges not covered, and keep going in the same thread until every
range has a report.

If another agent started you, every turn you end wakes it. End a turn only for a real
question or a stage ready for review. While workers run, block on them with the
harness's wait (in T3, `t3_thread_wait` with `untilDelegatedWorkSettled`, repeated on
timeout), even when a tool suggests ending your turn.
