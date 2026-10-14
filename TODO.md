# TODO

- [ ] Restore `grill-me` and its separate `grilling` dependency from Matt Pocock's
  pinned upstream revision, and `frontend-design` from Anthropic's pinned revision
  (see their `SOURCE.md` files). Verify exact upstream copies, update provenance
  notes, and keep this in a separate commit from the harness migration.
- [ ] Revisit all shared skills for the T3 setup, especially orchestration and
  delegation (`parallel-work`, `ask-for-review`, and delegation within other skills).
  Remove obsolete harness assumptions and instructions that duplicate T3's injected
  workflow; simplify or retire skills where T3 already provides the behavior.
- [ ] Strengthen delegated-review instructions: reviewers must not modify the
  author's checkout or deployed paths, including ignored/generated files and
  cleanup. Run mutating checks only in scratch copies or isolated worktrees and
  clean up only artifacts created there. Cover the incident where a reviewer
  deleted `.stow/home` aliases and temporarily broke deployed links.
