# Worker traps

Workers on earlier books fell into each of these. Put the ones for the worker's role in
its brief, in your own words; a brief written without them repeats the mistakes.

## Every worker except the blind reader

- **Ownership.** Name the files the worker may edit. It reports changes that belong
  elsewhere with the exact text instead of making them. It never edits checks, the
  verifier, build tools or tests to make its output pass, except work the brief assigns;
  if one looks wrong, it stops and reports. It doesn't commit, push or rebuild the PDF
  unless told to.
- **Inputs.** Point it at the plan file first: every sentence it adds serves one of the
  plan's goals. Give the current PDF for page references and the primary sources. It
  reads large texts with `grep -n` and `sed -n` ranges, never prints them whole and
  never copies them into the repository.
- **Isolation.** Each worker that runs a lab gets its own database, and its own server
  when a probe depends on server-wide state (system views, replication, settings).
  Environment changes are scoped to the test or subprocess that needs them, never set at
  module level.
- **Evidence.** Copy the trust rules (SKILL.md section 3) and the lab rules (`labs.md`)
  into the brief; workers break them first by quoting output they didn't run and by
  citing memory as a source. It runs the checks its assignment affects, and every source
  goes in the report.
- **Voice.** Match the model chapter: plain, direct, takes positions. No em dashes or
  dashes made of other characters, no filler, recaps or announcements. Use the
  glossary's terms, and they/them for people. No Python or other languages embedded in
  shell scripts.
- **Long jobs.** Give the literal commands to start a long job and wait for it. A worker
  that ends its turn while a job runs never sees it finish.
- **Delegation and cleanup.** It doesn't delegate, or delegates only to models that cost
  the same or less. Scratch files go in a named directory; it deletes probes and copies,
  drops its databases and stops its servers, keeping any handoff file.
- **Report.** One final message: what changed as `file:line` and why it is correct, the
  verification run and its result, edits needed in files it doesn't own, disagreements
  with the brief and their evidence, unfinished checks with the blocker and the last
  known result, and open questions.

## Research

- When the chapter needs a ranking or a choice between options, give the criteria and
  your reasons and name no candidates. A candidate named even as an example tilts the
  result toward it.
- The pack, written to a handoff file, has:
  - for each idea, what the primary source says it is for, how it works, when to use it
    and its warnings, with the exact location, quoting exactly only where the wording
    matters;
  - how current tools at named versions implement or replace it, each with a URL or a
    run;
  - real public cases with URLs and checked facts, unverified ones marked;
  - surprising behaviors, each with a run's output.
- It fetches every page it quotes. Accuracy beats volume: the writer works from the
  pack, so a wrong fact spreads.
- Lab drafts are small scripts, one behavior each, printing one line per outcome. They
  never change shared lab modules; new data models go in the worker's own module with
  names that can't collide.

## Writer

- Write the spec as the content the reader should see: claims, example, the output that
  settles it, the position and its cost. Edit notes ("replace X with three sharper
  questions") get copied into the prose. Afterwards, search the prose for sentences from
  the brief.
- Name the neighboring sections and what each teaches, from the plan where they aren't
  drafted. The new text picks up what they teach without repeating it or relying on
  anything taught later.
- Give the sources you already found, so the worker doesn't start from memory.
- It copies the model chapter's markup (the skill's `sample/book.typ` until the book has
  an approved chapter), labels every new heading, uses glossary terms and reports new
  ones with one-line definitions.
- It checks every code fence and Typst block it opened is closed.
- A build failing in a file it doesn't own gets reported, never fixed. It retries only
  when it knows another worker is mid-edit there.

## Fact-checker

- Scope it to one chapter or one fix round's diff. Include changed labs and the
  unchanged passages that depend on what changed; a prose-only diff hides what a lab
  change breaks. List the tools and versions the book names and the claims you already
  doubt.
- It checks quotes word for word and in context, tool claims by running code, reading
  source or fetching the docs at the named version, printed output by replaying it,
  definitions against the original author (the book's own terms too, across chapter,
  catalogue, glossary and exercises), every recall answer and verdict, universals, text
  that is misleading though literally true, positions stated as fact, and contradictions
  with the rest of the book.
- It covers the whole scope instead of stopping at the first problems, and says what it
  didn't reach. Each problem gets a verdict (WRONG, MISLEADING, UNVERIFIABLE), evidence
  and a fix, followed by a short list of claims checked and found correct.

## Guarantee reviewer

- Use it before a risky design is built (what interleaving, crash or retry breaks it,
  and what would you observe), once the lab runs (reproduce those scenarios), and after
  each fix round, because fixes create new races near the old ones.
- Worked designs and sample pages carry guarantees too, not only labs.
- A finding counts only with a reproduction or a cited primary source. It reports
  BLOCKER and MAJOR only, leaves prose and flow alone, and says "none" when nothing
  meets the bar.

## Fixer

- Give each finding verbatim with its evidence, grouped by file so no two workers share
  a file. Say which findings you already agree with, and in one sentence how another
  worker's change affects this one.
- A finding is a claim. It checks each one first and reports, with evidence, the ones it
  disagrees with.
- It picks the smallest correct fix that keeps the teaching (one atomic statement beats
  a retry loop around several), prefers replacing text to adding it, keeps the chapter
  about the same length, and checks the fix for the same class of bug in a new form.
- It never hedges a claim the book can support and never cuts an explanation to make a
  finding go away. If a paragraph goes, it says what the paragraph taught and where that
  now lives. After narrowing a claim it rereads the whole paragraph and its neighbors
  for dangling referents and choppy sentences, and rewraps to the source's line width.
- It never resolves an unverified failure demonstration by deleting it: it makes it
  replay or reports the blocker.
- A fixed guarantee gets a regression test that calls the lab's real function, runs the
  interleaving and observes the outcome before teardown or retries could produce it,
  plus a negative control in an isolated copy (heavy directories left out) that reverts
  only the mechanism and fails for the claimed reason. Changed lab output goes back into
  the book and is replayed.

## Diagram worker

- Name an approved diagram as the style model, or for the first one the fonts, colors,
  width and maximum height taken from the template.
- For each diagram, name the section and the lab run or source behind it. It draws only
  what that evidence shows: no icons, decoration or title inside the SVG.
- Fonts are the template's, quoted. Every label sits inside its box with margin, and no
  text crosses a line.
- It renders each file at twice its width and looks at the image before finishing: `nix
  shell nixpkgs#librsvg -c rsvg-convert -w <2x width> file.svg -o out.png`. It reports
  what backs each event, value and order, a sentence-case caption, and anything in the
  text that disagreed with the lab.

## Blind reader

- It sees only the PDF, frozen under a name with its source commit in the gitignored
  `book/out/reviews/`. No repository, no sources, no other brief.
- Give only the reader, their goals in order, and the settled decisions so it doesn't
  spend the turn re-arguing them. Anything more makes the read less blind. For a
  targeted reread, add the earlier findings and the changed pages.
- To split a long book, give every reader the whole PDF and a page range, then read
  across the range boundaries yourself.
- It looks for order (an idea used before it is taught), coherence (contradictions, a
  case told twice, a running example that changes, a bolted-on section, a wrong page
  reference), pacing (sections too long or thin for what they teach, material in the
  wrong chapter), prose that slows the reader (padding, recaps, mannered phrasing, one
  concept under several names, text that sounds machine-written), teaching (trivia
  recall, exercises that miss the point, output that doesn't show the claim) and layout
  (diagrams unreadable at page size, squeezed table columns, headings stranded at a page
  bottom, blank or half-empty pages).
- It separates "must fix" from "taste", gives for each the PDF page, the quoted phrase,
  the problem and a concrete fix, and lists the pages it read closely, skimmed and
  didn't reach.
