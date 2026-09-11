# Design Summary

## Architecture Decisions

**Main components:**

- `eligibility.py` — pure domain logic. No Streamlit import. Contains the
  data model (`Role`, `StudentProfile`, `RoleResult`), the fixed role data,
  normalization (`parse_skills`, `normalize_token`), validation
  (`validate_profile`), evaluation (`evaluate_role`, `evaluate_all`), and
  sorting/counting. Every function is a pure function of its inputs — no
  hidden state, no I/O.
- `app.py` — Streamlit UI. A thin rendering layer: reads
  `st.session_state`, calls into `eligibility.py`, renders the result.
  Contains no eligibility rules of its own.
- `cli.py` — optional terminal report, built on the exact same
  `eligibility.py` functions. Exists to prove there is only one eligibility
  implementation (Section 14's requirement, applied more broadly) and to
  give a fast, screenshot-able way to demonstrate correctness without a
  browser.

**Data flow:**

```
raw text fields (session_state)
        │  Evaluate clicked
        ▼
StudentProfile (strings)
        │
        ▼
validate_profile() ──► [] or [error codes]
        │                         │
   (valid)                   (invalid)
        │                         │
        ▼                         ▼
evaluate_all()            results = None
        │                  errors shown
        ▼                  counts cleared
sorted list[RoleResult]
        │
        ▼
render results + counts
```

**Technology choice:** Python + Streamlit. Rationale:

- The domain logic (set membership, numeric comparisons, sorting with
  tuple keys) is naturally expressed in plain Python with no framework.
- Streamlit satisfies the "one attractive primary screen" requirement
  (Section 1) while being pure Python — no HTML/CSS/JS surface to build or
  defend, and it hot-reloads on save, which matters for the live
  modification portion of the interview (Section 21).
- No backend, database, or network service is needed or added — the roles
  are fixed local data (Section 3) and there's a single in-memory profile,
  so a server-side data layer would be pure overhead.

**Why this architecture fits the scope:** the hard part of this problem is
not "build a web app," it's "get five ordering/validation contracts exactly
right." Isolating that logic into one dependency-free module makes it
directly unit-testable (141 non-UI tests run in ~0.2s) and means the UI can't
silently diverge from it — there is exactly one place eligibility is
decided.

## AI Influence

- AI (via the guided prompting strategy in the problem statement, Section
  17) was used to extract the requirements into an explicit rule list
  before any code was written — this surfaced the independent-evaluation
  requirement (Section 9: "do not stop after finding the first failed
  rule") as a first-class design constraint rather than something
  discovered via a failing test later.
- AI initially proposed evaluating rules with early returns (`if branch
  not allowed: return INELIGIBLE`). This was rejected — it directly
  contradicts Section 9 and would make CF05 report only
  `BRANCH_NOT_ALLOWED`-style single reasons instead of all three required
  ones. The implementation instead always evaluates all 5 rule checks and
  appends to a list.
- AI suggested using Streamlit's `st.number_input` for CGPA/year/backlogs
  fields. This was rejected: `number_input` with bounds set would make it
  impossible to type `10.5` for a CGPA field capped at 10, which is
  required to be reachable and rejected (Test 6). All fields are plain
  `st.text_input`, and validation is entirely owned by `eligibility.py`.
- AI flagged that `float("nan")` and `float("inf")` parse successfully in
  Python, which would silently accept `NaN`/`Infinity` as CGPA values —
  this is called out explicitly in the spec (Section 7) as invalid. Fixed
  with an explicit `math.isfinite()` check.

## Trade-offs

- **Simplicity vs. scalability:** the role list is a hardcoded tuple, not
  a loaded/parsed data file. Explicitly justified by the spec — roles are
  "fixed local data" (Section 3) and don't change during evaluation
  (Section 19's assumptions). Adding a data-loading layer would be
  unnecessary abstraction for 5 records that never change.
- **Development speed vs. abstraction:** no repository/service/interface
  layers. One module for logic, one for UI, one optional CLI. Three
  similar-shaped files (profile, roles, results) did not justify a shared
  base class or generic framework.
- **Client-side state vs. persistence:** results live only in
  `st.session_state` for the current browser session. No database, no
  file writes. This matches the "Not Required" list in Section 1
  (no backend services, no user accounts) and Section 19's assumption that
  no persistence is required.
- **Full test suite vs. focused acceptance tests:** the test suite targets
  Section 13's focused test plan plus the Section 12 acceptance tests,
  rather than exhaustively testing every possible input combination.
  Property-based/fuzz testing of the numeric parsers was considered and
  deferred — the boundary cases explicitly named in the spec (0, 10, 10.5,
  2000, 2100, 1999, 2101, NaN, Infinity) are covered directly, which is a
  better time investment for a 30–40 minute interview than broad fuzzing.
