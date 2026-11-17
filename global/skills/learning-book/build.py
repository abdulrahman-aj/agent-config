"""Typeset a book written against template.typ, then check the PDF.

    python3 build.py path/to/book.typ [--out book.pdf]

Typst, the three font families and poppler come from nixpkgs, and system fonts are
ignored, so a rebuild on another machine gives the same pages. The skill's template.typ is
copied next to book.typ first (Typst only imports files under the book's directory).

After the first compile, a chapter whose text ends in the top 30% of its last page gets
its spacing tightened, or failing that loosened, one small step at a time (see
`fit-levels` in template.typ), and the book is compiled again. Exits non-zero if a check
in check.py fails.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import check

SKILL = Path(__file__).resolve().parent
RUNT = 0.30
# Levels tried in order for a chapter that ends in a runt.
LEVELS = [0, -1, -2, -3, 1, 2, 3, 4]


def store_paths(*attrs):
    out = subprocess.run(['nix', 'build', '--no-link', '--print-out-paths', *(f'nixpkgs#{a}' for a in attrs)],
                         capture_output=True, text=True, check=True)
    return out.stdout.split()


class Typst:
    def __init__(self, book):
        typst, poppler, *fonts = store_paths('typst', 'poppler-utils', 'source-serif', 'source-sans',
                                             'jetbrains-mono')
        self.poppler = Path(poppler) / 'bin'
        self.base = [f'{typst}/bin/typst']
        self.flags = ['--ignore-system-fonts', '--root', str(book.parent)]
        for path in fonts:
            self.flags += ['--font-path', f'{path}/share/fonts']
        self.book = str(book)
        self.fit = {}

    def compile(self, pdf, fit):
        # Queries must see the same spacing levels as the last compile, or their pages differ.
        self.fit = dict(fit)
        subprocess.run(self.base + ['compile', *self.flags, *self.inputs(), self.book, str(pdf)], check=True)

    def query(self, selector):
        out = subprocess.run(self.base + ['query', *self.flags, *self.inputs(), self.book, selector, '--field', 'value'],
                             capture_output=True, text=True, check=True)
        return json.loads(out.stdout)

    def inputs(self):
        return ['--input', f'fit={json.dumps(self.fit)}']


def fit_chapters(typst, pdf):
    """Compile until no chapter ends in a runt, or every level has been tried."""
    fit, tried = {}, {}
    for _ in range(len(LEVELS) + 1):
        typst.compile(pdf, fit)
        changed = False
        for probe in typst.query('<fit>'):
            chapter, fill = str(probe['chapter']), probe['fill']
            history = tried.setdefault(chapter, {})
            history[fit.get(chapter, 0)] = fill
            # A chapter that fits on its opener page has no runt to fix.
            if fill >= RUNT or probe['page'] == probe['opener']:
                continue
            remaining = [level for level in LEVELS if level not in history]
            if remaining:
                fit[chapter] = remaining[0]
                changed = True
            else:
                # Nothing cleared the bar: keep the level that filled the last page most.
                fit[chapter] = max(history, key=history.get)
        if not changed:
            break
    typst.compile(pdf, fit)
    return {k: v for k, v in fit.items() if v}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('book', type=Path)
    parser.add_argument('--out', type=Path, help='default: book.typ with a .pdf suffix')
    args = parser.parse_args()
    book = args.book.resolve()
    pdf = (args.out or book.with_suffix('.pdf')).resolve()

    shutil.copyfile(SKILL / 'template.typ', book.parent / 'template.typ')
    typst = Typst(book)
    try:
        adjusted = fit_chapters(typst, pdf)
    except subprocess.CalledProcessError:
        sys.exit('typst failed; its error is above')
    print(f'wrote {pdf}; spacing adjusted (chapter: level): {adjusted or "none"}')
    sys.exit(check.run(pdf, typst))


if __name__ == '__main__':
    main()
