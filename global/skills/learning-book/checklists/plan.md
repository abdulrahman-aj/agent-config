# Planning checklist

Work through this with the chapter list, before any drafting. Each item added after
drafting costs a pass over every chapter.

## When the plan changes

Update the plan file first, then the title page, front matter, exercises and capstone
wherever the old promise appears.

## Coverage

- The reader's background decides the examples and how much each idea needs
  explaining. It never decides coverage: a topic inside the agreed scope stays, even if
  the reader half knows it, when they need it for the work the book prepares them for.
  Cut repetition and padding, not needed topics.
- If the book promises to replace or cover a source, list the source's ideas section by
  section and record where the book teaches each one, with its reasoning and limits.
  Mark each covered, thin, or out of scope. Repeat the audit after a restructure.
- If the book promises lessons that transfer across stacks, state each principle before
  its lab implementation, and show a second stack where it behaves differently.
- Admit a new tool or topic only when you can name the reader's decision it teaches and
  what the existing material cannot show. Check any claim about maturity or adoption.
- List useful topics that lose on scope in a "what this book leaves out" page, each
  with why it matters and one checked source.

- Name what this book teaches that existing material on the topic doesn't, and check
  that each chapter delivers part of it. An outline that would fit an older book on
  the same topic has missed the point.

## Structure

Scale the structure to the book's length. A short book read straight through needs no
parts, reading paths or lookup pages.

- Decide the parts, the reading paths for different goals, and the lookup pages (a
  symptom index, a catalogue), each with its own heading and contents entry.
- Walk each reading path and check that it supplies the prerequisites it skips.
- Decide which mechanisms get a diagram. Only real mechanisms do.
- If the book rates or classifies things, write the rule that decides each verdict
  before the first entry, then check every entry against it.
- Label every navigation element: a table gets a title, and a link's text names where
  it goes. An unlabeled link reads as part of whatever sits next to it.
- Give every heading you will link to a label from the start.

## The lab and the book

- The book gives setup once, then shows the plain command the reader runs and the
  output that settles each point.
- The lab carries run modes, variants and detail. Each lab's docstring gives its
  command, variants and book section, and `lab/README` holds shared setup. Add a
  markdown file per lab only for depth the book lacks.
- Name lab folders by topic (`ch05-lazy-load`, not `ch05`).

## The sample chapter

Agree the outline with the user first. Then build one representative chapter end to
end using the skill's lab, trust and typesetting rules: prose, a runnable exercise with
its answer, a fact-check and a rendered PDF. Review it with the user, fix what the
other chapters would inherit, and make it the writers' model chapter.
