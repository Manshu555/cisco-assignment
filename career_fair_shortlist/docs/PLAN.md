# Implementation Plan

Five steps, each with a concrete checkpoint, matching Section 16 of the
problem statement.

## Step 1 — Model the student profile and fixed role requirements

Define `StudentProfile` (raw string fields, since the UI collects text) and
`Role` (typed, normalized at construction time) as dataclasses. Hardcode the
five roles from Section 3 and the built-in sample profile from Section 2.

**Checkpoint:** `ROLES` has exactly 5 entries with IDs `CF01`–`CF05` in
spec order, and `SAMPLE_PROFILE` matches Section 2's table field-for-field.

## Step 2 — Implement input normalization and validation

Trim/casefold branch and skill comparisons. Parse skill lists (split on
comma, drop empty pieces, collapse duplicates case-insensitively). Validate
CGPA (finite, 0–10), graduation year (whole number, 2000–2100), backlogs
(whole number, ≥ 0), and non-blank branch — each producing its own error
code, all checked independently (not short-circuited).

**Checkpoint:** Invalid inputs produce the exact required codes —
`INVALID_BRANCH`, `INVALID_CGPA` (including `NaN`/`Infinity`/`10.5`),
`INVALID_GRADUATION_YEAR`, `INVALID_BACKLOG_COUNT`.

## Step 3 — Implement independent eligibility evaluation and deterministic sorting

For each role, check all 5 rules independently and collect every failed
reason in the fixed order (branch → CGPA → year → backlogs → missing
skills, missing skills sorted case-insensitively). Sort results: eligible
before ineligible, then by title (case-insensitive), then by role ID.

**Checkpoint:** Built-in profile reproduces Section 4 exactly — CF01/CF02
eligible; CF03 only `BRANCH_NOT_ALLOWED`; CF04 only `CGPA_BELOW_MINIMUM`;
CF05 all three reasons in order; counts 2/3.

## Step 4 — Build the primary UI and synchronized result/count state

Streamlit UI: editable profile fields, role-requirements table, Evaluate /
Load Sample / Reset actions, validation panel, results list, counts. State
lives in `st.session_state`; an invalid profile clears results and counts
in the same action that surfaces the validation message (no stale state).

**Checkpoint:** Entering CGPA `10.5` and clicking Evaluate clears any
previous results and both counts, and shows `INVALID_CGPA`. Reset restores
the built-in profile and clears any edited state.

## Step 5 — Add focused tests for acceptance criteria and edge cases

pytest suite covering Section 13's focused test plan: built-in result,
CGPA 8.5 boundary, invalid CGPA, CF05 complete reasons, skill parsing,
case handling, ordering, counts, reset, stale-state clearing. Plus headless
UI tests (Streamlit `AppTest`) that click buttons and edit fields, so the
UI layer is verified, not just the pure logic.

**Checkpoint:** `pytest -v` passes all tests (31/31), covering every
Section 12 acceptance test.
