# Framework-Independent Architecture

**Project:** SI26_P06 — Career Fair Eligibility Shortlist
**Scope:** Core system architecture, components, data flow, interfaces and
responsibilities that remain valid regardless of implementation technology.

The organizing principle is **functional core, imperative shell** — a pure,
deterministic domain surrounded by thin adapters. Chosen because this system's
defining property is that *eligibility is a pure function of (profile, roles)*:
no clock, no randomness, no I/O, no hidden state. Any architecture that lets a
framework touch that function is worse than one that doesn't.

---

## 1. System overview

Four layers, one direction of dependency.

| Layer | Role | Knows about |
|---|---|---|
| **Presentation Adapter** | Collects raw input, renders output, owns view state | Domain Core (calls it) |
| **Application/Orchestration** | Sequences validate -> evaluate -> order -> count; owns the outcome state machine | Domain Core |
| **Domain Core** | Normalization, validation, eligibility rules, ordering, tallies | **Nothing** |
| **Data Provider** | Supplies the immutable role catalog and the built-in sample profile | Domain value types only |

**The invariant:** dependencies point inward. The Domain Core imports no UI, no
storage, no framework, no platform API. Everything above it may be replaced
wholesale — screen, terminal, spreadsheet, mobile — with the core untouched and
its tests unchanged.

**Deployment shape:** a single process, single user, single in-memory session.
No tiers, no services, no network hops.

---

## 2. User interface layer

**What the user interacts with** — six regions, mandated by spec section 11 and
framework-neutral in description:

1. **Profile Editor** — five editable fields (branch, CGPA, graduation year,
   backlogs, skills).
2. **Role Requirements Display** — all five roles with every threshold visible,
   so a reviewer can verify a reason against the rule that produced it without
   reading source.
3. **Action Controls** — Evaluate, Load Sample, Reset.
4. **Validation Display** — status and failure codes.
5. **Result List** — role ID, title, status, ordered failure reasons.
6. **Count Display** — eligible and ineligible tallies.

### Responsibilities it holds

- Capture input **as raw text**, unparsed and uncoerced. Critical: the layer must
  be able to transport `"abc"` and `"10.5"` intact, because rejecting them is the
  *domain's* job and the exact rejection code is graded. A UI that silently
  coerces or blocks bad input destroys the evidence validation needs.
- Render the outcome state faithfully, including rendering *nothing* when there
  is nothing.
- Emit user intents (evaluate / load-sample / reset / field-changed) upward.

### Responsibilities explicitly denied to it

- No eligibility rules, no thresholds, no reason strings composed in the view.
- No independent counting — counts are read from the result set, never
  recomputed while rendering.
- No caching of prior results across an intent.

**The one hard UI contract:** the display must be a **function of the current
outcome state**. Not incrementally patched — derived. This is what makes the
stale-results prohibition (section 8) structural rather than remembered, and it
is the single most important architectural constraint in the whole system.

---

## 3. Application / business logic layer

Two distinct concerns, worth separating even at this size.

### 3a. Orchestration (the workflow)

Owns a **three-state outcome machine**, and nothing else:

```
NOT_EVALUATED   - no evaluation has been requested
INVALID         - validation failed; carries error codes, carries NO results
EVALUATED       - carries exactly five ordered results and both counts
```

Transitions:

| Intent | From any state | To |
|---|---|---|
| Evaluate (profile valid) | -> | `EVALUATED` |
| Evaluate (profile invalid) | -> | `INVALID` |
| Field changed | -> | `NOT_EVALUATED` |
| Load Sample | -> | `EVALUATED` on the built-in profile |
| Reset | -> | `NOT_EVALUATED` with the built-in profile restored |

Why three states and not a boolean: `NOT_EVALUATED`, `INVALID`, and *"zero
eligible"* are three genuinely different situations that must look different on
screen. Collapsing any pair is precisely the bug section 23 warns about. Because
`INVALID` **cannot structurally carry results**, stale display becomes
unrepresentable rather than merely discouraged.

### 3b. Domain Core (the rules)

Five pure operations, each total and side-effect free:

| Operation | Contract |
|---|---|
| **Normalize** | Trim + casefold branch/skill tokens; parse skill text (split on comma -> trim -> drop empties -> collapse duplicates case-insensitively, preserving first-seen spelling). Performs **no** alias, synonym, or relatedness inference. |
| **Validate** | Checks the four validatable fields **independently**, returning the complete set of failure codes. Never short-circuits. Skills have no validity rule. |
| **Evaluate** | For one role and one typed profile: tests all five rules independently, collects every failure reason in fixed order. Eligibility is **derived** as "the reason list is empty" — never computed separately, so status and reasons cannot disagree. |
| **Order** | One total ordering over the full result set: eligible group first, then title ascending case-insensitively, then role ID ascending. A single sort, not two concatenated ones. |
| **Tally** | Derives both counts from the same result set that renders. |

Determinism is a design requirement, not an accident: identical input yields
byte-identical output on any machine, forever.

---

## 4. Data layer

**There is no persistence, and that is the design decision — not an omission.**
Section 19 states no persistence is required; section 23 names databases as
over-engineering here.

Three data categories, three lifetimes:

| Category | Contents | Lifetime | Mutability |
|---|---|---|---|
| **Reference data** | The five role definitions | Program lifetime | **Immutable** |
| **Seed data** | The built-in sample profile | Program lifetime | **Immutable** |
| **Session data** | Current profile text + outcome state | Until reset or exit | Mutable, in-memory only |

**Access pattern:** the Data Provider is a **read-only catalog interface** —
"give me all roles", "give me the sample profile". No create, update, or delete.
No query language, no indexing, no filtering: five records are traversed
linearly, and any indexing would be pure ceremony.

**Immutability matters concretely.** Section 19 requires that role data cannot
change during evaluation. Enforcing that in the type — frozen records, not
defensive copies — makes an entire class of mutation bug impossible and removes
the need to reason about aliasing at all.

**The seam this creates:** because the Provider is an interface rather than
inline literals, role data could later arrive from a file, a config document, or
a service *without any change to the Domain Core*. That is the system's
principal extension point, and it costs nothing today.

---

## 5. External services and integrations

**None. Deliberately, and by requirement.**

| Integration | Status | Basis |
|---|---|---|
| Backend / network service | **Excluded** | Sections 1, 23 |
| External job feed / API | **Excluded** | Sections 1, 23 — roles are fixed local data |
| Database | **Excluded** | Section 19 |
| Authentication / authorization | **Excluded** | Sections 1, 19 |
| Telemetry / analytics | **Excluded** | Not required; would collect student data for no purpose |
| ML / scoring / ranking service | **Excluded** | Section 23 — *"eligibility, not candidate ranking"* |

**Architectural consequence — and it's a large one:** the system has **zero trust
boundaries**, **zero network failure modes**, and **zero partial-failure states**.
Every error is a local, synchronous, deterministic validation error. There is no
timeout, no retry, no circuit breaker, no eventual consistency, no cache
invalidation. Recognizing that this is a *closed, total system* is what licenses
the simplicity everywhere else — most of the usual architectural machinery exists
to manage risks this design simply doesn't have.

If an integration were ever mandated (say, a live role feed), it would enter at
exactly one point: **behind the Data Provider interface**, as an adapter
returning the same immutable role records. Nothing else in the system would
change.

---

## 6. Data flow

```
(1) User edits a field
    Presentation captures RAW TEXT (no coercion, no parsing)
    Orchestration -> NOT_EVALUATED   <- results & counts vanish immediately
                                        (structural fix for section 8)

(2) User triggers Evaluate
    Presentation emits { branch, cgpa, year, backlogs, skills } as raw strings
                      |
(3) VALIDATE - all four fields checked independently, no short-circuit
                      |
         +------------+------------+
    any failure                  none
         |                          |
(4) INVALID                  (5) PARSE + NORMALIZE
    - error codes                typed cgpa/year/backlogs
    - results: NONE              normalized branch
    - counts:  NONE              de-duplicated skill list
    - cannot hold results             |
      by construction          (6) EVALUATE x 5 roles
         |                         all rules independently
         |                         reasons in fixed order
         |                         eligible = (no reasons)
         |                              |
         |                       (7) ORDER - one sort:
         |                           (eligible first, title ci-asc, id asc)
         |                              |
         |                       (8) TALLY from that same ordered set
         |                              |
         +--------------+-----------> (9) EVALUATED
                        |
              (10) RENDER outcome state
                   result list - counts - role cards
                   ALL derived from ONE result set
```

**Two properties the flow guarantees:**

- **Single source of truth.** The result list, the counts, and any optional card
  view all read the *same* ordered collection. They cannot drift, which is
  acceptance test A7 satisfied by construction rather than by synchronization
  code.
- **Unrepresentable staleness.** Results exist only inside `EVALUATED`. Editing a
  field leaves that state. Invalid input enters a state with no room for results.
  There is no code path that displays results for a profile the user has moved on
  from.

---

## 7. Component responsibilities

| Component | Does | Must never |
|---|---|---|
| **Profile Editor** | Capture five raw text values; signal changes | Parse, coerce, validate, or block input |
| **Role Requirements Display** | Render all five roles' thresholds | Filter or reorder roles |
| **Action Controls** | Emit evaluate / load-sample / reset intents | Perform evaluation itself |
| **Validation Display** | Show codes from the outcome state | Compose or translate its own messages |
| **Result Renderer** | Render the ordered result set | Re-sort, re-filter, or reformat reasons |
| **Count Display** | Show tallies from the outcome state | Count independently |
| **Orchestrator** | Own the state machine; sequence the pipeline | Contain any eligibility rule or threshold |
| **Normalizer** | Trim, casefold, parse skill lists | Infer aliases, synonyms, or related skills |
| **Validator** | Independently check four fields -> codes | Short-circuit; validate skills |
| **Evaluator** | All five rules per role -> ordered reasons | Stop at the first failure |
| **Orderer** | One total ordering | Know why the ordering is what it is |
| **Tallier** | Derive counts from results | Read anything but the result set |
| **Role Catalog** | Supply immutable role records | Expose mutation |
| **Sample Provider** | Supply the built-in profile | Drift from the specified values |

**Two responsibilities worth stating as prohibitions**, because both are
load-bearing and both are easy to violate accidentally:

- **Reason strings are a closed vocabulary owned by the Domain Core** — nine
  literals, asserted verbatim in acceptance criteria. If any presentation
  component composes or rewords one, the contract breaks silently.
- **Eligibility is derived, never stored alongside reasons as an independent
  fact.** One source, one truth.

---

## 8. Interfaces / API boundaries

Four boundaries, described as contracts rather than signatures.

### B1. Presentation -> Orchestration (intent boundary)

Upward flow is a small closed set of intents: `Evaluate(raw profile)`,
`LoadSample()`, `Reset()`, `FieldChanged()`. The profile crosses as **five raw
strings**. Nothing typed, nothing validated, nothing coerced. Rationale: the
domain must see exactly what the user typed to reject it correctly.

### B2. Orchestration -> Presentation (state boundary)

Downward flow is **one immutable outcome value** — the three-state machine plus
its payload. Not a stream of update events, not a set of setters. A single value
the view renders wholesale. This is what makes staleness unrepresentable; an
event-patch boundary would reintroduce it.

### B3. Orchestration -> Domain Core (pure-function boundary)

Stateless calls in, values out. No callbacks, no context objects, no injected UI
handles, no exceptions used for control flow — **validation failure is a returned
value, not a thrown error**, because it's an expected outcome rather than an
exceptional one. This is why the Core is testable with no harness at all.

### B4. Domain Core -> Data Provider (catalog boundary)

Read-only: `all_roles()`, `sample_profile()`. Returns immutable records. The sole
seam where role data's *origin* could change without disturbing the rules that
consume it.

**The boundary rule, stated once:** every arrow points inward. Presentation
depends on Orchestration; Orchestration depends on the Core; the Core depends on
nothing. No inner layer ever imports, calls back into, or knows the name of an
outer one.

---

## 9. Security and reliability

**Authentication and authorization: not applicable, by design.** Single local
user, no accounts, no multi-tenancy, no shared or remote data. Section 1 excludes
accounts; section 19 excludes auth. Adding either would be over-engineering *and*
would create a credential-handling risk where none exists.

**Privacy — a genuine consideration.** Section 1 forbids sensitive personal
attributes. The profile contains academic data only: no name, no ID, no contact
details, no protected characteristics. Nothing is persisted, transmitted, or
logged, so there is no data-at-rest and no data-in-transit surface.
**Reliability requirement worth naming explicitly:** eligibility must never
depend on any attribute outside the five specified fields — an audit property,
not just a coding style.

**Input validation is the primary defense**, and it's structured as a total
function: every possible input string maps to either a typed value or a specific
failure code. There is no third outcome, no crash path, no undefined behavior on
`""`, `"abc"`, `"NaN"`, `"Infinity"`, `"-1"`, `"10.5"`, or `"2027.5"`. Since no
input reaches a database, shell, file system, or interpreter, injection classes
are structurally absent — but validation still runs completely, because the
*codes themselves* are the product.

**Error handling philosophy:** validation failures are **returned values**;
genuine defects are the only thing that should ever throw. The three-state
machine means every reachable condition has a defined display. There is no
silent-failure path — the system cannot show results and an error
simultaneously, nor show neither.

### Reliability properties this architecture yields

- **Determinism** — no clock, no randomness, no I/O, no ordering ambiguity. Same
  input, same output, always. Directly enables reliable automated testing.
- **No partial failure** — no network, no external dependency, so no timeout,
  retry, or degraded mode exists to reason about.
- **Immutable reference data** — role definitions cannot be corrupted at runtime.
- **Total ordering** — the composite sort key admits no ties, so output order is
  stable and reproducible rather than implementation-defined.
- **Testable core** — a UI-free domain means the rules can be verified
  exhaustively without launching, rendering, or clicking anything.

**Residual risks, honestly:** the dominant failure mode here is not attack or
outage — it's **environment fragility** (a missing runtime or dependency
preventing startup) and **spec drift** (a reason string or sort key quietly
diverging from the contract). The first is mitigated by pinned dependencies and a
rehearsed cold start; the second by asserting the literal contract values in
tests.

---

## 10. Scalability and maintainability

**Scaling users is a non-goal, and I'd defend refusing to design for it.** One
student profile, one local session, five roles, no persistence (section 19).
Designing for concurrency, sharding, or caching here would add cost against a
requirement that does not exist.

**The scalability that actually matters is scalability of *change*.** Measured
that way:

| Likely change | Blast radius |
|---|---|
| Add a sixth role | One record in the Role Catalog. **Zero logic changes.** |
| Change a threshold | One field in one record. |
| Add a new rule type (e.g. minimum certifications) | One field on the Role record, one independent check in the Evaluator, one reason constant, one ordering position. |
| Change result ordering | The Orderer's sort key. One place. |
| Add a new validation rule | The Validator plus one code constant. |
| Replace the UI entirely | Presentation Adapter only. Core and its tests untouched. |
| Load roles from a file or service | The Data Provider adapter only, behind B4. |
| Support multiple students | Orchestration loops the same pure Core per profile. The Core needs **no** change — it's already stateless. |

That last row is the real test of the design, and it passes: because eligibility
is a pure function with no session state, batch evaluation is a loop, not a
rewrite.

### Maintainability properties

- **Rules live in exactly one place**, so the UI, a terminal report, and any card
  view cannot disagree — section 14's "no second eligibility implementation" is
  guaranteed structurally, not by discipline.
- **Contract values are named constants**, so a spec change is a single-point
  edit and a single-point test failure.
- **The Core is testable in milliseconds** with no browser, no server, no
  fixtures — which is what makes a confident live modification possible at all
  (section 21).
- **Complexity is proportionate.** Four layers for five roles is justified *only*
  because the layer boundary is exactly where the graded requirements sit
  (purity, determinism, no stale state, no duplicated rules). It is not layering
  for its own sake.

**The genuine trade-off accepted:** everything is in memory, so nothing survives
exit, and nothing is shared between users. Both are explicitly permitted, and
both are cheap to revisit later — persistence would enter behind B4, and
multi-user would wrap the stateless Core. Neither would disturb a single rule.

---

## Architecture diagram

```
+----------------------------------------------------------------------+
|                       PRESENTATION ADAPTER                           |
|                    (replaceable - owns no rules)                     |
|                                                                      |
|  +------------+ +--------------+ +----------+ +---------+ +-------+  |
|  |  Profile   | |    Role      | |  Action  | | Result  | |Counts |  |
|  |  Editor    | | Requirements | | Controls | |Renderer | |  +    |  |
|  | (5 fields) | |   Display    | | Ev/Ld/Rs | | (list)  | |Valid. |  |
|  +------------+ +--------------+ +----------+ +---------+ +-------+  |
+-----------+------------------------------------------^---------------+
            |                                          |
   B1  intents +                                B2  ONE immutable
       RAW TEXT (uncoerced)                         outcome state
            |                                          |
+-----------v------------------------------------------+---------------+
|                    APPLICATION / ORCHESTRATION                       |
|                                                                      |
|      +------------------------------------------------------+        |
|      |  OUTCOME STATE MACHINE                               |        |
|      |    NOT_EVALUATED  -  INVALID  -  EVALUATED           |        |
|      |    INVALID cannot hold results  -> staleness is      |        |
|      |    unrepresentable, not merely discouraged           |        |
|      +------------------------------------------------------+        |
|         pipeline:  validate -> parse -> evaluate -> order -> tally   |
+-----------+------------------------------------------^---------------+
            |                                          |
     B3  pure calls                            values out
         (values in)                    (failures RETURNED, not thrown)
            |                                          |
+-----------v------------------------------------------+---------------+
|                          DOMAIN CORE                                 |
|              pure - deterministic - zero dependencies                |
|                                                                      |
|  +-----------+ +----------+ +-----------+ +---------+ +----------+   |
|  | NORMALIZE | | VALIDATE | | EVALUATE  | |  ORDER  | |  TALLY   |   |
|  |trim-fold  | |4 fields  | |5 rules x  | |eligible | | counts   |   |
|  |skill parse| |independ. | |5 roles    | |->title  | | from the |   |
|  |no aliases | |no short- | |no short-  | |->roleid | | SAME set |   |
|  |           | | circuit  | | circuit   | |one sort | |          |   |
|  +-----------+ +----------+ +-----------+ +---------+ +----------+   |
|                                                                      |
|   MODELS:  StudentProfile (raw) - Role (frozen) - EligibilityResult  |
|            ReasonCode vocabulary (9 closed literals)                 |
+-----------+----------------------------------------------------------+
            |
     B4  read-only catalog
            |
+-----------v----------------------------------------------------------+
|                          DATA PROVIDER                               |
|         all_roles()  -  sample_profile()   - IMMUTABLE, read-only    |
|         5 fixed roles (CF01-CF05)  -  built-in student profile       |
|         <- the ONLY seam where data origin could ever change ->      |
+----------------------------------------------------------------------+

========================================================================
  EXTERNAL SERVICES: none - no API - no DB - no auth - no network
  no job feed - no ML - no ranking - no telemetry - no persistence
  => zero trust boundaries - zero partial-failure modes
========================================================================

     Dependency direction:  =======> INWARD ONLY =======>
     Presentation -> Orchestration -> Domain Core -> (nothing)
```

---

## Implementing this architecture in different technologies

The mapping below changes **only the outer ring**. The Domain Core, the state
machine, the four boundaries, and every test of the rules stay identical.

| Architectural element | Python + Streamlit | TypeScript + React | Vanilla JS, single file | CLI (any language) | Mobile (Flutter/native) |
|---|---|---|---|---|---|
| Presentation Adapter | Streamlit widgets | Components + JSX | DOM nodes | Formatted stdout | Widgets / views |
| B1 (intents + raw text) | Widget session keys | Controlled-input props | Event listeners | Argument parsing | Input controllers |
| B2 (one outcome state) | Full script rerun | `useState` + re-render | One `render(state)` fn | One report function | Reactive state object |
| Orchestration | Module + session dict | Reducer / store | Plain state object | Main routine | State notifier |
| Domain Core | Pure module, no UI imports | Pure module, no DOM | Pure functions | Pure module | Pure module |
| Immutable role record | Frozen dataclass | `readonly` interface | `Object.freeze` | Struct / record | Immutable class |
| Data Provider | Module constant | Exported constant | Literal | Constant | Constant |
| Domain tests | pytest, no browser | Vitest, no DOM | Node test runner | Native harness | Unit tests |

**Why the substitution is safe in every column:** each alternative satisfies the
same four contracts — raw text crosses B1 uncoerced, one immutable outcome value
crosses B2, the Core is called as pure functions across B3, and roles arrive
immutably across B4. Nothing in the rules depends on how a button is drawn.

**The one property to verify when swapping the outer ring:** that B2 remains a
*whole-value render* rather than an incremental patch. Frameworks with
declarative re-rendering (Streamlit's rerun, React's reconciliation, Flutter's
rebuild) give this for free. Imperative widget toolkits and hand-written DOM code
do not — there, the burden shifts to a single `render(state)` entry point that
redraws the affected regions wholesale, and that discipline must be enforced
deliberately, because it's the difference between "stale results are impossible"
and "stale results are a bug we hope to catch."

**Extension paths that don't disturb the architecture:** persistence enters as a
Data Provider adapter behind B4. A remote role feed enters at the same seam,
returning the same immutable records. Multi-student batch evaluation wraps the
stateless Core in a loop at the Orchestration layer. A REST or CLI front-end is
simply another Presentation Adapter over the same B1/B2 pair. In every case the
rules — and their tests — are untouched, which is the whole point of putting the
boundary where it is.

---

## How the current implementation maps onto this architecture

| Architectural component | Current file |
|---|---|
| Domain Core (normalize, validate, evaluate, order, tally) | `eligibility.py` |
| Data Provider (`ROLES`, `SAMPLE_PROFILE`) | `eligibility.py` (module constants) |
| Orchestration | Currently inlined in `app.py` session state |
| Presentation Adapter (screen) | `app.py` |
| Presentation Adapter (terminal) | `cli.py` |
| Domain tests (no UI required) | `tests/test_eligibility.py` |
| Presentation tests (headless) | `tests/test_app_ui.py` |

**Known deviation:** the outcome state machine of section 3a is not yet explicit.
`app.py` tracks `evaluated` / `errors` / `results` as three separate session
keys, which permits the `EVALUATED`-with-stale-results combination that the
three-state model makes unrepresentable. Closing that gap is the one change
needed to satisfy section 8 structurally rather than by convention.
