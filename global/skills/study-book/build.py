"""Typeset a book written against template.typ, then check the PDF.

    python3 build.py path/to/book.typ [--out book.pdf]

Typst, the three font families and poppler come from nixpkgs. Pin nixpkgs with
--inputs-from to keep the tool and font versions fixed. The skill's template.typ is
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


def validate_pin(flake):
    lock = flake / "flake.lock"
    committed = subprocess.run(
        ["git", "-C", str(flake), "show", "HEAD:./flake.lock"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if (
        committed.returncode
        or not lock.is_file()
        or lock.read_bytes() != committed.stdout
    ):
        sys.exit(f"--inputs-from {flake}: flake.lock must match the committed lock")

    out = subprocess.run(
        ["nix", "flake", "metadata", "--json", "--no-update-lock-file", str(flake)],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    locks = json.loads(out.stdout)["locks"]
    nodes = locks["nodes"]
    root = nodes[locks["root"]]

    def input_node(node, name):
        target = node.get("inputs", {}).get(name)
        if isinstance(target, list):  # A follows path starts at the root.
            node = root
            for step in target:
                node = input_node(node, step)
            return node
        return nodes.get(target, {})

    if "locked" not in input_node(root, "nixpkgs"):
        sys.exit(
            f"--inputs-from {flake}: flake.lock must have a locked root input named nixpkgs"
        )


def store_paths(inputs_from, *attrs):
    pin = ["--inputs-from", str(inputs_from)] if inputs_from else []
    out = subprocess.run(
        [
            "nix",
            "build",
            "--no-link",
            "--print-out-paths",
            *pin,
            *(f"nixpkgs#{a}" for a in attrs),
        ],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    return out.stdout.split()


class Typst:
    def __init__(self, book, inputs_from):
        typst, poppler, *fonts = store_paths(
            inputs_from,
            "typst",
            "poppler-utils",
            "source-serif",
            "source-sans",
            "jetbrains-mono",
        )
        self.poppler = Path(poppler) / "bin"
        self.base = [f"{typst}/bin/typst"]
        self.flags = ["--ignore-system-fonts", "--root", str(book.parent)]
        for path in fonts:
            self.flags += ["--font-path", f"{path}/share/fonts"]
        self.book = book
        self.fit = {}

    def compile(self, pdf, fit, final=False):
        # Queries must see the same spacing levels as the last compile, or their pages differ.
        self.fit = dict(fit)
        out = subprocess.run(
            self.base + ["compile", *self.flags, *self.inputs(), self.book, str(pdf)],
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        # A trial spacing level can leave the layout oscillating between two page breaks,
        # and Typst warns that it did not converge. That trial is discarded or recompiled,
        # so only the final compile's warnings matter, and there non-convergence is an error:
        # the PDF's page numbers could disagree with its own references.
        if out.returncode != 0 or final:
            sys.stderr.write(out.stderr)
        if out.returncode != 0:
            raise SystemExit(f"typst compile failed with exit code {out.returncode}")
        if final and "did not converge" in out.stderr:
            raise SystemExit(
                "the final compile did not converge; see the warnings above"
            )

    def query(self, selector, *, field="value"):
        fields = ["--field", field] if field else []
        out = subprocess.run(
            self.base
            + ["query", *self.flags, *self.inputs(), self.book, selector, *fields],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(out.stdout)

    def inputs(self):
        return ["--input", f"fit={json.dumps(self.fit)}"]


def fit_chapters(typst, pdf):
    """Compile until no chapter ends in a runt, or every level has been tried."""
    fit, tried = {}, {}
    for _ in range(len(LEVELS) + 1):
        typst.compile(pdf, fit)
        changed = False
        for probe in typst.query("<fit>"):
            chapter, fill = str(probe["chapter"]), probe["fill"]
            history = tried.setdefault(chapter, {})
            history[fit.get(chapter, 0)] = fill
            # A chapter that fits on its opener page has no runt to fix.
            if fill >= RUNT or probe["page"] == probe["opener"]:
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
    typst.compile(pdf, fit, final=True)
    return {k: v for k, v in fit.items() if v}


def main():
    parser = argparse.ArgumentParser(
        description=(__doc__ or "Build the book PDF").splitlines()[0]
    )
    parser.add_argument("book", type=Path)
    parser.add_argument("--out", type=Path, help="default: book.typ with a .pdf suffix")
    parser.add_argument(
        "--inputs-from",
        type=Path,
        help="take nixpkgs from this flake's lock, so the build is reproducible",
    )
    args = parser.parse_args()
    inputs_from = args.inputs_from and args.inputs_from.resolve()
    book = args.book.resolve()
    pdf = (args.out or book.with_suffix(".pdf")).resolve()

    try:
        if inputs_from:
            validate_pin(inputs_from)
        typst = Typst(book, inputs_from)
    except subprocess.CalledProcessError:
        sys.exit("could not set up the build with Nix")
    shutil.copyfile(SKILL / "template.typ", book.parent / "template.typ")
    try:
        adjusted = fit_chapters(typst, pdf)
    except subprocess.CalledProcessError as e:
        # Only queries raise this; they capture stderr, so print it here.
        sys.stderr.write(e.stderr or "")
        sys.exit("typst query failed; its error is above")
    print(f"wrote {pdf}; spacing adjusted (chapter: level): {adjusted or 'none'}")
    sys.exit(check.run(pdf, typst))


if __name__ == "__main__":
    main()
