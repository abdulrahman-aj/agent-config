# Diagram brief

For a worker drawing SVG diagrams of real mechanisms. Start the brief with `common.md`.

How to fill it in:

- Name an existing diagram as the style model. If there is none, settle the style once
  and keep these values for every later brief.
- For each diagram, name the section it illustrates and the lab command whose output it
  must match. A diagram with no mechanism behind it shouldn't be drawn.

---

Draw these SVG diagrams. Edit only the SVG files named below.

## Style

Copy `<STYLE_MODEL.svg>` exactly:

- `font-family="'Source Sans 3'"` on the root; code and SQL labels use
  `font-family="'JetBrains Mono'"`. No other fonts.
- Colors: `<BOX_STROKE, BOX_FILL, HEADING, LINE colors>`; one accent, `<ACCENT>`, for
  failures and crashes only.
- viewBox width `<TEXT_BLOCK_WIDTH>`; height as needed, at most `<MAX_HEIGHT>`. Font
  sizes 12 to 15. Every label sits inside its box with margin, and no text crosses a
  line.
- Draw only what the text and the lab show. No icons, no decoration, no title inside the
  SVG (the caption is separate).

## The diagrams

`<FOR EACH: file name; the section and label it illustrates; the lab command to run; the
events, values and order it must show>`

Read the section and run the lab before drawing. Every event, value and order in the
diagram must match the lab's real output.

## Check your work

Render each SVG at twice its width and look at the image:

```
rsvg-convert -w <2 x WIDTH> <file>.svg -o <SCRATCH_DIR>/<YOUR_NAME>/<file>.png
```

Fix overlaps, clipped text and crossing lines. Don't end your turn until every file exists
and you have looked at each image.

## Report additions

For each diagram: one line per element tying it to the lab output line or the source line
that backs it, a one-sentence caption in sentence case, and anything in the text that
disagreed with the lab.
