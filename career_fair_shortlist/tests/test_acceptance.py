"""
Acceptance-criteria and contract test suite.

Every test here traces to a numbered clause of the problem statement, so a
reviewer can go criterion-by-criterion through the spec and find the assertion
that proves it. Test IDs:

    A1..A7  - Section 12 acceptance criteria
    C1..C8  - Section 6/7/9/10 contracts

This is deliberately a different axis from tests/test_eligibility.py, which
tests the same module unit-by-unit. Some overlap is intentional: the unit suite
answers "does this function work?", this suite answers "does the spec hold?".
"""

import dataclasses

import pytest

import eligibility
from eligibility import (
    ROLES,
    SAMPLE_PROFILE,
    INVALID_BACKLOG_COUNT,
    INVALID_BRANCH,
    INVALID_CGPA,
    INVALID_GRADUATION_YEAR,
    Role,
    StudentProfile,
    counts,
    evaluate_all,
    parse_skills,
    validate_profile,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def profile(**overrides) -> StudentProfile:
    """The built-in profile with individual fields overridden.

    Acceptance criteria are phrased as "change only the CGPA", so the tests
    should express exactly that and nothing more.
    """
    fields = {
        "branch": SAMPLE_PROFILE.branch,
        "cgpa": SAMPLE_PROFILE.cgpa,
        "grad_year": SAMPLE_PROFILE.grad_year,
        "backlogs": SAMPLE_PROFILE.backlogs,
        "skills": SAMPLE_PROFILE.skills,
    }
    fields.update(overrides)
    return StudentProfile(**fields)


def by_id(results) -> dict:
    return {r.role_id: r for r in results}


def order(results) -> list:
    return [r.role_id for r in results]


# ---------------------------------------------------------------------------
# A1 - Built-in profile (Section 12 Test 1, Section 4)
# ---------------------------------------------------------------------------

def test_a1_builtin_profile_is_the_specified_one():
    """Section 2: the built-in profile must match the spec table field-for-field."""
    assert SAMPLE_PROFILE.branch == "CSE"
    assert SAMPLE_PROFILE.cgpa == "8.1"
    assert SAMPLE_PROFILE.grad_year == "2027"
    assert SAMPLE_PROFILE.backlogs == "1"
    assert parse_skills(SAMPLE_PROFILE.skills) == ["Git", "Python", "SQL"]


def test_a1_builtin_profile_is_valid():
    assert validate_profile(SAMPLE_PROFILE) == []


@pytest.mark.parametrize(
    "role_id, expected_eligible",
    [("CF01", True), ("CF02", True), ("CF03", False), ("CF04", False), ("CF05", False)],
)
def test_a1_builtin_statuses(role_id, expected_eligible):
    """CF01, CF02 ELIGIBLE; CF03, CF04, CF05 INELIGIBLE."""
    assert by_id(evaluate_all(SAMPLE_PROFILE))[role_id].eligible is expected_eligible


def test_a1_builtin_counts_are_2_and_3():
    assert counts(evaluate_all(SAMPLE_PROFILE)) == (2, 3)


def test_a1_builtin_display_order():
    """Section 10's worked example: CF01, CF02 then CF03, CF04, CF05."""
    assert order(evaluate_all(SAMPLE_PROFILE)) == ["CF01", "CF02", "CF03", "CF04", "CF05"]


# ---------------------------------------------------------------------------
# A2/A3/A4 - Complete failure reasons (Section 12 Tests 2-4, Section 9)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "role_id, expected_reasons",
    [
        # A2: branch CSE is not in {ECE, EEE} - and nothing else fails.
        ("CF03", ["BRANCH_NOT_ALLOWED"]),
        # A3: 8.1 < 8.5 - and nothing else fails.
        ("CF04", ["CGPA_BELOW_MINIMUM"]),
        # A4: three independent failures, in the Section 9 order.
        (
            "CF05",
            [
                "GRADUATION_YEAR_NOT_ALLOWED",
                "TOO_MANY_ACTIVE_BACKLOGS",
                "MISSING_SKILL: Docker",
            ],
        ),
    ],
)
def test_a2_a3_a4_exact_failure_reasons(role_id, expected_reasons):
    """Exact list equality, not membership.

    `==` is the whole point: it simultaneously proves every failed rule is
    reported (no short-circuit), that none is reported twice, that no rule is
    reported spuriously, and that the order matches Section 9.
    """
    assert by_id(evaluate_all(SAMPLE_PROFILE))[role_id].reasons == expected_reasons


@pytest.mark.parametrize("role_id", ["CF01", "CF02"])
def test_a2_eligible_roles_carry_no_reasons(role_id):
    """Section 9: an eligible role must show no failure reasons."""
    assert by_id(evaluate_all(SAMPLE_PROFILE))[role_id].reasons == []


def test_a4_cf05_failure_is_not_short_circuited():
    """Section 23 names stopping at the first failed rule as an anti-pattern.

    CF05 fails year, backlogs and skills. A short-circuiting implementation
    would report only the first, so reason *count* is the regression guard.
    """
    assert len(by_id(evaluate_all(SAMPLE_PROFILE))["CF05"].reasons) == 3


# ---------------------------------------------------------------------------
# A5 - CGPA 8.5 boundary (Section 12 Test 5)
# ---------------------------------------------------------------------------

def test_a5_cgpa_85_flips_cf04_eligible():
    """CF04's minimum is 8.5 and the rule is >=, so 8.5 must PASS."""
    results = by_id(evaluate_all(profile(cgpa="8.5")))
    assert results["CF04"].eligible is True
    assert results["CF04"].reasons == []


def test_a5_cgpa_85_counts_are_3_and_2():
    assert counts(evaluate_all(profile(cgpa="8.5"))) == (3, 2)


def test_a5_cgpa_85_eligible_group_orders_by_title():
    """Data Operations < Machine Learning < QA Automation.

    This is why the spec picks 8.5: it makes CF04 land *between* CF01 and CF02,
    so ID order and title order disagree. Sorting by role ID would pass A1 but
    fail here.
    """
    results = evaluate_all(profile(cgpa="8.5"))
    assert [r.role_id for r in results if r.eligible] == ["CF01", "CF04", "CF02"]
    assert order(results) == ["CF01", "CF04", "CF02", "CF03", "CF05"]


@pytest.mark.parametrize(
    "cgpa, cf04_eligible",
    [("8.49", False), ("8.5", True), ("8.50", True), ("8.51", True), ("10", True)],
)
def test_a5_boundary_is_inclusive(cgpa, cf04_eligible):
    """Guards against `>` being written where `>=` is required."""
    assert by_id(evaluate_all(profile(cgpa=cgpa)))["CF04"].eligible is cf04_eligible


# ---------------------------------------------------------------------------
# A6 - Invalid CGPA clears everything (Section 12 Test 6, Section 8)
# ---------------------------------------------------------------------------

def test_a6_cgpa_105_reports_invalid_cgpa_only():
    assert validate_profile(profile(cgpa="10.5")) == [INVALID_CGPA]


def test_a6_invalid_cgpa_yields_no_results():
    assert evaluate_all(profile(cgpa="10.5")) is None


def test_a6_invalid_cgpa_clears_both_counts():
    """Section 8: counts must be CLEARED, not zeroed.

    (None, None) and (0, 0) must stay distinguishable - "no evaluation" is a
    different state from "nothing was eligible".
    """
    assert counts(evaluate_all(profile(cgpa="10.5"))) == (None, None)


def test_a6_invalid_input_after_valid_evaluation_discards_prior_results():
    """The stale-state scenario from Section 23, at the logic level."""
    assert evaluate_all(SAMPLE_PROFILE) is not None
    assert evaluate_all(profile(cgpa="10.5")) is None


@pytest.mark.parametrize("cgpa", ["-1", "10.5", "NaN", "Infinity", "-Infinity", "abc", ""])
def test_a6_invalid_cgpa_values(cgpa):
    """Section 7's rejection list, including the float() traps NaN/Infinity."""
    assert INVALID_CGPA in validate_profile(profile(cgpa=cgpa))


@pytest.mark.parametrize("cgpa", ["0", "7.5", "8.1", "10"])
def test_a6_valid_cgpa_boundaries(cgpa):
    assert validate_profile(profile(cgpa=cgpa)) == []


# ---------------------------------------------------------------------------
# A7 - Internal consistency (Section 12 Test 7)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "override",
    [
        {},
        {"cgpa": "8.5"},
        {"branch": "MECH"},
        {"skills": ""},
        {"backlogs": "0", "grad_year": "2026"},
    ],
)
def test_a7_counts_always_agree_with_statuses(override):
    """Counts must be DERIVED from the result set, never tallied separately."""
    results = evaluate_all(profile(**override))
    eligible, ineligible = counts(results)
    assert eligible == sum(1 for r in results if r.eligible)
    assert ineligible == sum(1 for r in results if not r.eligible)
    assert eligible + ineligible == len(ROLES) == 5


@pytest.mark.parametrize(
    "override",
    [{}, {"cgpa": "8.5"}, {"branch": "MECH"}, {"skills": ""}, {"cgpa": "10"}],
)
def test_a7_eligibility_always_matches_reason_emptiness(override):
    """`eligible` must be derived as "no reasons", never stored independently.

    If the two were computed separately they could disagree; this asserts the
    invariant across a spread of profiles.
    """
    for r in evaluate_all(profile(**override)):
        assert r.eligible == (not r.reasons)


def test_a7_every_role_is_reported_exactly_once():
    results = evaluate_all(SAMPLE_PROFILE)
    assert sorted(order(results)) == ["CF01", "CF02", "CF03", "CF04", "CF05"]
    assert len(results) == len(ROLES)


def test_a7_role_titles_in_results_match_the_catalog():
    catalog = {r.role_id: r.title for r in ROLES}
    for r in evaluate_all(SAMPLE_PROFILE):
        assert r.title == catalog[r.role_id]


# ---------------------------------------------------------------------------
# C1 - Ordering contract (Section 10)
# ---------------------------------------------------------------------------

def test_c1_eligible_group_always_precedes_ineligible_group():
    """Status dominates title: an ineligible "Aardvark" still sorts after an
    eligible "Zebra"."""
    fake_roles = (
        Role(
            role_id="CF90",
            title="Aardvark Intern",  # sorts first by title...
            allowed_branches=frozenset({"ece"}),  # ...but is ineligible for CSE
            min_cgpa=0,
            allowed_grad_years=frozenset({2027}),
            max_backlogs=9,
            required_skills=(),
        ),
        Role(
            role_id="CF91",
            title="Zebra Intern",  # sorts last by title...
            allowed_branches=frozenset({"cse"}),  # ...but is eligible
            min_cgpa=0,
            allowed_grad_years=frozenset({2027}),
            max_backlogs=9,
            required_skills=(),
        ),
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(eligibility, "ROLES", fake_roles)
        assert order(evaluate_all(SAMPLE_PROFILE)) == ["CF91", "CF90"]


def test_c1_equal_titles_break_ties_by_ascending_role_id():
    """Section 10 clause 2.

    No two of the five fixed roles share a title, so this branch can NEVER
    execute against production data. Without a synthetic catalog the tie-break
    would ship completely untested.
    """
    fake_roles = (
        Role(
            role_id="CF77",  # declared first, must sort second
            title="Shared Title Intern",
            allowed_branches=frozenset({"cse"}),
            min_cgpa=0,
            allowed_grad_years=frozenset({2027}),
            max_backlogs=9,
            required_skills=(),
        ),
        Role(
            role_id="CF66",  # declared second, must sort first
            title="Shared Title Intern",
            allowed_branches=frozenset({"cse"}),
            min_cgpa=0,
            allowed_grad_years=frozenset({2027}),
            max_backlogs=9,
            required_skills=(),
        ),
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(eligibility, "ROLES", fake_roles)
        assert order(evaluate_all(SAMPLE_PROFILE)) == ["CF66", "CF77"]


def test_c1_title_sort_is_case_insensitive():
    """"apple" must sort before "Banana" - a plain ASCII sort would invert this,
    since uppercase letters precede lowercase ones."""
    fake_roles = (
        Role(
            role_id="CF81",
            title="Banana Intern",
            allowed_branches=frozenset({"cse"}),
            min_cgpa=0,
            allowed_grad_years=frozenset({2027}),
            max_backlogs=9,
            required_skills=(),
        ),
        Role(
            role_id="CF82",
            title="apple Intern",
            allowed_branches=frozenset({"cse"}),
            min_cgpa=0,
            allowed_grad_years=frozenset({2027}),
            max_backlogs=9,
            required_skills=(),
        ),
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(eligibility, "ROLES", fake_roles)
        assert order(evaluate_all(SAMPLE_PROFILE)) == ["CF82", "CF81"]


# ---------------------------------------------------------------------------
# C2 - Missing-skill ordering and naming (Section 9)
# ---------------------------------------------------------------------------

def test_c2_missing_skills_sorted_case_insensitively():
    """Section 9's worked example: Docker, AWS, GitHub Actions -> A, D, G."""
    fake_roles = (
        Role(
            role_id="CF95",
            title="Skill Heavy Intern",
            allowed_branches=frozenset({"cse"}),
            min_cgpa=0,
            allowed_grad_years=frozenset({2027}),
            max_backlogs=9,
            required_skills=("Docker", "AWS", "GitHub Actions"),
        ),
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(eligibility, "ROLES", fake_roles)
        results = evaluate_all(profile(skills=""))
    assert results[0].reasons == [
        "MISSING_SKILL: AWS",
        "MISSING_SKILL: Docker",
        "MISSING_SKILL: GitHub Actions",
    ]


def test_c2_missing_skill_uses_the_roles_declared_spelling():
    """Section 4 expects literally "MISSING_SKILL: Docker".

    The student never typed "Docker" at all, so the reason text must come from
    the role definition, not from user input.
    """
    results = by_id(evaluate_all(profile(skills="git, python, sql")))
    assert "MISSING_SKILL: Docker" in results["CF05"].reasons


def test_c2_empty_skill_list_reports_every_required_skill():
    results = by_id(evaluate_all(profile(skills="")))
    assert results["CF01"].reasons == ["MISSING_SKILL: Python", "MISSING_SKILL: SQL"]
    assert "MISSING_SKILL: Git" in results["CF02"].reasons


def test_c2_each_missing_skill_reported_exactly_once():
    """Section 9: "list every failed rule exactly once"."""
    reasons = by_id(evaluate_all(profile(skills="Git, git, GIT")))["CF01"].reasons
    assert reasons.count("MISSING_SKILL: Python") == 1
    assert reasons.count("MISSING_SKILL: SQL") == 1


# ---------------------------------------------------------------------------
# C3 - Case-insensitive comparison (Section 6)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("branch", ["CSE", "cse", "Cse", "cSe", " CSE ", "  cse  "])
def test_c3_branch_compared_case_insensitively_after_trimming(branch):
    assert by_id(evaluate_all(profile(branch=branch)))["CF01"].eligible is True


@pytest.mark.parametrize(
    "skills",
    [
        "Git, Python, SQL",
        "git, python, sql",
        "GIT, PYTHON, SQL",
        " Git , Python , SQL ",
        "gIt,pYtHoN,sQl",
    ],
)
def test_c3_skills_compared_case_insensitively_after_trimming(skills):
    assert by_id(evaluate_all(profile(skills=skills)))["CF01"].eligible is True


def test_c3_no_alias_or_similar_skill_inference():
    """Section 6: "Python" and "PyTorch" must remain different skills.

    Guards against anyone "improving" matching with a prefix or fuzzy check.
    """
    results = by_id(evaluate_all(profile(cgpa="8.5", skills="Git, PyTorch, SQL")))
    assert results["CF04"].eligible is False
    assert "MISSING_SKILL: Python" in results["CF04"].reasons


def test_c3_no_branch_alias_inference():
    """"Computer Science" must not be inferred to mean "CSE"."""
    results = by_id(evaluate_all(profile(branch="Computer Science")))
    assert results["CF01"].eligible is False
    assert "BRANCH_NOT_ALLOWED" in results["CF01"].reasons


# ---------------------------------------------------------------------------
# C4 - Whitespace and duplicate skills (Section 6)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Git, Python, SQL", ["Git", "Python", "SQL"]),
        ("Git,, Python, ,SQL", ["Git", "Python", "SQL"]),        # empty pieces
        ("  Git  ,  Python  ,  SQL  ", ["Git", "Python", "SQL"]),  # padding
        ("Git, Python, Git, SQL", ["Git", "Python", "SQL"]),       # duplicates
        ("git, Git, GIT", ["git"]),                                # case-insensitive dupes
        (",,,", []),                                               # commas only
        ("", []),
        ("   ", []),
        ("Git", ["Git"]),                                          # no comma at all
        (",Git,", ["Git"]),                                        # leading/trailing comma
    ],
)
def test_c4_skill_parsing(raw, expected):
    assert parse_skills(raw) == expected


def test_c4_messy_skill_input_still_evaluates_correctly():
    """End-to-end: padding, empty pieces, duplicates and mixed case at once."""
    results = by_id(evaluate_all(profile(skills=" Git ,, python,  GIT , sql ,Python, ")))
    assert results["CF01"].eligible is True
    assert results["CF02"].eligible is True
    assert counts(evaluate_all(profile(skills=" Git ,, python,  GIT , sql ,Python, "))) == (2, 3)


def test_c4_skills_have_no_validation_rule():
    """Section 7 defines no INVALID_SKILLS code - empty skills is a VALID
    profile that simply fails skill-gated roles."""
    assert validate_profile(profile(skills="")) == []
    assert evaluate_all(profile(skills="")) is not None


# ---------------------------------------------------------------------------
# C5 - Validation contracts (Section 7)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("branch", ["", " ", "   ", "\t"])
def test_c5_blank_branch_is_invalid(branch):
    assert INVALID_BRANCH in validate_profile(profile(branch=branch))


@pytest.mark.parametrize("year", ["1999", "2101", "2027.5", "abc", ""])
def test_c5_invalid_graduation_years(year):
    assert INVALID_GRADUATION_YEAR in validate_profile(profile(grad_year=year))


@pytest.mark.parametrize("year", ["2000", "2027", "2100"])
def test_c5_valid_graduation_year_boundaries(year):
    assert validate_profile(profile(grad_year=year)) == []


@pytest.mark.parametrize("backlogs", ["-1", "1.5", "abc", ""])
def test_c5_invalid_backlog_counts(backlogs):
    assert INVALID_BACKLOG_COUNT in validate_profile(profile(backlogs=backlogs))


@pytest.mark.parametrize("backlogs", ["0", "1", "5", "99"])
def test_c5_valid_backlog_counts(backlogs):
    assert validate_profile(profile(backlogs=backlogs)) == []


def test_c5_all_fields_validated_independently():
    """Validation must not short-circuit on the first bad field."""
    errors = validate_profile(
        StudentProfile(branch="", cgpa="abc", grad_year="1999", backlogs="-1", skills="Git")
    )
    assert errors == [
        INVALID_BRANCH,
        INVALID_CGPA,
        INVALID_GRADUATION_YEAR,
        INVALID_BACKLOG_COUNT,
    ]


@pytest.mark.parametrize(
    "override",
    [{"branch": ""}, {"cgpa": "10.5"}, {"grad_year": "1999"}, {"backlogs": "-1"}],
)
def test_c5_any_invalid_field_blocks_evaluation(override):
    """Section 8: validation is a gate - one bad field suppresses everything."""
    assert evaluate_all(profile(**override)) is None
    assert counts(evaluate_all(profile(**override))) == (None, None)


# ---------------------------------------------------------------------------
# C6 - Validity is not eligibility (Section 7 vs Section 5)
# ---------------------------------------------------------------------------

def test_c6_valid_but_disallowed_graduation_year():
    """2099 is inside 2000-2100, so it is VALID input. No role allows it, so it
    is an ELIGIBILITY failure - GRADUATION_YEAR_NOT_ALLOWED, not
    INVALID_GRADUATION_YEAR."""
    assert validate_profile(profile(grad_year="2099")) == []
    results = evaluate_all(profile(grad_year="2099"))
    assert counts(results) == (0, 5)
    for r in results:
        assert "GRADUATION_YEAR_NOT_ALLOWED" in r.reasons


def test_c6_non_blank_unknown_branch_is_valid_input():
    """Only a BLANK branch is invalid (Section 7). "MECH" is well-formed input
    that simply matches no role's allowed set."""
    assert validate_profile(profile(branch="MECH")) == []
    results = evaluate_all(profile(branch="MECH"))
    assert counts(results) == (0, 5)
    for r in results:
        assert "BRANCH_NOT_ALLOWED" in r.reasons


def test_c6_zero_eligible_is_a_real_result_not_a_cleared_one():
    """(0, 5) must be distinguishable from the (None, None) of invalid input."""
    assert counts(evaluate_all(profile(branch="MECH"))) == (0, 5)
    assert counts(evaluate_all(profile(cgpa="10.5"))) == (None, None)


# ---------------------------------------------------------------------------
# C7 - Fixed role catalog (Section 3)
# ---------------------------------------------------------------------------

def test_c7_catalog_matches_the_spec_table():
    expected = {
        "CF01": ("Data Operations Intern", {"cse", "it"}, 7.5, {2027}, 1, ("Python", "SQL")),
        "CF02": ("QA Automation Intern", {"cse", "ece", "it"}, 7.0, {2027, 2028}, 1, ("Git",)),
        "CF03": ("Embedded Systems Intern", {"ece", "eee"}, 7.5, {2027}, 1, ("Git",)),
        "CF04": ("Machine Learning Intern", {"cse", "it"}, 8.5, {2027}, 1, ("Python",)),
        "CF05": ("Platform Engineering Intern", {"cse", "ece"}, 7.0, {2026}, 0, ("Docker", "Git")),
    }
    assert len(ROLES) == 5
    for role in ROLES:
        title, branches, min_cgpa, years, max_backlogs, skills = expected[role.role_id]
        assert role.title == title
        assert set(role.allowed_branches) == branches
        assert role.min_cgpa == min_cgpa
        assert set(role.allowed_grad_years) == years
        assert role.max_backlogs == max_backlogs
        assert role.required_skills == skills


def test_c7_role_records_are_immutable():
    """Section 19: role data must not change during evaluation."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        ROLES[0].min_cgpa = 0.0


# ---------------------------------------------------------------------------
# C8 - Determinism (Section 19)
# ---------------------------------------------------------------------------

def test_c8_repeated_evaluation_is_identical():
    """No clock, no randomness, no I/O - same input, same output, always."""
    first = evaluate_all(SAMPLE_PROFILE)
    second = evaluate_all(SAMPLE_PROFILE)
    assert order(first) == order(second)
    assert [r.reasons for r in first] == [r.reasons for r in second]


def test_c8_evaluation_does_not_mutate_the_input_profile():
    p = profile()
    before = (p.branch, p.cgpa, p.grad_year, p.backlogs, p.skills)
    evaluate_all(p)
    assert (p.branch, p.cgpa, p.grad_year, p.backlogs, p.skills) == before
