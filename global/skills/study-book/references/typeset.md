# Typesetting and PDF checks

Load this reference when setting up `book.typ`, diagnosing layout, or packaging a
release build.

## Authoring against `template.typ`

- Write `book.typ` against this skill's `template.typ`; its header lists the interface
  and `sample/book.typ` uses all of it.
- Structure parts with `#part(title)[body]`, optional contents-only groups with
  `#group(title)`, and chapters with `#chapter(title)[body]`. PDF bookmarks nest part,
  chapter and section; the book opens with a brief contents before the full contents, and
  each part opener lists its chapters at the foot.
- Use `numbered: false, tag: "R1"` on unnumbered review or synthesis chapters so their
  questions number under the tag and their Answers start on a new page.
- Label chapters with `label: <ch-topic>` and sections with `== Heading <sec-topic>`.
  Reference them with `@ch-topic`, `#chapter-number(<ch-topic>)` or `@sec-topic` so
  links and chapter numbers survive reordering.
- Put web addresses in `#web("https://...")` footnotes so URLs render in mono,
  unhyphenated and breakable after each slash instead of breaking prose lines.
- Use `#crux[question]` sparingly, only for the points a chapter turns on, never as a
  labelled opener in every section.
- Keep SVG diagrams next to `book.typ` with quoted font names, using `'Source Sans 3'`,
  `'Source Serif 4'` and `'JetBrains Mono'`.
- The template is screen-first. For print, change the copy beside `build.py`, because
  the build overwrites the copy next to `book.typ`, and check binding margins.
- Use `auto` in tables only for short-label columns and `fr` for text, because an `auto`
  column sizes to its longest cell and squeezes the rest.

## Building and inspecting

```bash
python3 <this skill>/build.py path/to/book.typ   # writes path/to/book.pdf
```

- The build fetches Typst, fonts and Poppler from nixpkgs, reduces short chapter
  endings, and fails on broken answer pages, links, labels, horizontal overflow, primes
  printed for apostrophes after digits, and a stray `.:` left by a cut sentence. It
  can't see vertical overflow or inside diagrams.
- After changing `template.typ` or `check.py`, confirm that a deliberately broken link
  and a broken answer reference still fail.
- Render every page and inspect it at reading size, because a squeezed table passed a
  50 dpi contact sheet:

```bash
nix shell nixpkgs#poppler-utils -c pdftoppm -r 80 -png book.pdf out/page
```

## Checkpoints and reproducible builds

- Freeze each checkpoint PDF as `book/out/reviews/review-<commit>.pdf`, gitignored, and
  give the user a link.
- If others will build the book, copy `build.py`, `check.py` and `template.typ` into
  `tools/typeset/`, record the skill commit, commit a flake lock with root input
  `nixpkgs`, and test from a fresh clone:

```bash
# <flake-dir> holds flake.lock with locked root input nixpkgs (for example . or ./lab)
nix shell --inputs-from <flake-dir> nixpkgs#python3 -c python3 tools/typeset/build.py --inputs-from <flake-dir> book/book.typ
```
