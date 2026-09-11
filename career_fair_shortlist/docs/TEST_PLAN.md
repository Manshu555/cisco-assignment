# Test Plan and Evidence

## Automated Test Suite

157 tests total, in four suites:

| Suite | Tests | Covers |
|---|---:|---|
| `tests/test_eligibility.py` | 27 | pure logic, unit by unit |
| `tests/test_acceptance.py` | 114 | spec criteria, clause by clause |
| `tests/test_app_ui.py` | 10 | headless UI via Streamlit `AppTest` |
| `tests/test_cli.py` | 6 | CLI argument overlay and report shape |

Run with `pytest -v`. Full captured output: `docs/evidence/pytest_output.txt`
(all 157 passed, ~9s). Terminal evidence: `docs/evidence/cli_test_evidence.txt`.

## Focused Test Plan (Section 13)

| Test Area | What Is Verified | Test(s) | Status |
|---|---|---|---|
| Built-in result | 2 eligible, 3 ineligible | `test_builtin_result_statuses`, `test_builtin_counts` | ✅ |
| Branch validation | Blank branch → `INVALID_BRANCH` | `test_blank_branch_is_invalid` | ✅ |
| CGPA validation | `10.5` → `INVALID_CGPA` (also `-1`, `NaN`, `Infinity`) | `test_cgpa_invalid_values` | ✅ |
| CGPA boundary | `8.5` makes CF04 eligible | `test_cgpa_boundary_makes_cf04_eligible` | ✅ |
| Graduation year | Invalid (`1999`, `2101`, `2027.5`) and disallowed-but-valid (`2099`) years | `test_graduation_year_invalid_values`, `test_disallowed_but_valid_graduation_year_is_not_a_validation_error` | ✅ |
| Backlog validation | Negative/non-whole values rejected | `test_backlog_invalid_values` | ✅ |
| Skill parsing | Spaces, empty entries, duplicates | `test_parse_skills_trims_and_ignores_empty_pieces`, `test_parse_skills_collapses_duplicates_case_insensitively` | ✅ |
| Case handling | Branches/skills compared case-insensitively | `test_branch_comparison_is_case_insensitive_and_trimmed`, `test_skill_comparison_is_case_insensitive_and_trimmed` | ✅ |
| No alias inference | `PyTorch` does not satisfy `Python` | `test_similar_skill_is_not_treated_as_match` | ✅ |
| Missing skills | Every missing skill reported once, sorted | `test_missing_skills_sorted_case_insensitively`, `test_cf05_complete_failure_reasons_in_order` | ✅ |
| Failure ordering | Exact required reason order | `test_cf03_only_branch_not_allowed`, `test_cf04_only_cgpa_below_minimum`, `test_cf05_complete_failure_reasons_in_order` | ✅ |
| Role ordering | Eligible first, then ineligible | `test_builtin_result_ordering`, `test_cgpa_boundary_makes_cf04_eligible` | ✅ |
| Title sorting | Case-insensitive ascending, ID as tiebreaker | `test_cgpa_boundary_makes_cf04_eligible` (CF01, CF04, CF02) | ✅ |
| Counts | Counts match result statuses | `test_builtin_counts`, `test_cgpa_boundary_makes_cf04_eligible` | ✅ |
| Reset | Built-in profile and role list restored | `test_reset_restores_builtin_profile_after_edit` (UI) | ✅ |
| Stale state | Invalid profile clears old results | `test_invalid_profile_after_valid_one_returns_none`, `test_invalid_cgpa_clears_results_in_ui` (UI) | ✅ |

## Acceptance Criteria (Section 12) — Manual/CLI Evidence

Captured verbatim output in `docs/evidence/cli_test_evidence.txt`. Summary:

### Test 1 — Built-In Profile
```
Eligible: 2   Ineligible: 3
CF01 -> ELIGIBLE   CF02 -> ELIGIBLE
CF03 -> INELIGIBLE   CF04 -> INELIGIBLE   CF05 -> INELIGIBLE
```
Matches spec exactly. ✅

### Test 2 — CF03 Failure
```
CF03 — Embedded Systems Intern
  - BRANCH_NOT_ALLOWED
```
Only reason present. ✅

### Test 3 — CF04 Failure
```
CF04 — Machine Learning Intern
  - CGPA_BELOW_MINIMUM
```
Only reason present. ✅

### Test 4 — CF05 Complete Failure Reasons
```
CF05 — Platform Engineering Intern
  - GRADUATION_YEAR_NOT_ALLOWED
  - TOO_MANY_ACTIVE_BACKLOGS
  - MISSING_SKILL: Docker
```
Exact order matches spec. ✅

### Test 5 — CGPA Boundary (8.1 → 8.5)
```
Eligible: 3   Ineligible: 2
ELIGIBLE order: CF01 — Data Operations Intern, CF04 — Machine Learning Intern, CF02 — QA Automation Intern
```
Matches spec's required title ordering (Data / Machine / QA). ✅

### Test 6 — Invalid CGPA (10.5)
```
VALIDATION FAILED:
  - INVALID_CGPA
(No role results — profile is invalid.)
```
Confirmed no stale results/counts shown, both in the CLI and in the
headless UI test `test_invalid_cgpa_clears_results_in_ui` (asserts zero
`st.metric` widgets rendered after an invalid Evaluate). ✅

### Test 7 — Built-In Data Synchronization
Verified structurally: `app.py` derives results, counts, and the
validation panel from a single `st.session_state["results"]` /
`["errors"]` pair set atomically inside the Evaluate handler — there is
no code path that updates one without the other. `test_reset_restores_builtin_profile_after_edit`
confirms Reset restores the profile fields; role requirements are static
(`ROLES` is a module-level constant, never mutated). ✅

## Edge Cases Additionally Verified

- Skill list `"Git,, python, ,SQL, GIT, Docker"` → normalizes to
  `Git, python, SQL, Docker` (empty pieces dropped, `GIT`/`Git` collapsed
  to first-seen spelling) — see `docs/evidence/cli_test_evidence.txt`, last block.
- CGPA `NaN` / `Infinity` / `-Infinity` → `INVALID_CGPA` (Python's
  `float()` parses these successfully; caught with `math.isfinite()`).
- Graduation year `2027.5` → `INVALID_GRADUATION_YEAR` (not a whole
  number).
- A *valid but disallowed* graduation year (e.g. `2099`, within
  2000–2100 but not offered by any role) is **not** a validation error —
  it correctly surfaces as `GRADUATION_YEAR_NOT_ALLOWED` per-role instead.
- Skill matching does not infer aliases: `PyTorch` does not satisfy a
  `Python` requirement.

## How To Reproduce This Evidence

```bash
cd career_fair_shortlist
pytest -v                                    # full automated suite
python cli.py                                # Test 1
python cli.py --branch CSE --cgpa 8.5 --grad-year 2027 --backlogs 1 --skills "Git, Python, SQL"   # Test 5
python cli.py --branch CSE --cgpa 10.5 --grad-year 2027 --backlogs 1 --skills "Git, Python, SQL"  # Test 6
streamlit run app.py                         # interactive verification of Tests 1-7
```
