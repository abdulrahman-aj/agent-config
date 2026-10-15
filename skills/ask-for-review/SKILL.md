---
name: ask-for-review
description: Use when requesting an independent review of a diff, commit, range, or PR.
---

- Use a reviewer who did not author the changes.
- Identify the repository and changes under review (commit range, PR, or uncommitted
  files). Explain the problem, trigger, intended outcome, constraints, and evidence.
  Ask whether the change is needed and whether a smaller change would suffice (YAGNI).
- Let the reviewer assess the changes before sharing your verdict. For targeted
  reviews, frame concerns as questions to investigate. Don't ask for agreement.
- Tell the reviewer: keep the author's checkout, deployed paths, and external
  services read-only, including ignored/generated files. Run mutating checks in
  scratch copies or isolated worktrees; use scratch output and deployment targets
  and clean up only artifacts created there.
- Ask the reviewer to classify findings as blockers, improvements, or nits.
  Omit empty categories.
- Verify findings against code or a reproduction before changing anything.
  Explain rejected findings.
