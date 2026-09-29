# ATS Resume Skill for Claude — Stop Your Resume From Parsing Blank in Workday

**A free, open-source Claude Skill that formats and audits resumes so Workday, Greenhouse, Lever, and iCIMS parse them correctly — instead of leaving your Company, Dates, or Title field blank.**

Most resumes that get formatted "for ATS" still fail silently: they look perfect to a human and to the candidate who wrote them, but the applicant tracking system's parser drops a required field, and the application never surfaces in recruiter search. This skill teaches Claude the specific, tested rules that prevent that — and gives it a repeatable pre-submission and post-upload checklist so the failure gets caught before you hit submit, not after weeks of silence.

[![GitHub stars](https://img.shields.io/github/stars/msdanyg/ats-resume-skill?style=social)](https://github.com/msdanyg/ats-resume-skill/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Skill](https://img.shields.io/badge/Claude-Agent%20Skill-6B4FBB)](https://www.anthropic.com/claude)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## See the failure in 10 seconds

**What you wrote** — looks perfect to you and to any human reader:

```
flowly
Senior Product Manager (Growth)
2021 – 2024
```

**What the ATS actually stored** after its parser read that block:

| Field | Value |
|-------|-------|
| Company | *(blank)* |
| Title | Growth |
| Dates | *(blank)* |

You are now invisible to every recruiter search that filters on company or dates — and nothing told you.

**After this skill rewrites the same three lines:**

```
Senior Product Manager
Flowly
Mar 2021 – Jun 2024
```

| Field | Value |
|-------|-------|
| Company | Flowly |
| Title | Senior Product Manager |
| Dates | Mar 2021 – Jun 2024 |

Same experience, same truth — three rendering fixes (capitalized company on its own line, the parenthetical off the title line, real months on the dates) turn an unsearchable record into a clean one.

> If this saves you a single silent rejection, **⭐ star the repo** so the next job seeker finds it too.

---

## Why this exists

Workday and most other ATS platforms don't show a recruiter your file. They convert it to plain text and run **named-entity recognition (NER)** to extract Job Title / Company / Dates / Description into structured fields. **The recruiter searches and screens those parsed fields — not your PDF.**

A resume with a year-only date range, a stylized company name, or a parenthetical on the wrong line can leave a required field blank — and a blank required field often means the application never routes into recruiter search at all. It looks exactly like getting ignored. It's actually a formatting bug.

This skill encodes the fixes for the specific, repeatable failure patterns that cause this — validated against live Workday submissions, not just general ATS folklore.

## Why generic ATS advice fails

Most "ATS tips" tell you to add more keywords and pick a simple template. That advice isn't wrong, but it aims at the wrong layer. The failure that actually sinks strong candidates isn't keyword density — it's that the parser never extracted your company, title, or dates into the structured fields recruiters search on. Keyword-optimizing a resume that parses blank just produces a well-tuned document nobody can find.

This skill targets the extraction layer instead: the exact rendering patterns — year-only dates, fused header lines, stylized company names, parenthetical titles — that make named-entity recognition silently drop a field. That's the part generic advice never names, and it's the difference between "my resume is optimized" and "my resume is actually in the recruiter's search results."

## What it does

Point Claude (or any agent that supports the open [Agent Skills](https://agentskills.io) `SKILL.md` standard) at this skill and ask it to review, format, or fix a resume for ATS upload. It will:

- **Catch the parse-breaking patterns** — year-only dates, comma-fused title/company lines, lowercase or domain-styled company names, parenthetical title lines, bulleted education entries, tab-column skills sections, and more.
- **Apply the fix**, not just flag the problem — with the correct rendered form for dates, company names, and section structure.
- **Walk you through a pre-submission validation step** (the plain-text paste test) so you catch a bad parse while you can still edit the file.
- **Give you a post-upload checklist** for the fields autofill gets wrong even on a perfectly formatted document.

See [`references/failure-patterns.md`](references/failure-patterns.md) for worked before/after examples of each failure mode.

## Install

### Claude.ai (web or desktop)
1. Download this repo as a ZIP, or clone it and zip the folder yourself — the ZIP needs the skill folder as its root, containing `SKILL.md`.
2. In Claude.ai, go to **Settings → Capabilities → Skills** (Free/Pro/Max) or **Customize → Skills** (Team/Enterprise), enable Code execution and file creation if prompted, then click **+ → Create skill** and upload the ZIP.
3. Ask Claude to review or format your resume for ATS — it will use the skill automatically.

### Claude Code
```bash
git clone https://github.com/msdanyg/ats-resume-skill.git
mkdir -p ~/.claude/skills
cp -r ats-resume-skill ~/.claude/skills/ats-resume-formatting
```
Start a new session — Claude Code detects the skill automatically. Use `/plugin` → Discover if you prefer installing through the plugin browser instead.

### Any other Agent-Skills-compatible tool
This repo follows the open [`SKILL.md` + YAML frontmatter standard](https://agentskills.io), so it should drop into any agent that supports the spec with no conversion needed — check that tool's own skills directory convention.

## Usage examples

Once installed, just ask naturally:

- *"Format my resume for Workday."*
- *"Why does my ATS resume keep leaving the Company field blank?"*
- *"Review this resume for ATS parsing issues before I upload it."*
- *"Is this resume single-column and parse-safe?"*

Claude will apply the rule sets in `SKILL.md`, flag anything in your draft that matches a known failure pattern, and rewrite the affected lines.

## What's inside

```
ats-resume-skill/
├── SKILL.md                        # The skill Claude loads — rules + checklist
└── references/
    └── failure-patterns.md         # Worked before/after examples, failure by failure
```

## Scope & limitations

- This skill governs **parsing and rendering** — getting your real experience into the system of record cleanly. It has no opinion on your content, wording, or metrics, and it will never fabricate experience.
- It's tuned against Workday's public-facing parsing behavior (the most common enterprise ATS) but the underlying rules — consistent date formats, isolated company names, no fused header lines, no bulleted education — generalize to Greenhouse, Lever, iCIMS, and most other NER-based parsers.
- **No format guarantees a 100% clean parse.** That's exactly why the skill treats the pre-submission paste test and post-upload manual field verification as mandatory, not optional.
- ATS behavior changes over time. If you observe a new failure pattern, please open an issue or PR — see below.

## Contributing

Found a parse failure this skill doesn't cover? Open an issue with the pattern (anonymize any real company/personal data) or submit a PR adding it to `references/failure-patterns.md` and, if it's a new rule class, `SKILL.md`. Keep examples fictional — this repo doesn't accept real resume content, screenshots containing personal data, or company-specific claims.

## License

[MIT](LICENSE) — use it, fork it, adapt it into your own skill collection.

---

Built by [Daniel Glickman](https://danielglickman.com) — B2B SaaS product marketing leader who builds and ships production AI systems (RAG pipelines, MCP servers, deployed agents) rather than just talking about them. More AI-builder work at [cmoconfessions.com](https://cmoconfessions.com).

**Keywords:** ATS resume, Workday resume parsing, applicant tracking system, resume formatting, Claude Skill, Claude Agent Skills, SKILL.md, job search tools, resume optimization, career tools, AI job search, resume parser, Workday autofill, ATS-friendly resume, resume NER parsing.
