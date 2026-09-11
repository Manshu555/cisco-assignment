"""
Headless UI smoke tests for app.py using Streamlit's AppTest harness.

These run the actual Streamlit script (no browser needed) and simulate
button clicks / text input, verifying the UI stays in sync with the
eligibility logic (Section 7 of the acceptance criteria: data sync).
"""

import re
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


def _run():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=15)  # first run compiles/imports the script; allow extra time
    assert not at.exception
    return at


def test_app_loads_without_exception():
    _run()


def test_evaluate_builtin_profile_shows_expected_counts():
    at = _run()

    evaluate_btn = [b for b in at.button if b.label == "Evaluate"][0]
    evaluate_btn.click().run()
    assert not at.exception

    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Eligible"] == "2"
    assert metrics["Ineligible"] == "3"


def test_invalid_cgpa_clears_results_in_ui():
    at = _run()
    cgpa_input = [t for t in at.text_input if t.label == "CGPA"][0]
    cgpa_input.set_value("10.5").run()

    evaluate_btn = [b for b in at.button if b.label == "Evaluate"][0]
    evaluate_btn.click().run()
    assert not at.exception

    # No metrics should be rendered once validation fails.
    assert len(at.metric) == 0
    # Validation error should be visible.
    error_bodies = [e.value for e in at.error]
    assert any("INVALID_CGPA" in body for body in error_bodies)


def test_reset_restores_builtin_profile_after_edit():
    at = _run()
    branch_input = [t for t in at.text_input if t.label == "Branch"][0]
    branch_input.set_value("ECE").run()

    reset_btn = [b for b in at.button if b.label == "Reset"][0]
    reset_btn.click().run()
    assert not at.exception

    branch_input_after = [t for t in at.text_input if t.label == "Branch"][0]
    assert branch_input_after.value == "CSE"


def _btn(at, label):
    return [b for b in at.button if b.label == label][0]


def _input(at, label):
    return [t for t in at.text_input if t.label == label][0]


def test_invalid_edit_clears_results_before_evaluate_is_pressed():
    """Spec sections 8 and 23: an invalid field must never leave stale results
    on screen, even if the user has not pressed Evaluate again."""
    at = _run()
    _btn(at, "Evaluate").click().run()
    assert len(at.metric) == 2

    _input(at, "CGPA").set_value("10.5").run()
    assert not at.exception
    assert len(at.metric) == 0
    assert [e.value for e in at.error] == ["INVALID_CGPA"]


def test_editing_to_a_new_valid_value_withholds_results_until_evaluate():
    """A changed-but-valid profile must not keep showing the previous results,
    and must not claim the stale results describe the new profile."""
    at = _run()
    _btn(at, "Evaluate").click().run()

    _input(at, "CGPA").set_value("8.5").run()
    assert len(at.metric) == 0
    assert [e.value for e in at.error] == []

    _btn(at, "Evaluate").click().run()
    metrics = {m.label: m.value for m in at.metric}
    assert metrics == {"Eligible": "3", "Ineligible": "2"}


def test_reverting_an_edit_restores_the_matching_results():
    """Returning the form to the evaluated profile shows its results again
    rather than a lingering error from the intermediate invalid value."""
    at = _run()
    _btn(at, "Evaluate").click().run()

    _input(at, "CGPA").set_value("10.5").run()
    assert [e.value for e in at.error] == ["INVALID_CGPA"]

    _input(at, "CGPA").set_value("8.1").run()
    assert [e.value for e in at.error] == []
    metrics = {m.label: m.value for m in at.metric}
    assert metrics == {"Eligible": "2", "Ineligible": "3"}


def test_load_sample_recovers_from_an_invalid_profile():
    at = _run()
    _input(at, "CGPA").set_value("10.5").run()
    _btn(at, "Evaluate").click().run()
    assert [e.value for e in at.error] == ["INVALID_CGPA"]

    _btn(at, "Load Sample").click().run()
    assert not at.exception
    assert _input(at, "CGPA").value == "8.1"
    assert [e.value for e in at.error] == []
    assert len(at.metric) == 0


def _result_cards(at):
    """
    The rendered role cards, in document order, as (role_id, status, reasons).

    Cards are markdown elements carrying inline styles (see app.py
    result_card); the coloured left edge is what distinguishes them from other
    markdown on the page. Tags are stripped so the assertions below check the
    text a user actually reads.
    """
    cards = [m.value for m in at.markdown if "border-left:4px" in m.value]
    parsed = []
    for card in cards:
        lines = [line.strip() for line in re.sub(r"<[^>]+>", "\n", card).split("\n")]
        lines = [line for line in lines if line]
        role_id = next(line for line in lines if re.fullmatch(r"CF\d+", line))
        status = next(line for line in lines if line in ("ELIGIBLE", "INELIGIBLE"))
        reasons = [line for line in lines
                   if line.split(":")[0] in REASON_CODES and line != status]
        parsed.append((role_id, status, reasons))
    return parsed


REASON_CODES = {
    "BRANCH_NOT_ALLOWED", "CGPA_BELOW_MINIMUM", "GRADUATION_YEAR_NOT_ALLOWED",
    "TOO_MANY_ACTIVE_BACKLOGS", "MISSING_SKILL",
}


def test_builtin_results_render_in_spec_order_with_reasons():
    """Spec sections 4, 9 and 10: role order, status, and the exact reason
    strings in their required order, per card."""
    at = _run()
    _btn(at, "Evaluate").click().run()

    assert _result_cards(at) == [
        ("CF01", "ELIGIBLE", []),
        ("CF02", "ELIGIBLE", []),
        ("CF03", "INELIGIBLE", ["BRANCH_NOT_ALLOWED"]),
        ("CF04", "INELIGIBLE", ["CGPA_BELOW_MINIMUM"]),
        ("CF05", "INELIGIBLE", ["GRADUATION_YEAR_NOT_ALLOWED",
                                "TOO_MANY_ACTIVE_BACKLOGS",
                                "MISSING_SKILL: Docker"]),
    ]


def test_cgpa_boundary_reorders_cards_by_title():
    """Spec Test 5: at 8.5 the eligible group is title-sorted, not ID-sorted."""
    at = _run()
    _input(at, "CGPA").set_value("8.5").run()
    _btn(at, "Evaluate").click().run()

    cards = _result_cards(at)
    assert [role_id for role_id, _, _ in cards] == ["CF01", "CF04", "CF02", "CF03", "CF05"]
    assert [status for _, status, _ in cards[:3]] == ["ELIGIBLE"] * 3


def test_table_view_renders_the_same_results_as_the_cards():
    """Spec section 14: the alternative view must be driven by the same
    results, never by a second eligibility implementation."""
    at = _run()
    _btn(at, "Evaluate").click().run()
    at.segmented_control[0].set_value("Table").run()
    assert not at.exception

    table = at.dataframe[0].value
    assert list(table["Role ID"]) == ["CF01", "CF02", "CF03", "CF04", "CF05"]
    assert list(table["Status"]) == ["ELIGIBLE", "ELIGIBLE",
                                     "INELIGIBLE", "INELIGIBLE", "INELIGIBLE"]
    assert table["Failure Reasons"].iloc[4] == (
        "GRADUATION_YEAR_NOT_ALLOWED · TOO_MANY_ACTIVE_BACKLOGS · MISSING_SKILL: Docker"
    )


def test_counts_placeholder_reserves_space_without_rendering_metrics():
    """docs/frontend.md C5: the KPI row is always present so the column does
    not jump, but real st.metric elements appear only in the valid state."""
    at = _run()
    assert len(at.metric) == 0
    placeholders = [m.value for m in at.markdown if "&mdash;" in m.value]
    assert len(placeholders) == 2

    _btn(at, "Evaluate").click().run()
    assert len(at.metric) == 2
    assert [m.value for m in at.markdown if "&mdash;" in m.value] == []


def test_status_pill_tracks_the_four_states():
    at = _run()

    def pill():
        for m in at.markdown:
            for label in ("Ready", "Evaluated", "Needs re-evaluation", "Invalid profile"):
                if "border-radius:999px" in m.value and label in m.value:
                    return label
        return None

    assert pill() == "Ready"
    _btn(at, "Evaluate").click().run()
    assert pill() == "Evaluated"
    _input(at, "CGPA").set_value("10.5").run()
    assert pill() == "Invalid profile"
    _input(at, "CGPA").set_value("8.5").run()
    assert pill() == "Needs re-evaluation"


def test_role_requirements_table_lists_all_five_roles():
    at = _run()
    table = at.dataframe[0].value
    assert list(table["Role ID"]) == ["CF01", "CF02", "CF03", "CF04", "CF05"]
