# Career Fair Eligibility Shortlist

Compare one student's academic profile and skills against five fixed
career-fair roles. Shows which roles the student is eligible for, and **every**
failed rule for each ineligible role.

Implements spec **SI26_P06** (`../SI26_P06-Career-Fair-Eligibility-Shortlist.md`
— see §11 below for the exact path). The specification is the authority: where
code and spec disagree, the code is wrong.

**Status:** 157 tests passing. App and CLI both verified working.

> Working on this with an AI assistant or a new IDE? Start with
> **[AGENTS.md](AGENTS.md)** — it carries the full context (rules, invariants,
> state model, and what not to change) in one portable file.

---

## 1. Prerequisites

- Python 3.10+ (developed and verified on 3.11.9)
- Two dependencies only: `streamlit`, `pytest`

## 2. Installation

```bash
cd career_fair_shortlist
pip install -r requirements.txt
```

## 3. Configuration

None. All role data and the sample student profile are hard-coded in
`eligibility.py` — no database, no external API, no job feed, no environment
variables, no accounts.

## 4. Running the application

### Browser UI (primary)

```bash
python -m streamlit run app.py
```

Opens at `http://localhost:8501`. Click **Load Sample** to populate the
built-in profile, edit any field, then click **Evaluate**.

Use `python -m streamlit` rather than the bare `streamlit` command: it runs the
app with the *same* interpreter as `python`, so it cannot pick up a stale
`streamlit` launcher left on `PATH` by another (possibly removed) Python
installation. On the original development machine a half-uninstalled Anaconda
does exactly that — see [AGENTS.md](AGENTS.md) §2 if you hit
`Script file '...streamlit-script.py' is not present.`

### CLI report (alternative / quick demo)

```bash
python cli.py                  # built-in sample profile
python cli.py --cgpa 8.5       # sample profile, CGPA changed (spec Test 5)
python cli.py --cgpa 10.5      # invalid CGPA (spec Test 6)
python cli.py --branch ""      # blank branch -> INVALID_BRANCH
```

Any flag you omit keeps its built-in sample value, so a single flag expresses a
single-field change. An explicitly empty value (`--branch ""`) is honoured
rather than defaulted, so the validation paths stay reachable. Run
`python cli.py --help` to see each flag's default.

## 5. Running tests

```bash
pytest -q                          # all 157, ~9s
pytest tests/test_eligibility.py -q   # logic only, ~0.03s — fastest loop
```

| Suite | Tests | What it covers |
|---|---:|---|
| `tests/test_eligibility.py` | 27 | pure logic, function by function |
| `tests/test_acceptance.py` | 114 | the numbered spec criteria, clause by clause |
| `tests/test_app_ui.py` | 10 | UI behaviour, headless via Streamlit `AppTest` |
| `tests/test_cli.py` | 6 | CLI flag overlay and report shape |

The overlap between the first two suites is intentional: one asks "does this
function work?", the other asks "does the spec hold?". The UI suite drives the
real Streamlit script — clicking buttons, editing fields — with no browser.

Captured evidence: `docs/evidence/`.

## 6. Sample data and expected result

Built-in student profile (spec §2):

| Field | Value |
|---|---|
| Branch | CSE |
| CGPA | 8.1 |
| Graduation Year | 2027 |
| Active Backlogs | 1 |
| Skills | Git, Python, SQL |

Expected output (spec §4) — this is exactly what the app and CLI produce:

```
Eligible: 2   Ineligible: 3

ELIGIBLE
  1. CF01 — Data Operations Intern
  2. CF02 — QA Automation Intern

INELIGIBLE
  3. CF03 — Embedded Systems Intern
       - BRANCH_NOT_ALLOWED
  4. CF04 — Machine Learning Intern
       - CGPA_BELOW_MINIMUM
  5. CF05 — Platform Engineering Intern
       - GRADUATION_YEAR_NOT_ALLOWED
       - TOO_MANY_ACTIVE_BACKLOGS
       - MISSING_SKILL: Docker
```

## 7. The five fixed roles (spec §3)

| ID | Title | Branches | Min CGPA | Grad years | Max backlogs | Skills |
|---|---|---|---:|---|---:|---|
| CF01 | Data Operations Intern | CSE, IT | 7.5 | 2027 | 1 | Python, SQL |
| CF02 | QA Automation Intern | CSE, ECE, IT | 7.0 | 2027, 2028 | 1 | Git |
| CF03 | Embedded Systems Intern | ECE, EEE | 7.5 | 2027 | 1 | Git |
| CF04 | Machine Learning Intern | CSE, IT | 8.5 | 2027 | 1 | Python |
| CF05 | Platform Engineering Intern | CSE, ECE | 7.0 | 2026 | 0 | Docker, Git |

## 8. How it works

A role is eligible only when **all five** rules pass: branch allowed, CGPA
**≥** minimum, graduation year allowed, backlogs **≤** maximum, and every
required skill present.

Every role is evaluated **independently with no short-circuiting**, so an
ineligible role reports *all* of its failed rules rather than just the first.
Reasons always appear in a fixed order, with multiple missing skills sorted
case-insensitively:

```
BRANCH_NOT_ALLOWED
CGPA_BELOW_MINIMUM
GRADUATION_YEAR_NOT_ALLOWED
TOO_MANY_ACTIVE_BACKLOGS
MISSING_SKILL: <skill>
```

Branches and skills are trimmed and compared case-insensitively; skill lists
drop blank entries and collapse duplicates. No aliases or synonyms are ever
inferred — `Python` and `PyTorch` stay distinct.

If any profile field is invalid, evaluation is blocked entirely: results and
both counts are cleared and the validation code is shown. Invalid input can
never leave stale results on screen, even before Evaluate is pressed again —
see [AGENTS.md](AGENTS.md) §5 for the state model that guarantees this.

Results are ordered eligible-first, then by title (case-insensitively), with
role ID breaking ties.

## 9. Architecture

```
eligibility.py   ← all business rules. Pure: no UI imports, no I/O.
      │
      ├── app.py     Streamlit UI    (renders state only)
      ├── cli.py     terminal report (renders state only)
      └── tests/     four suites
```

One rule, one place. `eligibility.py` is deterministic and framework-free, so
it is unit-testable without a browser, and the UI and CLI cannot drift apart —
both read the same `RoleResult` list. **Business rules change in
`eligibility.py` and nowhere else.**

## 10. Project layout

```
career_fair_shortlist/
│
│   # Context — read AGENTS.md first if you are an AI assistant or new here
├── AGENTS.md              # full project context, rules and invariants
├── CLAUDE.md              # short pointer to AGENTS.md
├── README.md              # this file
│
│   # Application — three flat modules, no package indirection
├── eligibility.py         # pure domain logic — roles, validation, evaluation, sorting
├── app.py                 # Streamlit UI (thin rendering layer)
├── cli.py                 # terminal report, same logic, no browser needed
│
│   # Config
├── requirements.txt       # two dependencies: streamlit, pytest
├── pytest.ini             # testpaths + discovery settings
├── conftest.py            # puts the project root on sys.path for tests
├── .gitignore
│
├── tests/                 # 157 tests; plain `import eligibility` works via conftest
│   ├── test_eligibility.py   #  27 — rules, validation, normalization, ordering
│   ├── test_acceptance.py    # 114 — spec criteria, clause by clause
│   ├── test_app_ui.py        #  10 — headless UI behaviour via Streamlit AppTest
│   └── test_cli.py           #   6 — CLI flag overlay and report shape
│
└── docs/
    ├── PLAN.md               # 5-step implementation plan + checkpoints
    ├── ARCHITECTURE.md       # layers, boundaries, data flow
    ├── DESIGN.md             # design decisions, AI influence, trade-offs
    ├── frontend.md           # UI/visual design system for app.py
    ├── TEST_PLAN.md          # test plan table + evidence mapping
    ├── review.md             # strict self-review (historical — see AGENTS.md §8)
    └── evidence/             # generated output, refreshed by re-running the commands
        ├── pytest_output.txt     # captured full test run
        └── cli_test_evidence.txt # captured terminal evidence for key scenarios
```

## 11. Specification

The authoritative spec is at the repo root:
`../SI26_P06-Career-Fair-Eligibility-Shortlist.md`.

Scope is deliberately narrow per spec §23 — no ranking or scoring, no backend,
database, authentication, external API or job feed. The goal is a small,
reliable solution that is fully explainable and quick to modify.
