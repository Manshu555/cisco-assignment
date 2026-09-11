# Cisco Assignment — SI26_P06: Career Fair Eligibility Shortlist

A **Career Fair Eligibility Shortlist** for a university placement team. It
compares one student's academic profile against five fixed career-fair roles
and reports, for each role, whether the student is eligible and — if not —
**every** rule that failed.

The application lives in **[`career_fair_shortlist/`](career_fair_shortlist/)**.

**Status:** complete. 161 tests passing; Streamlit UI and CLI both verified.

---

## Quick start

```bash
cd career_fair_shortlist
pip install -r requirements.txt

python -m streamlit run app.py   # browser UI at http://localhost:8501
pytest -q                        # 161 tests, ~10s
python cli.py                    # terminal report, no browser needed
```

Use `python -m streamlit` rather than the bare `streamlit` command — see
[`career_fair_shortlist/AGENTS.md`](career_fair_shortlist/AGENTS.md) §2 for why.

## What it does

A role is eligible only when **all five** rules pass: branch allowed, CGPA ≥
minimum, graduation year allowed, active backlogs ≤ maximum, and every required
skill present.

Every role is evaluated **independently with no short-circuiting**, so an
ineligible role reports *all* of its failed rules rather than stopping at the
first. Reasons appear in a fixed order, with multiple missing skills sorted
case-insensitively. Results are ordered eligible-first, then by title
(case-insensitively), with role ID breaking ties.

With the built-in profile (CSE, 8.1, 2027, 1 backlog, `Git, Python, SQL`):

```
Eligible: 2   Ineligible: 3

ELIGIBLE      CF01 Data Operations Intern · CF02 QA Automation Intern
INELIGIBLE    CF03 BRANCH_NOT_ALLOWED
              CF04 CGPA_BELOW_MINIMUM
              CF05 GRADUATION_YEAR_NOT_ALLOWED
                   TOO_MANY_ACTIVE_BACKLOGS
                   MISSING_SKILL: Docker
```

If any profile field is invalid, evaluation is blocked entirely: results and
both counts are cleared and a validation code is shown. Invalid input can never
leave stale results on screen.

## Architecture

```
eligibility.py   ← all business rules. Pure: no UI imports, no I/O.
      │
      ├── app.py     Streamlit UI    (renders state only)
      ├── cli.py     terminal report (renders state only)
      └── tests/     four suites, 161 tests
```

One rule, one place. Both front ends read the same `RoleResult` list, so the UI
and CLI cannot drift apart, and the logic is unit-testable without a browser.

## Repository layout

| Path | What it is |
|---|---|
| [`career_fair_shortlist/`](career_fair_shortlist/) | the application — start here |
| [`career_fair_shortlist/README.md`](career_fair_shortlist/README.md) | setup, usage, full project detail |
| [`career_fair_shortlist/AGENTS.md`](career_fair_shortlist/AGENTS.md) | full context for AI assistants / a new IDE |
| [`SI26_P06-Career-Fair-Eligibility-Shortlist.md`](SI26_P06-Career-Fair-Eligibility-Shortlist.md) | the authoritative problem specification |
| `AI-Assisted-Coding-Interview-Student-Guide.md` | interview guidance provided with the brief |
| `AI_Assisted_Development_Strategy_Career_Fair_Eligibility (1).docx` | AI-assisted development write-up |

## Scope

Deliberately narrow, per spec §23: no ranking or scoring, no backend, database,
authentication, external API or job feed. The five roles are fixed local data.
Two dependencies only — `streamlit` and `pytest`.

The goal is a small, reliable solution that is fully explainable and quick to
modify, not the most elaborate one.
