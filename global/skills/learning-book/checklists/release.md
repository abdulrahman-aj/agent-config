# Release checklist

Use this before sharing a version with the user or anyone else.

- Run the lab checklist's verification from a fresh clone.
- Freeze the PDF under a name that includes its source commit, and give the user that
  PDF in a form they can open where they read, such as a link.
- If others will build the book, copy `build.py`, `check.py` and `template.typ` into
  `tools/typeset/` as a set and record the skill commit. Commit a flake lock with a
  root input named `nixpkgs`. With the flake in `lab/`, `make pdf` runs this from the
  repository root; test it from a fresh clone:

  ```bash
  nix shell --inputs-from ./lab nixpkgs#python3 -c python3 tools/typeset/build.py --inputs-from ./lab book/book.typ
  ```

- When you change the template or checker, confirm that a deliberately broken link,
  label or pin fails the build.
- If the book will be shared, check that it describes its reader as a group, not as
  one person, and that quotes from other books are brief and inside your own
  explanation.
- When the plan changed since the last release, check the title page, front matter,
  exercises and capstone for the old promise.
