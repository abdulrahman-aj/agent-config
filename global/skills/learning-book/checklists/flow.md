# Flow checklist

Flow breaks most where parallel workers and fix rounds edit one section without reading
its neighbors. Check it at two costs:

- **After every batch of changes:** once every worker in the batch has finished, build
  the assembled book, then read each changed section with the sections around it.
- **After drafting a part, and before each whole-book blind read:** read the whole book
  in order. First list the key terms with the section that teaches each, and search
  earlier pages for uses.

What to check:

- Each chapter picks up what the previous one taught, and its sections serve the goals
  it opens with. A reader can do each stated goal from the chapter's text: if a goal
  needs a config file or a setup step, the chapter shows it.
- A running example keeps its names and schema unless the text announces the change.
- An exercise comes after the rules it needs.
- A case is told in one place.
- No passage relies on an idea taught later. A pointer forward is fine when the reader
  can keep going without following it.
- The same idea isn't explained twice, and one concept keeps one name.
- A section added later doesn't read as bolted on: it has a transition and sits where
  the argument needs it.
- Every passage frames its subject the way the plan's scope statement does. Search for
  the narrower framings that drift in, such as "the service" in a book about a whole
  application, and judge each one against the plan.
