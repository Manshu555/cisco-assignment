# Strict Senior Review — Career Fair Eligibility Shortlist

**Reviewed against:** `SI26_P06-Career-Fair-Eligibility-Shortlist.md`, sections 1–24
**Scope:** `eligibility.py`, `app.py`, `cli.py`, `tests/`, `docs/`, `README.md`
**Method:** every numbered contract in sections 5–10 traced to code; acceptance
criteria 12.1–12.7 executed; documentation claims checked against observed
behaviour on this machine.

---

## Verdict: 7 / 10

A genuinely strong domain implementation wrapped in a delivery that is not
currently demonstrable. The eligibility rules are spec-exact and I found **zero
rule-logic defects** — that is the hard part and it is done well. The score is
held down by the shell around it: the application does not start on this
machine, the committed test evidence was produced somewhere else, and the
documentation now describes a smaller test suite than the one that exists.

| Dimension | Score | Comment |
|---|---:|---|
| Domain correctness (sections 5–10) | 10/10 | All 14 contracts verified. No defects found. |
| Test suite | 9/10 | 145 tests, fast, spec-traceable. Cannot be run with a bare `pytest`. |
| UI / state handling (sections 8, 11) | 6/10 | Two defensible-but-attackable gaps; both are small fixes. |
| Architecture | 8/10 | Excellent core/shell split. Orchestration left implicit. |
| Documentation | 7/10 | Thorough and well-written, but now drifted from the code. |
| Interview readiness (sections 20, 21) | 3/10 | Nothing runs from a clean terminal. Evidence has a provenance problem. |

An earlier review of this codebase scored it 8/10. The reduction is not a change
of opinion about the code — it reflects two findings surfaced in this pass that
had not previously been checked: the provenance of `docs/pytest_output.txt`
(**S1-2**) and the documentation drift (**S3-3**).

---

## What is correct — verified, not assumed

Stated first because it is most of the system, and because a reviewer should be
able to trust the parts that are right.

- **All five eligibility rules (section 5)** are implemented exactly, including
  `>=` for CGPA and `<=` for backlogs. The 8.5 boundary passes.
- **Independent evaluation (sections 9, 23)** is real. `evaluate_role` appends
  every failed reason with no early exit; CF05 correctly reports all three.
- **Reason ordering (section 9)** is enforced by *code structure* — reasons are
  appended in the required sequence rather than sorted afterwards, so nothing can
  silently reorder them. Missing skills are sorted case-insensitively.
- **Result ordering (section 10)** is a single sort over the whole list with the
  composite key `(not eligible, title.casefold(), role_id)`. Correct, total, and
  stable.
- **Normalization (section 6)** trims and casefolds without inferring aliases.
  `PyTorch` does not satisfy `Python`; duplicate and empty skill pieces are
  handled per spec.
- **Validation (section 7)** rejects `NaN` and `Infinity` via `math.isfinite`
  (the trap here is that Python's `float()` accepts both), and rejects non-whole
  years such as `2027.5`.
- **Eligibility is derived**, not stored — `eligible=not reasons` — so status and
  reasons cannot disagree.
- **Role records are frozen** (section 19: role data must not change during
  evaluation), enforced in the type rather than by convention.
- **The domain module imports no UI.** This is the single best decision in the
  repository: it is why 141 logic tests run in 0.19s with no browser, and why the
  CLI and the screen can never disagree about the rules (section 14).

Acceptance criteria 12.1–12.6 all reproduce correctly at the logic level.

---

## Findings, ranked by severity

### S1 — Blocking. Fix before the interview.

---

#### S1-1 · The application does not run on this machine

**Impact:** Sections 20, 21 and 24 all require a working, quick-starting app.
Right now neither `streamlit run app.py` nor a bare `pytest` succeeds.

**Evidence:**

- `docs/pytest_output.txt` and `README.md` both state Python 3.13 via Anaconda.
  That interpreter is broken here: invoking it fails with
  `Fatal Python error: Failed to import encodings module`, and
  `C:\Users\Lenovo\anaconda3\Scripts\conda.exe` does not exist.
- The only working interpreter is the Windows Store Python 3.11, which has no
  Streamlit installed.
- Consequence: the primary UI cannot be launched, and `tests/test_app_ui.py`
  cannot import.

**Fix (precise):**

```bash
cd career_fair_shortlist
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -q                 # expect 145 passed
streamlit run app.py      # expect http://localhost:8501
```

Then update `README.md` sections 1–2 with the interpreter that actually worked,
and add `.venv/` to `.gitignore`. Rehearse the cold start end-to-end at least
once before the interview — section 21 asks specifically for this.

**Verified:** `streamlit>=1.60` is satisfiable (1.63.0 is current on PyPI), and
the `width="stretch"` arguments used in `app.py` are valid at that version. The
requirement pin is not the problem; the interpreter is.

---

#### S1-2 · Committed test evidence was generated in a different environment

**Impact:** Section 20 asks for test evidence, and section 23 addresses honest
representation of work. This is the finding most likely to cause a problem in the
room, and it is not a code defect.

**Evidence:** `docs/pytest_output.txt` lines 2 and 4 record:

```
platform win32 -- Python 3.13.1 -- C:\Users\91989\AppData\Local\Programs\Python\Python313\python.exe
rootdir: C:\study\web-dev-projects\manshu_cisco_aasignment\career_fair_shortlist
```

Neither the user account (`91989`) nor the path (`C:\study\web-dev-projects\...`)
belongs to the machine this project now sits on (`C:\Users\Lenovo\Downloads\...`).
The file also reports `31 passed`, while the suite now contains **145** tests.

An interviewer reading this file sees a foreign username and a foreign path in
the deliverable's own evidence. Whatever the explanation, it invites a question
you do not want to spend interview time on, and the numbers no longer match the
code regardless.

**Fix:** regenerate the evidence locally, after S1-1:

```bash
pytest -v > docs/pytest_output.txt 2>&1
python cli.py > docs/cli_test_evidence.txt 2>&1
```

Confirm the regenerated header shows this machine's interpreter and path, and
that the pass count matches the current suite. If any part of the work was done
on another machine or with another account, say so plainly in
`docs/AI_INTERACTION.md` — section 23 treats disclosure as expected and
concealment as the actual problem.

---

### S2 — High. Directly attackable against the specification.

---

#### S2-1 · `pytest` aborts at collection; the logic suite is hostage to the UI

**Location:** `tests/test_app_ui.py:14`

**Impact:** One missing optional dependency prevents **all 141 passing logic
tests** from running. `pytest` currently exits non-zero with
`ModuleNotFoundError: No module named 'streamlit'` and an
`Interrupted: 1 error during collection`. Section 21 requires that tests can be
run quickly; the documented command does not work.

**Fix:**

```python
import pytest

pytest.importorskip("streamlit")          # add before the import below

from streamlit.testing.v1 import AppTest
```

The UI tests then skip cleanly when Streamlit is absent and run normally when it
is present. `pytest -q` exits 0 either way. Worth doing even after S1-1: it makes
the fast feedback loop independent of the UI stack, which matters during a live
modification.

---

#### S2-2 · Stale results survive a field edit (section 8 / section 23)

**Location:** `app.py:79-90` and `app.py:118-138`

**Impact:** Section 23 states plainly: *"Never leave old results visible after
invalid student input."* The current implementation only re-evaluates when
**Evaluate** is clicked, so this sequence leaves incorrect output on screen:

1. Click **Evaluate** with the built-in profile — 2 / 3 and five role cards render.
2. Type `10.5` into CGPA. Do not click Evaluate.
3. The 2 / 3 counts and all five role cards **are still displayed**, now
   describing a profile the user is no longer looking at.

A strict reading of section 8 makes this a failure; a lenient reading ties the
clearing to the Evaluate action. It costs about ten lines to remove the ambiguity
entirely, and I would not leave it to the interviewer's interpretation.

**Fix:**

```python
def _clear_results() -> None:
    """Any profile edit invalidates the displayed results (spec section 8/23)."""
    st.session_state["results"] = None
    st.session_state["errors"] = []
    st.session_state["evaluated"] = False


st.text_input("Branch", key="branch", on_change=_clear_results)
st.text_input("CGPA", key="cgpa", on_change=_clear_results, help="0-10, finite number, e.g. 8.1")
st.text_input("Graduation Year", key="grad_year", on_change=_clear_results, help="Whole number, 2000-2100")
st.text_input("Active Backlogs", key="backlogs", on_change=_clear_results, help="Whole number, >= 0")
st.text_area("Skills (comma-separated)", key="skills", on_change=_clear_results, height=80)
```

Add the regression test:

```python
def test_editing_a_field_clears_previously_rendered_results():
    at = _run()
    [b for b in at.button if b.label == "Evaluate"][0].click().run()
    assert {m.label: m.value for m in at.metric}["Eligible"] == "2"

    [t for t in at.text_input if t.label == "CGPA"][0].set_value("10.5").run()
    assert len(at.metric) == 0          # counts cleared without clicking Evaluate
```

---

### S3 — Medium. Weakens the demo or the documentation.

---

#### S3-1 · "Load Sample" and "Reset" are byte-identical

**Location:** `app.py:43-47`

```python
if action == "load_sample":
    _init_state(SAMPLE_PROFILE)
elif action == "reset":
    _init_state(SAMPLE_PROFILE)
```

**Impact:** Section 11 requires three distinct actions. Two of them do exactly
the same thing, and the branch structure advertises that it was meant to
distinguish them. "What's the difference between these two buttons?" currently
has no good answer. Separately, section 12 Test 1 says *"load the built-in
profile in one action"* — today that takes two clicks (Load Sample, then
Evaluate).

**Fix — make Load Sample also evaluate, so Test 1 becomes one click:**

```python
if action in ("load_sample", "reset"):
    _init_state(SAMPLE_PROFILE)
    if action == "load_sample":
        # Section 12 Test 1: the built-in result must appear in ONE action.
        st.session_state["errors"] = validate_profile(SAMPLE_PROFILE)
        st.session_state["results"] = evaluate_all(SAMPLE_PROFILE)
        st.session_state["evaluated"] = True
```

Reset then means "restore the built-in profile, clear everything else", and Load
Sample means "show me the built-in result". Add a UI test asserting that one
click on Load Sample yields 2 / 3 with no separate Evaluate.

---

#### S3-2 · `python cli.py --cgpa 8.5` fails — the CLI cannot demo Test 5

**Location:** `cli.py:27-37`

**Impact:** Acceptance Test 5 is *"change only the CGPA"*. Passing only that flag
defaults every other field to `""`, producing:

```
VALIDATION FAILED:
  - INVALID_BRANCH
  - INVALID_GRADUATION_YEAR
  - INVALID_BACKLOG_COUNT
```

(Confirmed by running it.) The CLI's most natural demo — the one-field change —
is the one thing it cannot do without retyping all five arguments.

**Fix:**

```python
def build_profile_from_args(args: argparse.Namespace) -> StudentProfile:
    """Unspecified flags fall back to the built-in profile, so a single
    --cgpa 8.5 reproduces acceptance Test 5 (spec section 12)."""
    return StudentProfile(
        branch=args.branch if args.branch is not None else SAMPLE_PROFILE.branch,
        cgpa=args.cgpa if args.cgpa is not None else SAMPLE_PROFILE.cgpa,
        grad_year=args.grad_year if args.grad_year is not None else SAMPLE_PROFILE.grad_year,
        backlogs=args.backlogs if args.backlogs is not None else SAMPLE_PROFILE.backlogs,
        skills=args.skills if args.skills is not None else SAMPLE_PROFILE.skills,
    )
```

Note this changes behaviour for callers who deliberately passed empty fields to
demonstrate validation; add an explicit `--blank` flag if that demo is still
wanted. `python cli.py` with no arguments is unaffected.

---

#### S3-3 · Documentation understates the test suite by a factor of nearly five

**Locations:** `README.md` section 5; `docs/TEST_PLAN.md` lines 3–7

Both state **31 tests** (27 logic + 4 UI). The suite now contains **145**
(141 logic across two files + 4 UI). `docs/TEST_PLAN.md` also maps section 13's
focused test plan onto `test_eligibility.py` only, so the newer
`tests/test_acceptance.py` — which is the spec-traceable suite, and the one worth
showing an interviewer — is invisible in the documentation.

**Fix:** update both counts, and add `test_acceptance.py` to the TEST_PLAN
mapping table with its A1–A7 / C1–C8 test identifiers. Being able to say
"145 tests, and here is the one that proves section 10 clause 2" is worth more
than the raw number.

---

### S4 — Low. Polish; fix only if time allows.

| # | Location | Finding | Fix |
|---|---|---|---|
| S4-1 | `app.py:20` | `EMPTY_PROFILE` is defined and never referenced. Dead code invites "what was this for?" | Delete it. |
| S4-2 | `app.py:87-89` | `validate_profile` is called, then `evaluate_all` validates again internally. Harmless at n=5, but awkward when walking through the data flow. | Optional: have `evaluate_all` return `(errors, results)`. Skip if it churns more than ~20 lines. |
| S4-3 | `app.py:33-35` | Orchestration state is three independent session keys (`results`, `errors`, `evaluated`), which permits the illegal combination "evaluated **and** errors **and** stale results" — the root cause of S2-2. | Longer-term: a single explicit outcome value with three states (`NOT_EVALUATED` / `INVALID` / `EVALUATED`), as described in `docs/ARCHITECTURE.md` section 3a. Makes staleness unrepresentable rather than merely handled. |
| S4-4 | `cli.py:63-78` | The CLI re-derives the eligible/ineligible grouping instead of relying on the already-sorted order. Not a rule duplication, but a second place that knows about presentation grouping. | Iterate the sorted list and emit a group header on status change. |
| S4-5 | `app.py:116` | `Min CGPA` renders `7.0` inconsistently against `7.5` in the dataframe. | Format as a string with one decimal place. |
| S4-6 | — | Section 14's optional role-card view is not built as a distinct view. The bordered result containers arguably already satisfy it. | Optional. If added, it must consume the same `RoleResult` list — section 14 forbids a second eligibility implementation. |

---

## Missing requirements

Against sections 11 and 24, **no mandatory requirement is missing**. All six
required UI regions are present, all three actions exist, both counts render,
validation messages display, and all five roles with all their thresholds are
shown.

The only unimplemented item is section 14's role-card view, which the
specification marks explicitly optional.

---

## Architecture assessment

**Strengths, and worth defending under questioning:**

- The core/shell split is exactly where it should be. `eligibility.py` has no UI
  imports, which delivers fast tests, guaranteed CLI/UI agreement, and a safe
  live-modification surface.
- Roles are normalized once at construction rather than casefolded inside the
  comparison loop — the right place to pay that cost.
- Reason ordering enforced structurally, not by a sort key that could be edited
  in isolation.
- No backend, database, authentication, external API, scoring, or ranking.
  Section 23 clean.

**Weaknesses:**

- **Orchestration is implicit** (S4-3). The workflow layer exists conceptually
  but is scattered across session-state keys in the view, which is what allows
  the S2-2 stale-state combination to be representable at all.
- **Two sentinel layers** — `evaluate_all` returns `None` for invalid input, and
  `counts(None)` returns `(None, None)`. It works, and it is defensible as
  simplicity, but it forces every caller to remember the check. Expect this to be
  probed.

Neither weakness is a defect. Both are the kind of thing a reviewer asks about,
so have the answer ready rather than discovering it live.

---

## Usability assessment

| Issue | Severity | Note |
|---|---|---|
| Two buttons with identical behaviour | Medium | S3-1 |
| Results persist after editing the profile | Medium | S2-2 — actively misleading, not merely untidy |
| Built-in result needs two clicks | Low | S3-1 fix resolves it |
| CLI cannot vary a single field | Low | S3-2 |
| No visual link between a result and the profile that produced it | Low | Once S2-2 is fixed the ambiguity disappears |
| Free-text numeric fields | **Not an issue** | Deliberate and correct: number-typed widgets would prevent entering `10.5` or `abc`, destroying the evidence acceptance Test 6 requires. Keep them. |

---

## Fix order

1. **S1-1** — create the venv, install, confirm the app starts and tests pass.
2. **S1-2** — regenerate `pytest_output.txt` and `cli_test_evidence.txt` locally.
3. **S2-1** — `importorskip` guard so `pytest` never aborts on a missing UI dependency.
4. **S2-2** — clear results on field edit, plus the regression test.
5. **S3-1** — differentiate Load Sample from Reset; make Test 1 one click.
6. **S3-2** — CLI argument fallbacks.
7. **S3-3** — correct the documented test counts and map the new suite.
8. **S4-x** — only if time remains.

Items 1–4 are the difference between a 7 and a 9. None of them touch
`eligibility.py`, which is the part that is already right.

---

## Notes on scope of this review

- Domain contracts were verified by reading `eligibility.py` against sections
  5–10 and by executing the test suite (141 logic tests, 0.19s, all passing).
- UI defects S2-2 and S3-1 were identified by code inspection, not by running the
  application — it could not be started on this machine (S1-1). They should be
  re-confirmed once the environment is fixed.
- `python cli.py --cgpa 8.5` (S3-2) was executed; the failure output above is
  verbatim.
- The `streamlit>=1.60` pin and the `width="stretch"` API usage were checked
  against PyPI and found valid — no defect there.
