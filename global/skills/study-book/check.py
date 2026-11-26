"""Mechanical checks of a typeset book; build.py runs them after every build.

Fails on missing answers, incorrect answer page numbers or link destinations, misplaced
section labels, horizontal text overflow in the body area, a prime printed after a
digit, and a stray ".:" after a word.
Reports without failing: counts, pages less than half full with the likely reason, and
pages that end well short of the bottom while their chapter continues. Read the report;
an "unexpected" short page usually means a block too tall to fit was pushed to the next.
"""

import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter

TOLERANCE = 1.0  # points
# Typst hangs punctuation and hyphens slightly into the margin on purpose.
HANGING = ",.;:-\xad–—)’”"
SECTION_LABEL = re.compile(r"<sec-[\w.:-]+>")
ANSWER_LINK = re.compile(r"\bAnswer [\w.-]+\.\d+, page \w+ →$")


def page_texts(pdf, poppler):
    out = subprocess.run(
        [poppler / "pdftotext", "-layout", str(pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.split("\f")[:-1]


def required_attribute(element: ET.Element, name: str) -> str:
    value = element.get(name)
    if value is None:
        raise ValueError(f"Poppler XML: <{element.tag}> is missing {name}")
    return value


def word_boxes(pdf, poppler):
    out = subprocess.run(
        [poppler / "pdftotext", "-bbox", str(pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    xml = re.sub(r"<!DOCTYPE[^>]*>", "", out.stdout)
    xml = re.sub(r'xmlns="[^"]*"', "", xml)
    pages = []
    for page in ET.fromstring(xml).iter("page"):
        pages.append(
            [
                (
                    float(required_attribute(w, "xMin")),
                    float(required_attribute(w, "yMin")),
                    float(required_attribute(w, "xMax")),
                    float(required_attribute(w, "yMax")),
                    w.text or "",
                )
                for w in page.iter("word")
            ]
        )
    return pages


def parse_answer_links(xml_text, html_name, answers, geometry=None):
    """Return question-pointer links and per-answer backlinks from pdftohtml XML."""
    links = Counter()
    row_backlinks = {}
    by_page = {}
    for a in answers:
        if a["page"] is not None:
            by_page.setdefault(a["page"], set()).add(a["n"])
    for page in ET.fromstring(xml_text).iter("page"):
        page_num = int(required_attribute(page, "number"))
        for anchor in page.iter("a"):
            printed = ANSWER_LINK.search(" ".join("".join(anchor.itertext()).split()))
            file, _, dest = anchor.get("href", "").rpartition("#")
            if printed and file == html_name and dest.isdecimal():
                links[page_num, printed.group(), int(dest)] += 1
        expected = by_page.get(page_num)
        if not expected:
            continue
        page_width = float(required_attribute(page, "width"))
        texts = []
        right_links = []
        for el in page.iter("text"):
            top = float(required_attribute(el, "top"))
            left = float(required_attribute(el, "left"))
            width = float(required_attribute(el, "width"))
            height = float(required_attribute(el, "height"))
            label = " ".join("".join(el.itertext()).split())
            texts.append((top, left, height, label))
            anchors = list(el.iter("a"))
            if len(anchors) == 1:
                anchor_text = " ".join("".join(anchors[0].itertext()).split())
                file, _, dest = anchors[0].get("href", "").rpartition("#")
                if anchor_text == label and file == html_name and dest.isdecimal():
                    right_links.append(
                        (top, height, left + width, anchor_text, int(dest))
                    )
        num_lefts = [left for _, left, _, label in texts if label in expected]
        if not num_lefts:
            continue
        col1_left = min(num_lefts)
        if geometry is not None:
            margin = geometry["outside"] if page_num % 2 == 1 else geometry["inside"]
            right_edge = page_width * (geometry["width"] - margin) / geometry["width"]
        else:
            right_edge = page_width - col1_left
        # Skip the odd-page running head ("Answers" at the right margin); only a column-1
        # Answers heading marks where the Answers section begins on a shared page.
        heading_tops = [
            top
            for top, left, _, label in texts
            if label == "Answers" and left <= col1_left + 2
        ]
        after_top = max(heading_tops) if heading_tops else -1
        for top, left, height, label in texts:
            if label not in expected or left > col1_left + 2 or top <= after_top:
                continue
            # Match only the backlink column flush with the right margin, never a link
            # inside the prompt column on the same row.
            matches = [
                (text, dest)
                for bl_top, bl_h, bl_right, text, dest in right_links
                if bl_top > after_top
                and abs(bl_right - right_edge) <= 6
                and bl_top < top + height
                and top < bl_top + bl_h
            ]
            if len(matches) == 1:
                row_backlinks[page_num, label] = matches[0]
    return links, row_backlinks


def answer_links(pdf, poppler, answers, geometry=None):
    out = subprocess.run(
        [poppler / "pdftohtml", "-q", "-xml", "-i", "-stdout", str(pdf)],
        capture_output=True,
        text=True,
        check=True,
    )
    return parse_answer_links(
        out.stdout, pdf.with_suffix(".html").name, answers, geometry
    )


def check_answers(questions, answers, texts, links, row_backlinks):
    problems = []
    expected_links = Counter()
    by_number = {a["n"]: a for a in answers}
    for q in questions:
        n = q["n"]
        a = by_number.get(n)
        if a is None:
            problems.append(f"question {n} has no answer")
            continue
        # An unconverged layout can leave an answer unplaced; report it instead of crashing.
        if a["page"] is None:
            problems.append(f"answer {n} never resolved to a page")
            continue
        # Compare against the printed text, not just the metadata, so a layout that did not
        # converge shows up.
        pointer = f"Answer {n}, page {a['folio']} →"
        if pointer not in texts[q["page"] - 1]:
            problems.append(
                f"question {n}: pointer on page {q['folio']} does not say page {a['folio']}"
            )
        expected_links[q["page"], pointer, a["page"]] += 1
        # The row's backlink-column link checks both the printed folio and destination.
        backlink = f"← page {q['folio']}"
        if row_backlinks.get((a["page"], n)) != (backlink, q["page"]):
            problems.append(
                f"answer {n}: back link on page {a['folio']} does not link to page {q['folio']}"
            )
    for n in set(by_number) - {q["n"] for q in questions}:
        problems.append(f"answer {n} has no question")
    for source, printed, dest in expected_links - links:
        problems.append(
            f'PDF page {source}: "{printed}" is missing a link to PDF page {dest}'
        )
    return problems


def check_section_labels(typst):
    # Let Typst decide which candidates are labels. The scan can also find examples
    # in code fences or comments, which the query will ignore.
    labels = sorted(
        {
            label
            for path in typst.book.parent.rglob("*.typ")
            for label in SECTION_LABEL.findall(path.read_text(encoding="utf-8"))
        }
    )
    if not labels:
        return []
    first, *rest = labels
    selector = f"selector({first})"
    if rest:
        selector += f".or({', '.join(rest)})"
    elements = typst.query(selector, field=None)
    problems = [
        f"{el['label']} labels {el['func']} instead of a heading"
        for el in elements
        if el["func"] != "heading"
    ]
    problems += [
        f"{label} is defined {count} times"
        for label, count in Counter(el["label"] for el in elements).items()
        if count > 1
    ]
    return problems


def overflow(boxes, geometry):
    found = []
    width, height = geometry["width"], geometry["height"]
    for index, words in enumerate(boxes):
        recto = (index + 1) % 2 == 1
        left = geometry["inside"] if recto else geometry["outside"]
        right = width - (geometry["outside"] if recto else geometry["inside"])
        for x0, y0, x1, y1, word in words:
            if y1 < geometry["top"] or y0 > height - geometry["bottom"]:
                continue  # running head or folio
            slack = 3.0 if word[-1:] in HANGING else TOLERANCE
            if x0 < left - TOLERANCE or x1 > right + slack:
                found.append(f'page {index + 1}: "{word}" at x {x0:.0f}..{x1:.0f}')
    return found


def stray_marks(texts):
    """Two slips that build cleanly and read as typos.

    Typst's smart quote turns ' after a digit into a prime ("chapter 8′s"); write ’ in
    prose instead. A period followed by a colon is what cutting a sentence before a
    listing leaves behind when the cut sentence ended in a colon.
    """
    found = []
    for index, text in enumerate(texts):
        # Only after a digit (a prime after a letter can be a derivative), and only a
        # word of two or more letters before ".:", so "e.g.:", "1.:" and "...:" pass.
        for match in re.finditer(r"\S*(?:\d\u2032|\b[A-Za-z]{2,}\.:(?=\s|$))\S*", text):
            found.append(f'page {index + 1}: stray mark in "{match.group()}"')
    return found


def page_fills(boxes, geometry):
    top, bottom = geometry["top"], geometry["height"] - geometry["bottom"]
    fills = []
    for words in boxes:
        body = [w for w in words if top <= w[1] <= bottom]
        fills.append((max(w[3] for w in body) - top) / (bottom - top) if body else 0.0)
    return fills


def run(pdf, typst):
    texts = page_texts(pdf, typst.poppler)
    boxes = word_boxes(pdf, typst.poppler)
    geometry = typst.query("<book-geometry>")[0]
    questions = typst.query("<question-mark>")
    answers = typst.query("<answer-mark>")
    probes = typst.query("<fit>")
    chapters = typst.query("<chapter-open>")
    part_pages = {p["page"] for p in typst.query("<part-open>")}
    answer_breaks = {p["page"] for p in typst.query("<answers-break>")}
    diagrams = typst.query("<diagram>")

    numbered = sum(1 for c in chapters if c["numbered"])
    cases = sum(1 for q in questions if q["case"])
    print(
        f"pages: {len(texts)}; chapters: {numbered} numbered, {len(chapters) - numbered} unnumbered; "
        f"diagrams: {len(diagrams)}; questions: {len(questions) - cases}; cases: {cases}"
    )

    links, row_backlinks = answer_links(pdf, typst.poppler, answers, geometry)
    problems = check_answers(questions, answers, texts, links, row_backlinks)
    print(f"answers checked: {len(answers)}")
    problems += check_section_labels(typst)
    outside = overflow(boxes, geometry)
    print(f"words outside the text block: {len(outside)}")
    for line in outside[:20]:
        print("  ", line)
    problems += outside
    problems += stray_marks(texts)

    # Short pages, with the reason each is expected.
    fills = page_fills(boxes, geometry)
    chapter_ends = {p["page"] for p in probes}
    # The title and contents end where they end; the contents may run to several pages.
    front = min(p["opener"] for p in probes) - 1
    print("pages less than half full:")
    short = 0
    for index, fill in enumerate(fills):
        page = index + 1
        if fill >= 0.5:
            continue
        short += 1
        if page <= front:
            reason = "title or contents"
        elif page in chapter_ends:
            reason = "a chapter's last page"
        elif page in part_pages:
            reason = "a part opener"
        elif page in answer_breaks:
            reason = "a tagged chapter's last page before its answers"
        else:
            reason = "unexpected"
        print(f"   page {page}: {fill:.0%} full, {reason}")
    if not short:
        print("   none")
    # texts is 0-based, so texts[page] is the page after `page`: the chapter continues there.
    holes = [
        page
        for page, fill in enumerate(fills, 1)
        if page > front
        and 0.5 <= fill < 0.88
        and page not in chapter_ends
        and page not in part_pages
        and page not in answer_breaks
        and page < len(fills)
        and texts[page].strip()
    ]
    print(f"pages ending under 88% full while the chapter continues: {holes or 'none'}")

    for problem in problems:
        print("PROBLEM:", problem)
    return 1 if problems else 0
