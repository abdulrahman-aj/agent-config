# Diagram brief

For a worker drawing SVG diagrams of real mechanisms. Start the brief with `common.md`.

How to fill it in:

- Name an approved diagram as the style model. For the book's first diagram, set the
  style from the template's fonts and colors and reuse it in every later brief.
- For each diagram, name the section it illustrates and the lab run or primary source
  that backs it. A diagram with no mechanism behind it shouldn't be drawn.

---

Draw these SVG diagrams. Edit only the SVG files named below.

## Style

Follow `<STYLE_MODEL.svg>`, or for the first diagram these values: `<FONTS, COLORS,
WIDTH, MAX_HEIGHT>`.

- Text uses `'Source Sans 3'`; code and SQL labels use `'JetBrains Mono'`. No other
  fonts.
- Every label sits inside its box with margin, and no text crosses a line.
- Draw only what the text and the lab show. No icons, no decoration, no title inside
  the SVG (the caption is separate).

## The diagrams

`<FOR EACH: file name; the section and label it illustrates; the lab command or source;
the events, values and order it must show>`

Read the section and run the lab before drawing. Every event, value and order in the
diagram must match the lab's real output or the cited source.

## Check your work

Render each SVG at twice its width and look at the image:

```
nix shell nixpkgs#librsvg -c rsvg-convert -w <2 x WIDTH> <file>.svg -o <SCRATCH_DIR>/<file>.png
```

Fix overlaps, clipped text and crossing lines. Don't end your turn until every file
exists and you have looked at each image.

## Report additions

For each diagram: what backs each event and value (a lab output line or a source line),
a one-sentence caption in sentence case, and anything in the text that disagreed with
the lab.
