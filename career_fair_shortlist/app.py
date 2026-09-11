"""
Career Fair Eligibility Shortlist - Streamlit UI.

This module renders state only. Every eligibility rule, normalization step and
validation code lives in eligibility.py and is imported from there, so the UI,
the CLI and the tests all share one implementation of the business rules.

State model
-----------
Widget values are the single source of truth for the *inputs*. Pressing
Evaluate takes a snapshot of the profile it evaluated. On every rerun the live
widget values are compared against that snapshot, and the panel state is
*derived* (never mutated in place) so the screen can never disagree with the
inputs:

    idle    - nothing evaluated yet
    valid   - live profile matches the snapshot, results are current
    invalid - a field is invalid; results and counts are withheld (spec 8, 23)
    stale   - profile edited since the last Evaluate; results withheld

Visual design
-------------
Layout, palette and type scale follow docs/frontend.md. Colour is expressed as
theme tokens in .streamlit/config.toml wherever Streamlit supports it; the
per-card tints below need per-element values that no theme key can express, so
they are inlined here as named constants rather than as CSS targeting hashed
class names (which break on upgrade - see docs/frontend.md section 2).
"""

import html

import streamlit as st

from eligibility import (
    ROLES,
    SAMPLE_PROFILE,
    StudentProfile,
    counts,
    evaluate_all,
    validate_profile,
)

st.set_page_config(page_title="Career Fair Eligibility Shortlist", layout="wide")

FIELD_KEYS = ("branch", "cgpa", "grad_year", "backlogs", "skills")

# Palette - docs/frontend.md section 4. Every text pairing is >= 4.5:1.
INK, BODY, MUTED = "#0F172A", "#334155", "#64748B"
BORDER, SUBTLE, SURFACE = "#CBD5E1", "#F1F5F9", "#FFFFFF"
SUCCESS, SUCCESS_WASH, SUCCESS_EDGE = "#065F46", "#ECFDF5", "#A7F3D0"
DANGER, DANGER_WASH, DANGER_EDGE = "#991B1B", "#FEF2F2", "#FECACA"
WARNING, WARNING_WASH = "#B45309", "#FFFBEB"
PRIMARY = "#1D4ED8"

MONO = 'ui-monospace, "SF Mono", Consolas, "Liberation Mono", monospace'

# Tall enough for the largest KPI variant (st.metric at 40px) so the tile
# height is identical in all four states. Measured, not guessed.
KPI_HEIGHT = 96

# Status pill copy and colour per state (docs/frontend.md C3).
PILL = {
    "idle": ("Ready", MUTED, SUBTLE, BORDER),
    "valid": ("Evaluated", SUCCESS, SUCCESS_WASH, SUCCESS_EDGE),
    "stale": ("Needs re-evaluation", WARNING, WARNING_WASH, "#FDE68A"),
    "invalid": ("Invalid profile", DANGER, DANGER_WASH, DANGER_EDGE),
}


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def _init_state(profile: StudentProfile) -> None:
    """Load a profile into the widgets and clear every evaluation artefact."""
    st.session_state["branch"] = profile.branch
    st.session_state["cgpa"] = profile.cgpa
    st.session_state["grad_year"] = profile.grad_year
    st.session_state["backlogs"] = profile.backlogs
    st.session_state["skills"] = profile.skills
    st.session_state["results"] = None
    st.session_state["errors"] = []
    st.session_state["evaluated"] = False
    st.session_state["evaluated_profile"] = None


if "branch" not in st.session_state:
    _init_state(SAMPLE_PROFILE)

# Button actions are handled here, before the widgets are instantiated:
# Streamlit forbids writing to a widget's session_state key once it has
# rendered, so the click sets a flag and reruns.
if st.session_state.pop("_pending_action", None) in ("load_sample", "reset"):
    _init_state(SAMPLE_PROFILE)


def _live_profile() -> StudentProfile:
    return StudentProfile(**{key: st.session_state[key] for key in FIELD_KEYS})


# ---------------------------------------------------------------------------
# Presentation helpers
# ---------------------------------------------------------------------------

def section_label(text: str) -> None:
    """Quiet uppercase micro-heading (docs/frontend.md C4)."""
    st.markdown(
        f'<div style="font-size:13px;font-weight:600;color:{MUTED};'
        f'text-transform:uppercase;letter-spacing:.06em;'
        f'margin:0 0 .35rem;">{html.escape(text)}</div>',
        unsafe_allow_html=True,
    )


def kpi_placeholder(label: str) -> None:
    """
    Stand-in KPI tile for the three non-valid states.

    Deliberately *not* st.metric: three tests assert `len(at.metric) == 0`
    outside the valid state, and the spec requires counts to be cleared when
    the profile is invalid. Reserving the same vertical space in every state
    is what stops the results column jumping (docs/frontend.md L1, C5).
    """
    st.markdown(
        f'<div style="padding:.1rem 0 .25rem;">'
        f'<div style="font-size:12px;font-weight:600;color:{MUTED};'
        f'text-transform:uppercase;letter-spacing:.04em;">{html.escape(label)}</div>'
        f'<div style="font-size:40px;font-weight:700;line-height:1.2;'
        f'color:{BORDER};font-family:{MONO};">&mdash;</div></div>',
        unsafe_allow_html=True,
    )


def status_pill(state: str) -> None:
    text, fg, bg, edge = PILL[state]
    st.markdown(
        f'<div style="text-align:right;padding-top:1.6rem;">'
        f'<span style="display:inline-block;padding:.25rem .7rem;'
        f'border:1px solid {edge};background:{bg};color:{fg};'
        f'border-radius:999px;font-size:12px;font-weight:600;'
        f'letter-spacing:.02em;">{html.escape(text)}</span></div>',
        unsafe_allow_html=True,
    )


def result_card(rank: int, result) -> None:
    """
    One role verdict (docs/frontend.md C9-C10).

    Rendered through st.markdown rather than st.html so the reason codes stay
    inside a Markdown element - the UI tests assert those strings verbatim,
    and spec section 9 fixes both their text and their order. Reasons are
    monospace because they are contract tokens, never prose.
    """
    if result.eligible:
        fg, bg, edge, word = SUCCESS, SUCCESS_WASH, SUCCESS_EDGE, "ELIGIBLE"
    else:
        fg, bg, edge, word = DANGER, DANGER_WASH, DANGER_EDGE, "INELIGIBLE"

    reasons = "".join(
        f'<div style="font-family:{MONO};font-size:13px;font-weight:500;'
        f'color:{DANGER};padding:.15rem 0 .15rem .1rem;">{html.escape(code)}</div>'
        for code in result.reasons
    )
    reason_block = (
        f'<div style="margin-top:.6rem;padding-top:.55rem;'
        f'border-top:1px solid {edge};">{reasons}</div>' if reasons else ""
    )

    st.markdown(
        f'<div style="border:1px solid {edge};border-left:4px solid {fg};'
        f'background:{bg};border-radius:8px;padding:.75rem .9rem;'
        f'margin-bottom:.6rem;">'
        f'<div style="display:flex;align-items:baseline;gap:.6rem;'
        f'flex-wrap:wrap;">'
        f'<span style="font-family:{MONO};font-size:13px;color:{MUTED};">'
        f'{rank}</span>'
        f'<span style="font-family:{MONO};font-size:13px;font-weight:500;'
        f'color:{MUTED};">{html.escape(result.role_id)}</span>'
        f'<span style="font-size:16px;font-weight:600;color:{INK};">'
        f'{html.escape(result.title)}</span>'
        f'<span style="margin-left:auto;font-size:11px;font-weight:700;'
        f'letter-spacing:.08em;color:{fg};">{word}</span>'
        f'</div>{reason_block}</div>',
        unsafe_allow_html=True,
    )


def empty_state(message: str) -> None:
    """One component, three messages, identical height (docs/frontend.md C13)."""
    st.markdown(
        f'<div style="border:1px dashed {BORDER};border-radius:8px;'
        f'background:{SURFACE};padding:2.5rem 1rem;text-align:center;'
        f'color:{MUTED};font-size:14px;">{html.escape(message)}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

head_left, head_right = st.columns([3, 1], gap="small")
with head_left:
    st.markdown(
        f'<div style="font-size:28px;font-weight:600;color:{INK};'
        f'letter-spacing:-.02em;line-height:1.25;margin-bottom:.15rem;">'
        f'Career Fair Eligibility Shortlist</div>'
        f'<div style="font-size:14px;color:{MUTED};">'
        f'One profile &middot; five fixed roles &middot; every failed rule reported'
        f'</div>',
        unsafe_allow_html=True,
    )

st.write("")

left, right = st.columns([0.85, 1.6], gap="large")

# ---------------------------------------------------------------------------
# Left column - profile, actions, validation
# ---------------------------------------------------------------------------

with left:
    section_label("Student Profile")
    st.text_input("Branch", key="branch", placeholder="CSE")
    st.text_input("CGPA", key="cgpa", help="Finite number, 0-10 (e.g. 8.1)")
    st.text_input("Graduation Year", key="grad_year", help="Whole number, 2000-2100")
    st.text_input("Active Backlogs", key="backlogs", help="Whole number, 0 or more")
    st.text_area(
        "Skills (comma-separated)",
        key="skills",
        height=80,
        help="Trimmed and compared case-insensitively; blanks and duplicates are dropped.",
    )

    actions = st.columns(3)
    evaluate_clicked = actions[0].button("Evaluate", type="primary", width="stretch")
    if actions[1].button("Load Sample", width="stretch"):
        st.session_state["_pending_action"] = "load_sample"
        st.rerun()
    if actions[2].button("Reset", width="stretch"):
        st.session_state["_pending_action"] = "reset"
        st.rerun()

    profile = _live_profile()

    if evaluate_clicked:
        errors = validate_profile(profile)
        st.session_state["errors"] = errors
        st.session_state["results"] = None if errors else evaluate_all(profile)
        st.session_state["evaluated"] = True
        st.session_state["evaluated_profile"] = profile

    # Derive what to show. Nothing below writes to session state, so a rerun
    # triggered by a keystroke cannot leave the panels contradicting the form.
    if not st.session_state["evaluated"]:
        state, shown_errors, results = "idle", [], None
    elif profile != st.session_state["evaluated_profile"]:
        live_errors = validate_profile(profile)
        state = "invalid" if live_errors else "stale"
        shown_errors, results = live_errors, None
    else:
        shown_errors = st.session_state["errors"]
        state = "invalid" if shown_errors else "valid"
        results = st.session_state["results"]

    # Validation sits directly under the actions: cause and effect adjacent
    # (docs/frontend.md L3).
    st.write("")
    section_label("Validation")
    if state == "idle":
        st.info("Enter a profile and click Evaluate.")
    elif state == "invalid":
        for code in shown_errors:
            st.error(code)
    elif state == "stale":
        # Warning (amber), not info (blue), so the callout matches the amber
        # status pill for this state - docs/frontend.md section 4 assigns the
        # `warning` token to stale.
        st.warning("Profile changed - click Evaluate to refresh the results.")
    else:
        st.success("Profile is valid.")

with head_right:
    status_pill(state)

# ---------------------------------------------------------------------------
# Right column - verdict first, reference data last
# ---------------------------------------------------------------------------

with right:
    # KPI row: always rendered, so the column never jumps (L1). A real
    # st.metric and the markdown placeholder are different element types with
    # different intrinsic heights, so both are pinned inside a fixed-height
    # container - otherwise the whole results column shifts ~24px whenever the
    # state changes, which is the jump L1 exists to remove.
    kpi = st.columns(2)
    for column, label, value in ((kpi[0], "Eligible", 0), (kpi[1], "Ineligible", 1)):
        with column:
            with st.container(height=KPI_HEIGHT, border=False):
                if state == "valid":
                    st.metric(label, counts(results)[value])
                else:
                    kpi_placeholder(label)

    st.write("")
    head = st.columns([1, 1])
    with head[0]:
        section_label("Results")
    with head[1]:
        view = st.segmented_control(
            "Result view",
            options=["Cards", "Table"],
            default="Cards",
            label_visibility="collapsed",
            key="result_view",
        )

    if state == "idle":
        empty_state("No evaluation yet. Click Evaluate to see role verdicts.")
    elif state == "invalid":
        empty_state("No results - fix the validation errors and evaluate again.")
    elif state == "stale":
        empty_state("No results - the profile changed. Click Evaluate to refresh.")
    elif view == "Table":
        # Same RoleResult list as the cards - spec section 14 forbids a second
        # eligibility implementation for an alternative view.
        st.dataframe(
            [
                {
                    "#": rank,
                    "Role ID": r.role_id,
                    "Title": r.title,
                    "Status": "ELIGIBLE" if r.eligible else "INELIGIBLE",
                    "Failure Reasons": " · ".join(r.reasons),
                }
                for rank, r in enumerate(results, start=1)
            ],
            hide_index=True,
            width="stretch",
        )
    else:
        for rank, result in enumerate(results, start=1):
            result_card(rank, result)

    st.write("")
    with st.expander("Role requirements (5 roles)", expanded=True):
        st.dataframe(
            [
                {
                    "Role ID": role.role_id,
                    "Title": role.title,
                    "Allowed Branches": ", ".join(
                        sorted(b.upper() for b in role.allowed_branches)),
                    "Min CGPA": role.min_cgpa,
                    "Allowed Grad Years": ", ".join(
                        str(y) for y in sorted(role.allowed_grad_years)),
                    "Max Backlogs": role.max_backlogs,
                    "Required Skills": ", ".join(role.required_skills),
                }
                for role in ROLES
            ],
            hide_index=True,
            width="stretch",
            column_config={
                # Without an explicit format the grid renders 7.0 as "7", which
                # reads inconsistently next to 7.5 and 8.5 in the same column.
                "Min CGPA": st.column_config.NumberColumn(format="%.1f"),
            },
        )
