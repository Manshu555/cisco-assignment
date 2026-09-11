# Frontend Design System — Career Fair Eligibility Shortlist

**Stack:** Streamlit (Python). Not React, not Next.js — the design below is
built for what Streamlit can actually render, not adapted from a CSS framework.
**Status:** **implemented** in `app.py` + `.streamlit/config.toml` (2026-09-11).
Verified against Streamlit 1.63 in a real browser; 161 tests passing.
See section 8 for what shipped and what was deliberately left out.
**Hard rule:** this document changes `app.py` only. `eligibility.py` is never
touched by visual work.

---

## 1. Design philosophy

**"A placement officer should read the answer in three seconds, and trust it."**

This is a decision-support tool, not a marketing page. Three principles, in
priority order:

1. **The verdict is the interface.** Eligible/ineligible counts and the ranked
   role list are the product. Everything else — the form, the requirements
   table — is supporting material and should recede visually.
2. **Failure reasons are evidence, not decoration.** Each reason is a literal
   contract string (`MISSING_SKILL: Docker`). They are rendered in monospace
   because they *are* machine tokens, and they are never reworded, sentence-cased
   or prettified — the specification asserts them verbatim.
3. **State is never ambiguous.** The app has four states (idle / valid / stale /
   invalid). Each gets a distinct, labelled visual treatment. A user must never
   wonder whether what they are looking at reflects what they typed.

**Anti-goals:** gradients, shadows deeper than 2px, animation, illustration,
hero sections, marketing copy. "Clean and professional" here means *quiet* —
restraint reads as competence in an internal tool.

---

## 2. Stack constraints (read before designing anything)

Streamlit is not a CSS framework. Three tiers of styling, in descending order of
reliability. **Stay in tier 1 wherever possible.**

| Tier | Mechanism | Reliability | Use for |
|---|---|---|---|
| **1** | `.streamlit/config.toml` `[theme]` | Official, survives upgrades | Colour, font, radius, borders — ~80% of this redesign |
| **2** | Native semantic widgets (`st.metric`, `st.container(border=True)`, `st.badge`, colour-markdown) | Official | Structure and status |
| **3** | `st.html` / `unsafe_allow_html` CSS | **Fragile** — internal class names are hashed and change between releases | Last resort, ≤ 5 rules, `data-testid` selectors only |

**Consequence:** the palette below is expressed as theme tokens, not as a
stylesheet. This is a feature — it means the redesign is ~30 lines of TOML plus
markup changes, and it cannot rot when Streamlit updates.

### Verify which theme keys your version supports

Core keys work everywhere. The 2025-era keys (`baseRadius`, `borderColor`,
`headingFont`, `linkColor`, `fontFaces`, `[theme.sidebar]`) landed across
1.44–1.50 and are **available on 1.63**, but confirm before relying on them —
Streamlit ignores unknown keys silently, so a typo looks like "the design didn't
apply":

```bash
python -c "import streamlit; print(streamlit.__version__)"
streamlit config show | sed -n '/\[theme\]/,/^\[/p'
```

If a key is absent from that output, it is not supported — fall back to tier 2.

---

## 3. Layout & structure

### Current problems

Reading `app.py` as it stands:

1. **The answer is below the fold.** The right column renders the Role
   Requirements table *first*, pushing counts and results down. The primary
   output is the least prominent thing on screen.
2. **Cause and effect are diagonally opposite.** Validation messages sit
   bottom-left; results sit top-right. The two panels that always change
   together are as far apart as the layout allows.
3. **Flat hierarchy.** Title, three `st.subheader`s, and everything else at body
   weight. Nothing signals what matters.
4. **Layout jumps.** Counts exist only in the `valid` state, so the results
   column shifts vertically on every state change.
5. **Status is carried by an emoji.** ✅/❌ plus a code-formatted word is doing
   the work a proper status treatment should.
6. **Reference data occupies prime space.** The requirements table is looked at
   once, then ignored — but it holds the top-right corner permanently.

### Proposed structure

```
┌───────────────────────────────────────────────────────────────────────┐
│  Career Fair Eligibility Shortlist              [ status pill ]       │  header
│  One profile · five fixed roles · every failed rule reported          │
├──────────────────────┬────────────────────────────────────────────────┤
│  STUDENT PROFILE     │   ┌──────────────┐  ┌──────────────┐           │
│  ┌────────────────┐  │   │  ELIGIBLE    │  │  INELIGIBLE  │           │  KPI row
│  │ Branch         │  │   │      2       │  │      3       │           │  (always
│  │ CGPA           │  │   └──────────────┘  └──────────────┘           │  present)
│  │ Graduation Year│  │                                                │
│  │ Active Backlogs│  │   RESULTS              [ Cards | Table ]       │
│  │ Skills         │  │   ┌──────────────────────────────────────┐     │
│  └────────────────┘  │   │ 1 · CF01  Data Operations Intern      │    │
│                      │   │   ELIGIBLE                            │    │
│  [Evaluate] [Sample] │   ├──────────────────────────────────────┤     │
│  [Reset]             │   │ 5 · CF05  Platform Engineering Intern │    │
│                      │   │   INELIGIBLE                          │    │
│  ── VALIDATION ──    │   │   GRADUATION_YEAR_NOT_ALLOWED         │    │
│  ┌────────────────┐  │   │   TOO_MANY_ACTIVE_BACKLOGS            │    │
│  │ callout        │  │   │   MISSING_SKILL: Docker               │    │
│  └────────────────┘  │   └──────────────────────────────────────┘     │
│                      │                                                │
│                      │   ▸ Role requirements (5 roles)                │
└──────────────────────┴────────────────────────────────────────────────┘
```

**Six changes, each with a reason:**

| # | Change | Why |
|---|---|---|
| L1 | Counts move to a **persistent KPI row at the top of the results column** | The verdict becomes the first thing read. Reserving the space in all four states kills the layout jump. |
| L2 | **Role requirements move below results**, inside an expander that is open by default | Still visible on the primary screen (spec §11 satisfied), but no longer outranking the output. |
| L3 | **Validation callout moves directly beneath the action buttons** | Cause and effect adjacent. It already lives in the left column — just tighten the gap. |
| L4 | **Status pill in the header** reflecting the four states | One glance answers "is this current?" |
| L5 | Column ratio `[1, 1.4]` → **`[0.85, 1.6]`** | The form is fixed-size; results grow. Give the output the room. |
| L6 | **Segmented control: Cards / Table** over the same result list | Delivers spec §14's optional role-card view. Both views read the same `RoleResult` objects — §14 forbids a second eligibility implementation. |

**Rejected: `st.form`.** Batching the five inputs into a form would be
conventional, but form widgets only commit on submit, which makes the `stale`
state unreachable and would silently delete a tested behaviour. The current
snapshot-comparison model is better than a form here. Do not "improve" this.

---

## 4. Colour palette

Semantic tokens, not decorative ones. Every value below was contrast-checked
against its actual background — measured ratios, not estimates.

### Neutrals

| Token | Hex | RGB | Use | Contrast |
|---|---|---|---|---|
| `ink` | `#0F172A` | 15, 23, 42 | Headings, role titles | **17.85:1** on white |
| `body` | `#334155` | 51, 65, 85 | Body text, labels | **10.35:1** on white |
| `muted` | `#64748B` | 100, 116, 139 | Captions, helper text | **4.76:1** on white ✓ AA |
| `border` | `#CBD5E1` | 203, 213, 225 | Card and input borders | non-text |
| `subtle` | `#F1F5F9` | 241, 245, 249 | Secondary surfaces, table header | surface |
| `canvas` | `#F8FAFC` | 248, 250, 252 | Page background | surface |
| `surface` | `#FFFFFF` | 255, 255, 255 | Cards, inputs | surface |

### Semantic

| Token | Hex | Use | Contrast |
|---|---|---|---|
| `primary` | `#1D4ED8` | Primary button, focus ring, links | **6.7:1** both directions vs white |
| `primary-hover` | `#1E40AF` | Hover state | — |
| `primary-wash` | `#EFF6FF` | Selected segment background | surface |
| `success` | `#065F46` | Eligible text and badge | **7.29:1** on `success-wash` |
| `success-wash` | `#ECFDF5` | Eligible card tint | surface |
| `success-edge` | `#A7F3D0` | Eligible card left border | non-text |
| `danger` | `#991B1B` | Ineligible text, validation errors | **7.6:1** on `danger-wash` |
| `danger-wash` | `#FEF2F2` | Ineligible card tint | surface |
| `danger-edge` | `#FECACA` | Ineligible card left border | non-text |
| `warning` | `#B45309` | Stale-state callout | **4.84:1** on `warning-wash` ✓ AA |
| `warning-wash` | `#FFFBEB` | Stale callout background | surface |

**Every text pairing meets WCAG AA (≥ 4.5:1); most exceed AAA (≥ 7:1).**

**Colour is never the only signal.** Eligible/ineligible is carried by the word
`ELIGIBLE`/`INELIGIBLE`, position (eligible sorts first), *and* colour. This
matters for the ~8% of men with colour-vision deficiency, and red/green is the
worst possible pairing to rely on alone.

### `.streamlit/config.toml`

```toml
[theme]
# --- core keys: supported on every modern Streamlit ---
base                    = "light"
primaryColor            = "#1D4ED8"
backgroundColor         = "#F8FAFC"
secondaryBackgroundColor = "#FFFFFF"
textColor               = "#334155"
font                    = "sans serif"

# --- 2025-era keys: verify with `streamlit config show` first ---
baseRadius              = "0.5rem"
borderColor             = "#CBD5E1"
linkColor               = "#1D4ED8"
showWidgetBorder        = true
```

Note the inversion: `backgroundColor` is the *canvas* tint and
`secondaryBackgroundColor` is white. Streamlit paints cards and inputs with the
secondary colour, so this makes surfaces lift off the page rather than sink in.

---

## 5. Typography

### Families

| Role | Family | Fallback stack |
|---|---|---|
| UI / body | **Inter** | `-apple-system, "Segoe UI", Roboto, sans-serif` |
| Reason codes, role IDs, numerals | **JetBrains Mono** | `"SF Mono", Consolas, "Liberation Mono", monospace` |

**Why a mono face is not decorative here.** Reason codes are contract strings
asserted character-for-character by 157 tests. Monospace signals "this is a
literal token, not prose", discourages anyone from rewording it, and aligns
`MISSING_SKILL:` prefixes into a scannable column. Role IDs (`CF01`) and counts
get the same treatment — tabular figures keep digits aligned.

Inter is the default fallback on most systems and is optional; the system stack
alone is perfectly acceptable and costs zero load time. Only pull the webfont if
`theme.fontFaces` is supported on your version.

### Scale

| Element | Size | Weight | Colour | Notes |
|---|---|---|---|---|
| Page title | 28px | 600 | `ink` | Tracking −0.02em |
| Subtitle | 14px | 400 | `muted` | One line, no marketing copy |
| Section heading | 13px | 600 | `muted` | **Uppercase, tracking 0.06em** — quiet labels, not competing headlines |
| KPI value | 40px | 700 | `ink` | Tabular figures |
| KPI label | 12px | 600 | `muted` | Uppercase |
| Role title | 16px | 600 | `ink` | |
| Role ID | 13px | 500 | `muted` | Mono |
| Status word | 11px | 700 | semantic | Uppercase, tracking 0.08em |
| Reason code | 13px | 500 | `danger` | Mono |
| Form label | 13px | 500 | `body` | |
| Helper text | 12px | 400 | `muted` | |

Body line-height 1.5; headings 1.25. Never below 12px.

---

## 6. Component checklist

Build or restyle, in dependency order.

- [x] **C1 · Theme file** — `.streamlit/config.toml`. *Do first: ~60% of the
      visual change lands here with zero markup edits.*
- [x] **C2 · Page header** — title, one-line subtitle, right-aligned status pill.
- [x] **C3 · Status pill** — 4 variants:
      `Ready` (muted) · `Evaluated` (success) · `Needs re-evaluation` (warning) ·
      `Invalid profile` (danger).
- [x] **C4 · Section label** — uppercase micro-heading replacing `st.subheader`.
- [x] **C5 · KPI tile** ×2 — Eligible / Ineligible. **Always rendered.** Shows an
      em-dash placeholder when there is no result.
      ⚠️ *`st.metric` labels must stay exactly `"Eligible"` / `"Ineligible"` — 6
      tests assert them.*
- [x] **C6 · Profile form field** — consistent label, helper text, placeholder.
      ⚠️ *`st.text_input` labels must stay `"Branch"`, `"CGPA"`,
      `"Graduation Year"`, `"Active Backlogs"` — tests select on them.*
- [x] **C7 · Button group** — `Evaluate` primary, `Load Sample` / `Reset`
      secondary. ⚠️ *Labels are asserted by tests.*
- [x] **C8 · Validation callout** — 4 states, icon + message + code list. Error
      bodies must still contain the raw code (`INVALID_CGPA`) — asserted.
- [x] **C9 · Role result card** — eligible and ineligible variants. Rank number,
      role ID (mono), title, status word, reason list. Coloured left edge.
- [x] **C10 · Reason chip** — mono, danger-tinted, one per line. Verbatim text.
- [x] **C11 · Results toolbar** — `Cards | Table` segmented control (spec §14).
- [x] **C12 · Requirements table** — restyled `st.dataframe` in a
      default-open expander below results. Keep the `%.1f` CGPA format.
- [x] **C13 · Empty state** — one component, three messages (idle / stale /
      invalid). Centred, muted, same height in every state to prevent jump.

---

## 7. Implementation notes

### Order of work

**Step 1 — Theme only.** Create `.streamlit/config.toml`, restart, screenshot.
Change nothing else. This de-risks everything: if the app looks materially
better with zero markup edits, the remaining steps are refinement rather than
rescue.
› *Checkpoint:* `pytest -q` still 157 passing (config cannot affect logic), app
still starts.

**Step 2 — Layout skeleton.** Reorder the right column to KPI row → results →
requirements expander. Change the column ratio. Move the validation callout up.
No new styling yet.
› *Checkpoint:* all four states render without vertical jump; UI tests green.

**Step 3 — Components C2–C5.** Header, status pill, section labels, persistent
KPI tiles.
› *Checkpoint:* `len(at.metric) == 0` assertions still hold in non-valid states
— **if KPI tiles are rendered via `st.metric` in every state, three tests break.**
Render the placeholder tiles as markdown, and use real `st.metric` only in the
`valid` state.

**Step 4 — Result cards C9–C11.** The visual centrepiece. Coloured left edge,
mono reason chips, rank numerals.
› *Checkpoint:* the ordering test that reads `at.markdown` still finds reason
strings verbatim.

**Step 5 — Polish.** Requirements table, empty states, segmented control,
focus-visible rings.
› *Checkpoint:* full suite green; keyboard-only pass; screenshots captured for
`docs/`.

### Guardrails

**These will break tests if changed** — the headless UI suite selects widgets by
label:

- Button labels: `Evaluate`, `Load Sample`, `Reset`
- Input labels: `Branch`, `CGPA`, `Graduation Year`, `Active Backlogs`
- Metric labels: `Eligible`, `Ineligible`
- `st.metric` must render **only** in the `valid` state (`len(at.metric) == 0`
  is asserted in idle, stale and invalid)
- Reason and validation strings must appear **verbatim** in rendered markdown

If a design change genuinely requires a different label, update the test in the
same commit and say so — never loosen an assertion to make a visual change pass.

**These must not change at all:**

- `eligibility.py` — no rule, threshold, code string or sort key
- The four-state model in `app.py`'s docstring
- Result ordering, or the reason order within a card
- Reason text — no sentence-casing, no humanising, no icon substitution

### CSS rules of engagement

If tier 3 CSS becomes unavoidable, cap it at five rules, use `st.html` once near
the top of the script, and target only `data-testid` attributes
(`[data-testid="stMetric"]`, `[data-testid="stVerticalBlockBorderWrapper"]`) —
never hashed emotion class names. Add a comment naming the Streamlit version it
was written against, because it *will* need revisiting on upgrade.

### Accessibility checklist

- [ ] Every text pairing ≥ 4.5:1 (table in §4 — all pass)
- [ ] Status never conveyed by colour or icon alone
- [ ] Full keyboard traversal: fields → Evaluate → Sample → Reset
- [ ] Visible focus ring, 2px `primary`, never `outline: none`
- [ ] Validation errors adjacent to the form, not only in the results column
- [ ] Emoji removed from status (screen readers announce "white heavy check
      mark"); the word `ELIGIBLE` carries the meaning

### Dark mode

Out of scope for the first pass. Streamlit honours the OS preference when
`base = "light"` is *not* pinned; pinning it forces one considered look, which is
the right trade for a demo. If added later, invert `canvas`/`surface` and lift
`success`/`danger` toward their 400-level tints for contrast on dark
backgrounds — the wash and edge tokens do not survive inversion unchanged.

---

## 8. Implementation record (2026-09-11)

Built in the order section 7 prescribes. Theme first, then layout, then
components — each step verified before starting the next.

**Landed:** all of C1–C13. Theme tokens (`.streamlit/config.toml`), header with
status pill, uppercase section labels, persistent KPI row, result cards with
coloured left edge and monospace reason codes, `Cards | Table` segmented
control (spec §14), requirements table in a default-open expander below the
results, and a shared empty-state component.

**Every key in section 4 is supported on 1.63** — verified with
`streamlit config show` before use, per section 2. The version also offers
`metricValueFontSize`, `codeFont` and `dataframeHeaderBackgroundColor`, which
were used to push more of the design into tier 1 than originally planned.

**Zero tier-3 CSS was needed.** The section 2 budget allowed up to five rules
against `data-testid` selectors; none were used. Per-card tints are inline
styles on elements this file owns, so nothing depends on hashed class names and
nothing can rot on upgrade.

### Two things the plan did not anticipate

**L1 needed a fixed-height container, not just a placeholder.** Rendering a
markdown placeholder in the non-valid states was not sufficient: `st.metric`
and a markdown block are different element types with different intrinsic
heights, leaving a measured **24.2px** jump. Both branches are now pinned
inside `st.container(height=KPI_HEIGHT)`, measured to **0.0px** across all four
states.

**The stale callout was blue.** Section 4 assigns `warning` to stale, but
`st.info` renders blue and contradicted the amber pill. Now `st.warning`.

### Test impact

One test broke, exactly where section 7 Step 4 predicted:
`test_builtin_results_render_in_spec_order_with_reasons` matched the old
`**1. CF01 — …**` / `- CODE` markup. Following the section 7 guardrail it was
**rewritten rather than loosened** — it now parses each card and asserts the
reason list *per role*, which is stricter than the previous flat list. Four
tests were added (card ordering at the 8.5 boundary, table/card parity, KPI
placeholder behaviour, status pill across all four states).

Suite: **157 → 161 passing.** No guardrail label changed; `eligibility.py` was
not touched.

### Not done

- **Inter / JetBrains Mono webfonts** (§5) — the system stacks are used
  instead. `fontFaces` is supported, but a webfont costs load time for a demo
  and the mono stack already achieves the "this is a literal token" signal.
- **Dark mode** — explicitly out of scope in §9, and `base = "light"` is pinned.
