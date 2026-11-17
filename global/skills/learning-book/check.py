"""Mechanical checks of a typeset book; build.py runs them after every build.

Fails on: a question whose answer is missing, a printed "Answer n, page P" pointer or
"<- page Q" back link that does not land where it says, and words outside the text block.
Reports without failing: counts, pages less than half full with the likely reason, and
pages that end well short of the bottom while their chapter continues. Read the report;
an "unexpected" short page usually means a block too tall to fit was pushed to the next.
"""

import re
import subprocess
import xml.etree.ElementTree as ET

TOLERANCE = 1.0  # points
# Typst hangs punctuation and hyphens slightly into the margin on purpose.
HANGING = ',.;:-\xad–—)’”'


def page_texts(pdf, poppler):
    out = subprocess.run([poppler / 'pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, check=True)
    return out.stdout.split('\f')[:-1]


def word_boxes(pdf, poppler):
    out = subprocess.run([poppler / 'pdftotext', '-bbox', str(pdf), '-'], capture_output=True, text=True, check=True)
    xml = re.sub(r'<!DOCTYPE[^>]*>', '', out.stdout)
    xml = re.sub(r'xmlns="[^"]*"', '', xml)
    pages = []
    for page in ET.fromstring(xml).iter('page'):
        pages.append([(float(w.get('xMin')), float(w.get('yMin')), float(w.get('xMax')), float(w.get('yMax')),
                       w.text or '') for w in page.iter('word')])
    return pages


def check_answers(questions, answers, texts):
    problems = []
    by_number = {a['n']: a for a in answers}
    for q in questions:
        n = q['n']
        a = by_number.get(n)
        if a is None:
            problems.append(f'question {n} has no answer')
            continue
        # Compare against the printed text, not just the metadata, so a layout that did not
        # converge shows up.
        if f'Answer {n}, page {a["folio"]}' not in texts[q['page'] - 1]:
            problems.append(f'question {n}: pointer on page {q["folio"]} does not say page {a["folio"]}')
        answer_page = texts[a['page'] - 1]
        if not re.search(rf'^\s*{re.escape(n)}\s.*← page {re.escape(q["folio"])}\s*$', answer_page, re.M):
            problems.append(f'answer {n}: back link on page {a["folio"]} does not say page {q["folio"]}')
    for n in set(by_number) - {q['n'] for q in questions}:
        problems.append(f'answer {n} has no question')
    return problems


def overflow(boxes, geometry):
    found = []
    width, height = geometry['width'], geometry['height']
    for index, words in enumerate(boxes):
        recto = (index + 1) % 2 == 1
        left = geometry['inside'] if recto else geometry['outside']
        right = width - (geometry['outside'] if recto else geometry['inside'])
        for x0, y0, x1, y1, word in words:
            if y1 < geometry['top'] or y0 > height - geometry['bottom']:
                continue  # running head or folio
            slack = 3.0 if word[-1:] in HANGING else TOLERANCE
            if x0 < left - TOLERANCE or x1 > right + slack:
                found.append(f'page {index + 1}: "{word}" at x {x0:.0f}..{x1:.0f}')
    return found


def page_fills(boxes, geometry):
    top, bottom = geometry['top'], geometry['height'] - geometry['bottom']
    fills = []
    for words in boxes:
        body = [w for w in words if top <= w[1] <= bottom]
        fills.append((max(w[3] for w in body) - top) / (bottom - top) if body else 0.0)
    return fills


def run(pdf, typst):
    texts = page_texts(pdf, typst.poppler)
    boxes = word_boxes(pdf, typst.poppler)
    geometry = typst.query('<book-geometry>')[0]
    questions = typst.query('<question-mark>')
    answers = typst.query('<answer-mark>')
    probes = typst.query('<fit>')
    chapters = typst.query('<chapter-open>')
    diagrams = typst.query('<diagram>')

    numbered = sum(1 for c in chapters if c['numbered'])
    cases = sum(1 for q in questions if q['case'])
    print(f'pages: {len(texts)}; chapters: {numbered} numbered, {len(chapters) - numbered} unnumbered; '
          f'diagrams: {len(diagrams)}; questions: {len(questions) - cases}; cases: {cases}')

    problems = check_answers(questions, answers, texts)
    print(f'answers checked: {len(answers)}')
    outside = overflow(boxes, geometry)
    print(f'words outside the text block: {len(outside)}')
    for line in outside[:20]:
        print('  ', line)
    problems += outside

    # Short pages, with the reason each is expected.
    fills = page_fills(boxes, geometry)
    chapter_ends = {p['page'] for p in probes}
    print('pages less than half full:')
    short = 0
    for index, fill in enumerate(fills):
        page = index + 1
        if fill >= 0.5:
            continue
        short += 1
        if page <= 2:
            reason = 'title or contents'
        elif page in chapter_ends:
            reason = "a chapter's last page"
        else:
            reason = 'unexpected'
        print(f'   page {page}: {fill:.0%} full, {reason}')
    if not short:
        print('   none')
    # texts is 0-based, so texts[page] is the page after `page`: the chapter continues there.
    holes = [page for page, fill in enumerate(fills, 1)
             if 0.5 <= fill < 0.88 and page not in chapter_ends and page < len(fills)
             and texts[page].strip()]
    print(f'pages ending under 88% full while the chapter continues: {holes or "none"}')

    for problem in problems:
        print('PROBLEM:', problem)
    return 1 if problems else 0
