# Contributing

Pull requests and issues are welcome — this skill gets better with more observed parse failures across more ATS platforms.

## Reporting a new failure pattern

Open an issue with:
1. Which ATS/portal you observed it on (Workday, Greenhouse, Lever, iCIMS, etc.)
2. The formatting pattern that failed (a fictional/anonymized example, not your real resume content)
3. What field ended up blank or wrong

**Do not include real company names, personal contact info, or actual resume content in issues or PRs.** Use fictional examples that illustrate the pattern — see `references/failure-patterns.md` for the style.

## Submitting a fix or new rule

1. Fork the repo, branch off `main`.
2. If it's a new failure class, add a rule to the relevant Rule Set in `SKILL.md` and a worked before/after example to `references/failure-patterns.md`.
3. If it's a refinement to an existing rule, update both files together so they stay consistent.
4. Keep `SKILL.md` lean — long explanations and multiple examples belong in `references/`, not the top-level file.
5. Open a PR describing what you observed and why the fix addresses it.

## Style

- Keep everything platform-generic. This isn't a place for anyone's personal career history.
- Prefer showing the before/after over just describing it — that's what makes the pattern testable.
