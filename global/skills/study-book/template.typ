// A modern technical book on a 160 x 212 mm screen-first page: serif body (Source Serif 4),
// sans structure (Source Sans 3), mono code (JetBrains Mono). build.py copies this file next
// to the book's book.typ on every build; edit it here, not the copy.
//
// Interface (everything else in this file is styling and may change):
//   #show: book.with(title:, subtitle:, reader:, snapshot:)     title page, brief and full contents
//   #part(title)[body]                                          part opener with its chapter list
//   #chapter(title, numbered: true, label: none,                opener on a new page; tag (e.g. "R1")
//     tag: none, tag-label: "Review")[body]                     replaces the number on an unnumbered
//                                                               chapter and breaks before Answers
//   @ch-topic, @sec-topic                                       reordering-safe chapter ("chapter N")
//                                                               or section ("“Title” (p. N)") link
//   #chapter-number(<ch-topic>)                                 linked chapter number alone
//   #takeaways[- list]                                          "After this chapter you can"
//   #exercise(title, where: "Laptop", disposable: false)[body]  read + try
//   #case(title, meta: none)[story][ask][verdict]               a real case the reader judges
//   #question[prompt][answer]                                   answer goes to the chapter end
//                                                               (numbered or tagged chapters)
//   #aside[body]                                                a side note
//   #crux[question]                                             optional decision question; use
//                                                               sparingly, only for the points a
//                                                               chapter turns on, never as a labelled
//                                                               opener in every section
//   #diagram(path, caption)                                     an SVG figure
//   #web("https://…", ...)                                      web addresses as one mono footnote
//   #glossary(([term], [definition], <heading-label>), ...)     link to a section or chapter
//   ```terminal  lines: "$ cmd" (command), ">> out" (highlighted output), else output
//   ```lang      ordinary code; long blocks split with three lines kept on each side

// Heading levels: parts are 1, chapters 2 and sections 3, so PDF bookmarks nest
// part > chapter > section. Inside a chapter `==` is a section: the chapter sets a
// heading offset, so chapter files never spell out these numbers.
#let chapter-level = 2
#let section-level = 3

// Parts are unnumbered and never step the heading counter, so its value at a chapter is
// (0, n) and the chapter count runs on across parts.
#let chapter-of(nums) = nums.at(chapter-level - 1, default: 0)
#let chapter-numbering(..nums) = str(chapter-of(nums.pos()))

// An unnumbered chapter may carry a tag, such as "R1" for a part's review, that stands
// where a number would: on the opener, in the contents, in the running head and in front
// of its question numbers. It doesn't step the heading counter.
#let chapter-tag = state("chapter-tag", none)
#let chapter-tag-label = state("chapter-tag-label", "Review")

// What goes where a chapter's number goes: its number, its tag, or none.
#let chapter-mark(h) = if h.numbering != none {
  str(chapter-of(counter(heading).at(h.location())))
} else { chapter-tag.at(h.location()) }

#let serif = "Source Serif 4"
#let sans = "Source Sans 3"
#let mono = "JetBrains Mono"

// A web address goes in a footnote, so the sentence names the resource and a reader of a
// printed copy finds the address at the page foot. Mono and unhyphenated, because a hyphen
// the typesetter adds is a typo once typed back in. Each slash is also a break point.
// Several addresses stack under the first, so each starts at the same column.
#let web(..urls) = {
  let items = urls.pos().map(u => {
    let shown = u.trim("https://", at: start).trim("www.", at: start).trim("/", at: end)
    link(u, text(font: mono, size: 7.6pt, hyphenate: false, shown.replace("/", "/\u{200B}")))
  })
  footnote(if items.len() == 1 { items.first() } else {
    box(baseline: 100% - 0.62em, stack(spacing: 0.55em, ..items))
  })
}

#let ink = rgb("#18212b")
#let soft = rgb("#586474")
#let faint = rgb("#8a95a3")
#let rule = rgb("#c9d1db")
#let blue = rgb("#1f57b0")
#let blue-tint = rgb("#f1f5fb")
#let ochre = rgb("#8d6200")
#let ochre-tint = rgb("#fbf6ea")
#let code-tint = rgb("#f2f4f7")

// Sized for reading on screen at fit-to-width: margins only need to clear the running head
// and folio, so the page wraps the text block closely and the type renders larger. The
// 134 mm measure keeps body lines near 80 characters; widen it and code starts wrapping.
// 13 mm still prints on loose sheets, but is too tight for a perfect-bound spine.
#let page-width = 160mm
#let page-height = 212mm
#let margins = (inside: 13mm, outside: 13mm, top: 14mm, bottom: 14mm)

// One vertical unit, a little under half a body line. Paragraph gaps are one unit beyond
// the leading; blocks (code, tables, boxes) sit two units away from text. Kept tight: the
// books are read as PDFs, and airy spacing reads as padding there.
#let unit = 5.5pt
#let leading = 0.62em
#let par-gap = leading + unit
#let block-gap = 2 * unit

#let caps(body, size: 7.6pt, fill: soft, weight: 600) = text(
  font: sans, size: size, weight: weight, tracking: 0.09em, fill: fill, upper(body))

// ---------------------------------------------------------------- page numbers

// Front matter is numbered i, ii, ...; the first numbered chapter restarts at 1.
#let main-start() = {
  let opens = query(<chapter-open>).filter(m => m.value.numbered)
  if opens.len() == 0 { none } else { opens.first().location().page() }
}

#let folio-at(loc) = {
  let n = counter(page).at(loc).first()
  let start = main-start()
  if start != none and loc.page() >= start { str(n) } else { numbering("i", n) }
}

// "?" until the label exists: answers are placed after the question that points at them, so
// the first layout pass cannot see them yet. check.py fails on any "?" that survives.
#let folio-of(lbl) = {
  let found = query(lbl)
  if found.len() == 0 { "?" } else { folio-at(found.first().location()) }
}

#let page-ref(lbl) = context folio-of(lbl)

// A row of the brief contents and of a part opener's chapter list. Every title starts on
// one line; the part label or chapter number hangs in the column to its left. A part row
// shows no page: its opener is always the page before its first chapter.
#let toc-row(mark, title, pg, above: 0.55 * unit) = block(above: above, below: 0.55 * unit,
  grid(columns: (15mm, 1fr, auto), column-gutter: (0pt, 6pt),
    align: (right + bottom, left + bottom, right + bottom),
    box(inset: (right: 4mm), mark),
    par(justify: false, text(font: sans, size: 9.8pt, fill: ink, {
      title
      if pg != none {
        box(width: 1fr, inset: (x: 4pt), repeat(gap: 3pt, text(fill: faint, size: 7pt, ".")))
      }
    })),
    text(font: sans, size: 9.8pt, fill: soft, pg)))

#let chapter-row(h) = {
  link(h.location(), toc-row(text(font: sans, size: 9.8pt, weight: 600, fill: blue,
    chapter-mark(h)),
    h.body, folio-at(h.location())))
}

// ---------------------------------------------------------------- page furniture

// Pages without a running head: chapter openers, and the title and contents pages.
#let is-opener(p) = query(<chapter-open>).any(m => m.location().page() == p)
#let is-quiet(p) = query(<quiet>).any(m => m.location().page() == p)

#let running-head = context {
  let p = here().page()
  if is-opener(p) or is-quiet(p) { return }
  let chapters = query(heading.where(level: chapter-level)).filter(h => h.location().page() <= p)
  if chapters.len() == 0 { return }
  let chapter = chapters.last()
  set text(font: sans, size: 7.8pt, fill: soft)
  let number = text(weight: 700, fill: ink, folio-at(here()))
  if calc.even(p) {
    let mark = chapter-mark(chapter)
    let label = if mark != none { text(weight: 700, fill: blue, mark) + h(0.6em) }
    number + h(1.4em) + label + chapter.body
  } else {
    let start = chapter.location().page()
    let sections = query(heading.where(level: section-level)).filter(h => {
      let q = h.location().page()
      q >= start and q <= p
    })
    let on-page = sections.filter(h => h.location().page() == p)
    let title = if on-page.len() > 0 { on-page.first().body } else if sections.len() > 0 {
      sections.last().body
    } else { chapter.body }
    align(right, title + h(1.4em) + number)
  }
}

#let running-foot = context {
  let p = here().page()
  if is-opener(p) {
    align(center, text(font: sans, size: 7.8pt, fill: soft, folio-at(here())))
  }
}

// ---------------------------------------------------------------- code

// The fill a code block uses depends on whether it sits inside a tinted exercise box.
#let in-box = state("in-box", false)
#let code-blocks = counter("code-block")

// How many spaces a line starts with, so a wrapped line can hang past its own indent.
// Spaces only: tabs would need their rendered width.
#let leading-spaces(line) = line.len() - line.trim(" ", at: start).len()

// A terminal transcript: the prompt in grey, the command in full ink, output in a lighter
// grey, ">> " lines in blue. A command ending in "\" continues on the next line.
#let terminal-rows(source) = {
  // A local show-set, because the book's `show raw` fill would override an outer text fill.
  let styled(fill, weight: 400, s) = { show raw: set text(fill: fill, weight: weight); raw(s) }
  let rows = ()
  let continued = false
  for line in source.split("\n") {
    if continued or line.starts-with("$ ") {
      let (prompt, cmd) = if continued { ("", line) } else { ("$ ", line.slice(2)) }
      rows.push((styled(faint, prompt) + styled(ink, weight: 600, cmd), true, 0))
      continued = line.ends-with("\\")
    } else if line.starts-with(">> ") {
      rows.push((styled(blue, weight: 600, line.slice(3)), false, 0))
    } else {
      rows.push((styled(rgb("#56616f"), line), false, leading-spaces(line)))
    }
  }
  rows
}

// Each source line is its own paragraph, so a wrapped line can hang four characters past
// the line's own indent; a fixed hang reads as a dedent under an indented line. Long
// blocks may break across pages but never leave fewer than three lines on either side
// or a command apart from its first output line, and the part on the new page carries
// a small "continued" mark. `rows` holds (line, keep-with-next, indent) triples, the
// indent counted in characters.
#let code-block(rows) = {
  let code-size = 7.5pt
  let long = rows.len() >= 7
  // Only long blocks can break, so only they get the mark. Each of their lines carries a
  // label, and a line whose page differs from the previous line's page gets the mark.
  // Labels rather than a state updated line by line: such a chain needed more layout
  // passes than Typst allows, and the document did not converge. A wrapped line never
  // breaks across pages: half a statement on each page can't be read or copied.
  if long { code-blocks.step() }
  context {
    let n = code-blocks.get().first()
    let tag(i) = label("code-" + str(n) + "-" + str(i))
    let mark(i) = context {
      let prev = query(tag(i - 1))
      if prev.len() > 0 and prev.first().location().page() != here().page() {
        // A paragraph cannot hold a placed element directly, but a zero-size box can.
        box(width: 0pt, height: 0pt, place(top + left, dy: -12.8pt,
          text(hyphenate: false, caps([continued], size: 5.6pt, fill: faint, weight: 600))))
      }
    }
    // JetBrains Mono advances 0.6 em per character.
    let line(i, (row, keep, indent)) = block(spacing: 0.56em, sticky: keep, breakable: false,
      par(hanging-indent: (indent + 4) * 0.6 * code-size, {
      if long {
        if i > 0 { mark(i) }
        [#metadata(none)#tag(i)]
      }
      if row == [] or row == none { raw("\u{200b}") } else { row }
    }))
    let lines = rows.enumerate().map(((i, row)) => line(i, row))
    block(width: 100%, above: block-gap, below: block-gap, breakable: long,
      fill: if in-box.get() { none } else { code-tint },
      inset: (x: 8pt, y: 8pt), stroke: (left: 1.6pt + rule), {
        set par(justify: false, leading: 0.56em, spacing: 0.56em,
          linebreaks: "simple", first-line-indent: 0pt)
        set text(hyphenate: false)
        show raw: set text(size: code-size)
        if long {
          block(breakable: false, spacing: 0.56em, lines.slice(0, 3).join())
          lines.slice(3, -3).join()
          block(breakable: false, spacing: 0.56em, lines.slice(-3).join())
        } else {
          lines.join()
        }
      })
  }
}

// ---------------------------------------------------------------- document

#let book(title: "", subtitle: none, reader: none, snapshot: none, body) = {
  // No date, so rebuilding unchanged content gives a byte-identical PDF.
  set document(title: title, date: none)
  set page(width: page-width, height: page-height, margin: margins,
    header: running-head, footer: running-foot, header-ascent: 45%, footer-descent: 40%)
  set text(font: serif, size: 10pt, lang: "en", region: "us", hyphenate: true, fill: ink,
    costs: (hyphenation: 80%, runt: 120%, widow: 200%, orphan: 200%))
  set par(justify: true, leading: leading, spacing: par-gap, first-line-indent: 0pt,
    linebreaks: "optimized")
  show strong: set text(weight: 600)
  show raw: set text(font: mono, size: 8.6pt, fill: rgb("#24303d"), features: (calt: 0))
  set list(marker: text(fill: blue, sym.bullet), indent: 0.3em, body-indent: 0.55em,
    spacing: leading + 0.4 * unit)
  set enum(indent: 0.1em, body-indent: 0.55em, spacing: leading + 0.4 * unit,
    numbering: n => text(font: sans, weight: 600, fill: blue, str(n) + "."))
  set block(spacing: block-gap)

  // Chapter references (`@ch-x`) render as "chapter N"; unnumbered chapters and sections
  // (`@sec-x`) render as their title and page, so links survive reordering.
  show ref: it => {
    let el = it.element
    if el != none and el.func() == heading and el.level == chapter-level and el.numbering != none and it.supplement == auto {
      link(el.location(), [chapter~#chapter-of(counter(heading).at(el.location()))])
    } else if el != none and el.func() == heading and (el.level > chapter-level or el.numbering == none) and it.supplement == auto {
      link(el.location(), [“#el.body” (p.~#folio-at(el.location()))])
    } else {
      it
    }
  }

  show raw.where(block: true): it => code-block(
    if it.lang == "terminal" { terminal-rows(it.text) } else { it.lines.map(l => (l.body, false, leading-spaces(l.text))) })

  show heading: set text(font: sans, fill: ink, hyphenate: false)
  show heading: set par(justify: false)
  show heading.where(level: section-level): it => block(above: if it.supplement == [Case] { 0.6 * unit } else { 3.4 * unit },
    below: 1.3 * unit, sticky: true,
    text(size: 12.5pt, weight: if it.supplement == [Case] { 700 } else { 600 }, it.body))
  show heading.where(level: 1): it => block(width: 100%, above: 0pt, below: 6 * unit, {
    v(48mm)
    block(below: 12pt, caps([Part #context counter("part").display()], size: 9pt))
    block(above: 0pt, below: 0pt, par(leading: 0.3em,
      text(size: 30pt, weight: 600, tracking: -0.015em, fill: blue, it.body)))
    v(14pt)
    line(length: 30mm, stroke: 2pt + blue)
  })
  show heading.where(level: chapter-level): it => block(width: 100%, above: 0pt, below: 4 * unit, {
    v(22mm)
    context {
      let mark = chapter-mark(it)
      if mark != none {
        let kicker = if it.numbering != none [Chapter] else { chapter-tag-label.at(it.location()) }
        if kicker != none { block(below: 10pt, caps(kicker, size: 8pt)) }
        block(below: 14pt, text(font: sans, size: 60pt, weight: 300, fill: blue,
          top-edge: "cap-height", bottom-edge: "baseline", mark))
      } else {
        v(26pt)
      }
    }
    block(above: 0pt, below: 0pt, par(leading: 0.3em,
      text(size: 23pt, weight: 600, tracking: -0.01em, it.body)))
    v(12pt)
    line(length: 100%, stroke: 1pt + ink)
  })

  // Tables: rules instead of a grid, no hyphenation in cells. Tables of five rows or fewer
  // stay whole; longer ones may break between rows, never inside one, so they should mark
  // their first row with table.header so it repeats. Keeping long tables whole left
  // half-empty pages behind them.
  set table(inset: (x: 5pt, y: 4.6pt), align: left + top, stroke: (x, y) => (
    top: if y == 0 { 0.9pt + ink } else if y == 1 { 0.6pt + ink } else { 0.35pt + rule }))
  show table.cell.where(y: 0): set text(font: sans, weight: 700, size: 8.6pt)
  set table.cell(breakable: false)  // a row moves to the next page whole
  show table: it => {
    let cols = if type(it.columns) == array { it.columns.len() } else { it.columns }
    set text(size: 8.8pt, hyphenate: false)
    set par(justify: false, leading: 0.5em)
    show raw: set text(size: 7.8pt)
    block(above: block-gap, below: block-gap, breakable: it.children.len() > 5 * cols,
      stroke: (bottom: 0.9pt + ink), it)
  }

  show figure.caption: it => block(width: 100%, above: 7pt,
    align(left, text(font: sans, size: 8.4pt, fill: soft, it.body)))
  set figure(gap: 7pt)

  // Contents: chapters with their number or tag, sections indented with dot leaders, cases marked.
  show outline.entry: it => {
    let entry = it.element
    let pg = folio-at(entry.location())
    if entry.supplement == [Part] {
      let n = counter("part").at(entry.location()).first()
      block(above: 3.2 * unit, below: 0.6 * unit, sticky: true, link(entry.location(),
        block(width: 100%, inset: (bottom: 4pt), stroke: (bottom: 0.6pt + blue),
          grid(columns: (1fr, auto), column-gutter: 6pt,
            text(font: sans, size: 11.5pt, weight: 700, fill: blue, [Part #n#h(0.6em)#entry.body]),
            text(font: sans, size: 10.5pt, weight: 600, pg)))))
    } else if entry.level == chapter-level {
      block(above: 1.9 * unit, below: 0.9 * unit, sticky: true, link(entry.location(),
        grid(columns: (9mm, 1fr, auto), column-gutter: (0pt, 6pt),
          text(font: sans, size: 10.5pt, weight: 700, fill: blue, chapter-mark(entry)),
          text(font: sans, size: 10.5pt, weight: 600, entry.body),
          text(font: sans, size: 10.5pt, weight: 600, pg))))
    } else {
      block(above: 0.75 * unit, below: 0.75 * unit, link(entry.location(),
        grid(columns: (9mm, 1fr, auto), column-gutter: (0pt, 6pt), [],
          par(justify: false, hanging-indent: 1em, text(size: 9.4pt, {
            if entry.supplement == [Case] { caps([Case], size: 6.8pt) + h(0.5em) }
            entry.body
            box(width: 1fr, inset: (x: 4pt), repeat(gap: 3pt, text(fill: faint, size: 7pt, ".")))
          })),
          text(font: sans, size: 9.4pt, fill: soft, pg))))
    }
  }

  // Page geometry in points, for check.py.
  [#metadata((width: page-width.pt(), height: page-height.pt(), top: margins.top.pt(),
    bottom: margins.bottom.pt(), inside: margins.inside.pt(), outside: margins.outside.pt()))
    <book-geometry>]

  // Title page.
  [#metadata(none) <quiet>]
  v(42mm)
  line(length: 22mm, stroke: 3pt + blue)
  v(8mm)
  par(justify: false, leading: 0.4em,
    text(font: sans, size: 36pt, weight: 700, tracking: -0.015em, hyphenate: false, title))
  if subtitle != none {
    v(6mm)
    block(width: 82%, par(justify: false, leading: 0.5em,
      text(font: sans, size: 13.5pt, fill: soft, subtitle)))
  }
  if reader != none {
    v(10mm)
    block(width: 82%, par(justify: false, text(font: sans, size: 10.5pt, weight: 600, reader)))
  }
  v(1fr)
  if snapshot != none {
    line(length: 100%, stroke: 0.5pt + rule)
    v(8pt)
    block(width: 85%, par(justify: false, leading: 0.55em,
      text(font: sans, size: 8.2pt, fill: soft, snapshot)))
  }

  // Brief contents, then the full contents. No right-hand openers: the books are read on
  // screen, where the blank pages they force are just gaps.
  pagebreak()
  [#metadata(none) <quiet>]
  heading(level: chapter-level, numbering: none, outlined: false, bookmarked: true)[Brief contents]
  {
    // One page with the book's shape: parts and chapters, no sections.
    show outline.entry: it => {
      let entry = it.element
      if entry.supplement == [Part] {
        let n = counter("part").at(entry.location()).first()
        link(entry.location(), toc-row(above: 2.6 * unit,
          caps([Part #n], size: 7.4pt, weight: 700, fill: blue),
          text(weight: 600, entry.body), none))
      } else { chapter-row(entry) }
    }
    outline(title: none, depth: chapter-level, target: heading)
  }
  pagebreak()
  [#metadata(none) <quiet>]
  heading(level: chapter-level, numbering: none, outlined: false, bookmarked: true)[Contents]
  outline(title: none, depth: section-level, target: heading)

  body
}

// ---------------------------------------------------------------- parts

// A part opens on its own quiet page: "Part N", its title, then an optional body such as
// a sentence on what the part holds, with its chapters listed at the foot. It is a level-1
// heading with the supplement [Part], so it nests chapters beneath it in PDF bookmarks
// while the running head and chapter numbering skip it.
#let part(title, body) = {
  pagebreak(weak: true)
  counter("part").step()
  [#metadata(none) <quiet>]
  context [#metadata((page: here().page())) <part-open>]
  heading(level: 1, numbering: none, supplement: [Part], title)
  // A standfirst in the opener's sans, like the title page's subtitle: set as body text it
  // read as a stray paragraph under the display title.
  block(width: 78%, {
    set text(font: sans, size: 13pt, fill: soft, hyphenate: false)
    set par(justify: false, leading: 0.55em)
    body
  })
  // The part's chapters at the foot of the opener, for a reader who lands here from a
  // bookmark or a link.
  v(1fr)
  context {
    let next-part = query(heading.where(level: 1).after(here()))
    let end = if next-part.len() > 0 { next-part.first().location().page() } else { none }
    let chapters = query(heading.where(level: chapter-level).after(here()))
      .filter(h => end == none or h.location().page() < end)
    if chapters.len() > 0 {
      line(length: 100%, stroke: 0.5pt + rule)
      for h in chapters { chapter-row(h) }
    }
  }
}

// ---------------------------------------------------------------- chapters

// build.py passes per-chapter spacing levels as JSON in sys.inputs.fit, keyed by the
// chapter's position (1-based, all chapters). Negative tightens and positive loosens
// paragraph and block gaps by a point or so: enough to pull a few stray lines back from a
// chapter's last page, or to push a near-empty last page past a third full.
#let fit-levels = json(bytes(sys.inputs.at("fit", default: "{}")))
#let chapter-index = counter("chapter-index")
#let fit-level = state("fit-level", 0)

#let chapter-number(target) = ref(target, supplement: none)

#let answers = state("answers", ())
#let question-count = counter("question")

#let chapter(title, numbered: true, label: none, tag: none, tag-label: "Review", body) = {
  assert(tag == none or not numbered, message: "a tag replaces the number: use numbered: false")
  pagebreak(weak: true)
  chapter-tag.update(tag)
  chapter-tag-label.update(tag-label)
  chapter-index.step()
  question-count.update(0)
  answers.update(())
  // The first numbered chapter starts the arabic page numbers at 1.
  context if numbered and chapter-of(counter(heading).get()) == 0 { counter(page).update(1) }
  // No page in the value: every folio and running head queries this marker, so a value that
  // moves with the layout costs a pass each time and can keep the book from converging.
  [#metadata((numbered: numbered)) <chapter-open>]
  let h = heading(level: chapter-level, numbering: if numbered { chapter-numbering } else { none },
    title)
  if label != none [#h#label] else { h }

  set heading(offset: chapter-level - 1)
  context {
    let idx = chapter-index.get().first()
    let level = fit-levels.at(str(idx), default: 0)
    fit-level.update(level)
    set par(leading: leading + level * 0.12pt, spacing: par-gap + level * 0.8pt)
    set list(spacing: leading + 0.4 * unit + level * 0.5pt)
    set enum(spacing: leading + 0.4 * unit + level * 0.5pt)
    body

    // Answers at the chapter end, so the reader commits to an answer first.
    context {
      let items = answers.get()
      if items.len() > 0 {
        // A tagged chapter (such as a review) is often short, so its answer would land
        // under its question; a new page keeps the reader from seeing it early.
        if tag != none {
          context [#metadata((page: here().page())) <answers-break>]
          pagebreak(weak: true)
        }
        block(above: 6 * unit, below: 0pt, sticky: true, line(length: 100%, stroke: 1.4pt + ink))
        heading(level: section-level, outlined: false, bookmarked: true)[Answers]
        for a in items {
          block(above: 2.2 * unit, below: 0pt, {
            // Locate the answer by its label: here() would resolve to the enclosing
            // context, i.e. where the Answers section starts, not where this answer is.
            // query, not locate: the label doesn't exist yet on the first layout pass.
            let found = query(std.label("ans-" + a.n))
            let loc = if found.len() > 0 { found.first().location() }
            [#metadata((n: a.n, page: if loc != none { loc.page() },
              folio: if loc != none { folio-at(loc) } else { "?" })) <answer-mark>]
            [#metadata(none)#std.label("ans-" + a.n)]
            set text(size: 9.3pt + level * 0.1pt)
            show raw: set text(size: 8pt)
            block(below: 0.8 * unit, sticky: true, grid(columns: (9mm, 1fr, auto),
              column-gutter: (0pt, 8pt),
              text(font: sans, size: 9.3pt, weight: 700, fill: blue, a.n),
              if a.case { text(font: sans, weight: 700, a.prompt) } else { emph(a.prompt) },
              link(std.label("q-" + a.n), text(font: sans, size: 7.6pt, weight: 600, fill: blue,
                [#sym.arrow.l page #page-ref(std.label("q-" + a.n))]))))
            pad(left: 9mm, a.answer)
          })
        }
      }
    }

    // Where the chapter ends, as a fraction of its last page's text height.
    context {
      let pos = here().position()
      let fill = (pos.y - margins.top) / (page-height - margins.top - margins.bottom)
      let opener = query(heading.where(level: chapter-level).before(here())).last().location().page()
      [#metadata((chapter: idx, page: pos.page, opener: opener, fill: fill)) <fit>]
    }
  }
}

#let takeaways(body) = block(width: 100%, above: 0pt, below: 4 * unit, breakable: false,
  inset: (bottom: 10pt), stroke: (bottom: 0.6pt + ink), {
    caps([After this chapter you can], fill: ink, weight: 700)
    v(0.6 * unit)
    set text(size: 9.6pt)
    set par(justify: false)
    set list(marker: text(fill: blue, [–]), spacing: leading + 0.3 * unit)
    body
  })

// ---------------------------------------------------------------- exercises and asides

// `where` names the machine the reader runs this on. A disposable environment (a VM, a
// scratch container) gets an ochre, dashed treatment so it never reads as "run this on
// your own machine".
#let exercise(title, where: "Laptop", disposable: false, body) = {
  let color = if disposable { ochre } else { blue }
  let edge = if disposable { (paint: color, thickness: 0.8pt, dash: (3pt, 2pt)) } else { 0.8pt + color }
  in-box.update(true)
  // Unbreakable: a reader works an exercise as one set of instructions, and a box split
  // mid-sentence across a page turn hides half of them. Keep each exercise under a page.
  block(width: 100%, above: 2.4 * unit, below: 2.4 * unit, breakable: false,
    fill: if disposable { ochre-tint } else { blue-tint },
    inset: (x: 10pt, top: 9pt, bottom: 11pt), stroke: (top: edge, bottom: edge), {
      block(below: unit, sticky: true, {
        caps(where, size: 7.4pt, weight: 700, fill: color)
        h(0.7em)
        text(font: sans, size: 10.5pt, weight: 700, title)
      })
      body
    })
  in-box.update(false)
}

#let aside(body) = block(width: 100%, above: 2 * unit, below: 2 * unit,
  fill: blue-tint, inset: (x: 10pt, y: 8pt), stroke: (left: 1.6pt + blue), {
    set text(size: 9.4pt)
    body
  })

// The question a section builds its answer to, set before the material so the reader reads
// for the answer. Use sparingly, only for the points a chapter turns on, never as a
// labelled opener in every section. Unbreakable and sticky, so it never strands at a foot.
#let crux(body) = block(width: 100%, above: 2.2 * unit, below: 2.2 * unit, breakable: false,
  sticky: true, inset: (x: 10pt, y: 8pt), stroke: (top: 0.8pt + ink, bottom: 0.8pt + ink), {
    caps([The crux], size: 7.4pt, weight: 700, fill: ink)
    v(0.5 * unit)
    set par(justify: false)
    text(font: sans, size: 10.2pt, weight: 600, body)
  })

#let diagram(path, caption) = [#metadata(path) <diagram>] + figure(
  block(width: 100%, inset: (y: 4pt), image(path, width: 100%)),
  caption: caption, placement: auto, numbering: none, supplement: none, kind: "diagram")

// ---------------------------------------------------------------- questions and cases

// Registers an answer for the chapter end and numbers it, e.g. "2.3" or "R1.1". Questions
// belong in numbered or tagged chapters: the number uses the chapter's mark, so untagged
// unnumbered ones would collide.
#let register(prompt, answer, case: false, body) = context {
  let tag = chapter-tag.get()
  let mark = if tag != none { tag } else { str(chapter-of(counter(heading).get())) }
  // This context reads the counter before the step below takes effect, hence the + 1.
  let n = mark + "." + str(question-count.get().first() + 1)
  question-count.step()
  answers.update(list => list + ((n: n, prompt: prompt, answer: answer, case: case),))
  [#metadata((n: n, case: case, page: here().page(), folio: folio-at(here()),
    pointer: folio-of(label("ans-" + n))))
    <question-mark>]
  [#metadata(none)#label("q-" + n)]
  body(n, link(label("ans-" + n), text(font: sans, size: 8.2pt, weight: 600, fill: blue,
    [Answer #n, page #page-ref(label("ans-" + n)) #sym.arrow.r])))
}

#let question(prompt, answer) = register(prompt, answer, (n, pointer) => block(
  above: 1.6 * unit, below: 1.6 * unit, breakable: false, grid(columns: (9mm, 1fr),
    text(font: sans, size: 9.6pt, weight: 700, fill: blue, n),
    { prompt; block(above: 0.7 * unit, pointer) })))

// A real case: what happened, then a question the reader answers before turning to the
// verdict at the chapter end.
#let case(title, meta: none, body, ask, verdict) = {
  block(above: 4 * unit, below: 0pt, sticky: true, line(length: 100%, stroke: 1.4pt + ink))
  if meta != none {
    block(above: 0.8 * unit, below: 0pt, sticky: true, caps(meta, size: 7.4pt))
  }
  heading(level: section-level, supplement: [Case], title)
  body
  register(ask, verdict, case: true, (n, pointer) => block(above: 2 * unit, below: 2 * unit,
    breakable: false, stroke: (left: 1.6pt + ink), inset: (left: 9pt, y: 3pt), {
      text(font: sans, size: 10pt, weight: 700, ask)
      h(0.8em)
      pointer
    }))
  block(above: 2 * unit, below: 3 * unit, line(length: 100%, stroke: 0.5pt + ink))
}

// ---------------------------------------------------------------- glossary

// Each term links to the heading that introduces it. Show the chapter number for
// numbered headings and the folio for unnumbered headings.
// Its row gap follows the chapter's fit level, since the paragraph gaps the level adjusts
// barely occur here.
#let glossary(..entries) = block(above: 2 * unit, context {
  set text(size: 9.2pt)
  set par(justify: false, leading: 0.55em)
  show raw: set text(size: 8pt)
  grid(columns: (30mm, 1fr, 7mm), column-gutter: 9pt,
    row-gutter: 1.5 * unit + fit-level.get() * 0.6pt,
    ..entries.pos().map(((term, definition, ch)) => (
      text(font: sans, weight: 700, size: 9.4pt, term),
      definition,
      align(right, link(ch, text(font: sans, size: 8.4pt, weight: 600, fill: blue,
        context if query(ch).first().numbering == none { "p." + folio-of(ch) }
          else { str(chapter-of(counter(heading).at(locate(ch)))) }))),
    )).flatten())
})
