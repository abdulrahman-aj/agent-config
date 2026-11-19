# Release checklist

- Freeze each checkpoint PDF in the repository's gitignored `book/out/reviews/` as
  `review-<commit>.pdf`, never in shared directories like `~/.local/share`, and give the
  user a link they can open.
- Before a release, run `make verify` from a fresh clone (`labs.md`).
- If others will build the book, copy `build.py`, `check.py` and `template.typ` into
  `tools/typeset/` as a set, record the skill commit, and commit a flake lock with a root
  input named `nixpkgs`. With the flake in `lab/`, `make pdf` runs this from the
  repository root; test it from a fresh clone:

  ```bash
  nix shell --inputs-from ./lab nixpkgs#python3 -c python3 tools/typeset/build.py --inputs-from ./lab book/book.typ
  ```
