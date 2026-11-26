---
name: study-book
disable-model-invocation: true
description: Write a personal study book and typeset it as a PDF. Use when someone wants long material they will study and act on, such as a book, a course, or an owner's manual; not for short docs, READMEs or single pages.
---

# Study book

You know how to write, teach and review. Earlier books still went wrong in the ways
below.

## Principles

1. **You own the book.** Workers and reviewers propose; nothing counts until you check
   it. Workers report unverified success, so read changes to checks and tests first,
   then prose line by line. Cheaper writers leave mannered lines, recaps, hedged claims,
   dropped explanations and confident wrong asides. Fix for the reader, not less work.
2. **Nothing is true until it ran.** Print only real run output, trimmed never edited,
   including sentence fragments and illustrative lines. Check claims against primary
   sources at the named version and definitions against the original author. Guarantees
   need a reproduction that fails without the mechanism, in worked designs and labs.
3. **Strong models gate, cheaper ones filter.** Cheap fact-checkers missed must-fix
   errors in new prose every round. A strong reviewer checks risky designs before you
   build them and gates every new section and guarantee. For judgment work such as
   recurring ideas and their names, run a strong pass beside the cheap one so the cheap
   sweep doesn't anchor the answer.
4. **Fix the class, not the instance.** Name each finding's class and search for
   siblings.
5. **The scope decides coverage.** One scope statement lives in the plan and front
   matter, describing the book as it is and never promising unwritten chapters. Reader
   background sets examples and depth, never which needed topics stay. The page budget
   is a ceiling, pagination is fixed in layout not content, and narrower framing such as
   naming one layer in a whole-system book is a scope bug.
6. **Content before form.** Tables, lists or headings chosen for rigor get filled to
   fit. Keep a column or item only if deleting it loses an answer to a reader question.

## Scope and plan

- Load `grill-me`. Settle background, what must stick months later after details fade,
  priority-ordered can-do goals, page and hour budget, real cases, where exercises run
  and must not touch, screen or print, and allowed models per role. Survey the field
  yourself, propose a chapter TOC with can-do takeaways, budgets and exclusions, end on
  approval, and record everything in a plan file every brief cites.
- Give each book a private repository with `book/`, plus `lab/` for runnable labs, and
  ship the PDF as a release asset when hosted. Source material never enters the repo.
- If shared, describe the reader as a group and quote other books briefly inside your
  own explanation.
- Name what this book teaches that existing material doesn't; an outline matching an
  older book has missed the point.
- When replacing a source, audit its ideas section by section as covered, thin or out of
  scope, again after any restructure. Covering it is the floor, not the frame. Open
  chapters on the reader's problem, explain in the book's voice with one citation, and
  quote only where the source's words carry the argument.
- Transferable lessons state the principle before the exercise or lab and show a second
  context where it behaves differently.
- Admit a tool only for a decision existing material can't show; put losers on a "what
  this book leaves out" page with a checked source.
- Decide teaching devices book-wide before drafting, because per-chapter choices drift.
- Plan return use and unprompted transfer before drafting. Decide where the reader
  combines chapters without a chapter heading naming the tool, such as part-end
  synthesis cases or a capstone task, and how a returning reader enters with a job, such
  as reading paths, a checklist or a symptom index.
- Tell the reader in front matter to predict before exercises and answer prompts before
  reading answers.
- If core principles recur across chapters, introduce each unnamed in context, ask the
  reader to compare and name it on a later meeting, and index them at the back.
- Label every linked heading from the start and point glossary entries at sections.
- If the book rates options, name labels after their test, never praise words, state
  each label's rule before the first entry, and have every rating say when it holds and
  what evidence would change it.
- Point to one official, free place to learn a tool when printed code needs it, the book
  tells the reader to adopt it, or a position recommends it without teaching it. Print
  the full URL and verify the pointer's claim against that page.
- Build one sample chapter end to end and review it with the user before the rest.

## Write to teach

- Every section, exercise and question serves a stated can-do goal and what must stick;
  cut or move out material that serves none.
- Open each decision section with its crux question in plain prose, or set off visually
  only for a chapter's key pivots. Never repeat a labelled opener in every section, and
  never state the rule before the reader reasons about the problem.
- Build the mechanism until the reader can predict the outcome, ask for a prediction
  before showing the trace, and put your position after its reasons with its cost and
  the evidence or threshold that would flip it.
- Nothing before an exercise's or question's answer may give it away, code comments
  included; blind readers flagged prompts whose answer was already in view.
- Recall questions and cases put the reader in an unseen scenario; answers name the
  deciding force rather than restating the chapter body.
- Fix dense or stumbling passages with a worked example, a compact table or an annotated
  output line, not more prose caveats.
- Draw a small SVG diagram when prose tracks a timeline, an interleaving, state
  transitions or a multi-hop flow; strong models default to prose walls otherwise.
- Gloss specialist terms and forward references in one clause on first use so the reader
  can keep reading without flipping ahead.
- Run `unslop` over every new passage before committing, then reread every new table
  cell, caption, diagram label and shortened sentence for every, any, only or always,
  a single outcome where the real one depends on a race or a commit, and one tool's
  behavior stated as the standard's.

## Review and finish

- A different family fact-checks each chapter and fix diff, with a reproduction or a
  source for every finding.
- Besides fact-checks and principle 3's strong gate, a blind reader from another family
  reads the frozen PDF after each major revision to catch unannounced example switches
  and exercises before their rules. Add one fresh-context strong reader for book-wide
  defects.
- Reviews check accuracy, not teaching. Run a reader probe in book order on rendered PDF
  or extracted text, never source files where answers sit inline. Have a cold reader
  write what stuck in at most 150 words without looking back, answer recall questions
  before peeking and self-grade, and quote where they stumbled. Revise and re-run the
  same probe to confirm improvement, and test the top can-do goal with a checkable task.
- Correctness rounds pull a book toward a spec. Narrow the claim before extending a
  worked example when a review finds a gap; when each round's findings land in prior
  additions, re-cut the scope instead of fixing again.
- After every batch, build and read changed sections with neighbors; before each blind
  read, read the whole book. Check running-example names, one home per case and idea,
  scope framings, exercise rules, and that readers can do each chapter's can-do goals.
- Where the book uses recurring threads, check the map mechanically so every callback
  comes after its naming chapter and carries a reason; past about four per chapter they
  read as slogans.
- Before release, run a cross-chapter contradiction sweep over thresholds, ratings,
  glossary definitions, cross-reference targets and universal claims.
- The book is done when every range is reviewed, no supported blocker or major finding
  remains, and the blind read has no "must fix".

## References

- Load `references/labs.md` when the book has runnable labs or code extracted from them.
- Load `references/delegation.md` when briefing workers, running parallel batches, or
  running book-wide sweeps and blind comparisons.
- Load `references/typeset.md` when setting up `book.typ`, checking layout, or packaging
  a release build.
