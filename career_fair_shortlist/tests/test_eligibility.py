"""
Focused test suite for the Career Fair Eligibility Shortlist.

Covers Section 12 (Acceptance Criteria) and Section 13 (Focused Test Plan)
of the problem statement.
"""

from eligibility import (
    ROLES,
    SAMPLE_PROFILE,
    StudentProfile,
    evaluate_all,
    counts,
    parse_skills,
    validate_profile,
    INVALID_BRANCH,
    INVALID_CGPA,
    INVALID_GRADUATION_YEAR,
    INVALID_BACKLOG_COUNT,
)


# ---------------------------------------------------------------------------
# Test 1 / built-in result
# ---------------------------------------------------------------------------

def test_builtin_profile_has_five_roles():
    assert len(ROLES) == 5
    assert [r.role_id for r in ROLES] == ["CF01", "CF02", "CF03", "CF04", "CF05"]


def test_builtin_result_statuses():
    results = evaluate_all(SAMPLE_PROFILE)
    status = {r.role_id: r.eligible for r in results}
    assert status["CF01"] is True
    assert status["CF02"] is True
    assert status["CF03"] is False
    assert status["CF04"] is False
    assert status["CF05"] is False


def test_builtin_counts():
    results = evaluate_all(SAMPLE_PROFILE)
    eligible, ineligible = counts(results)
    assert eligible == 2
    assert ineligible == 3


# ---------------------------------------------------------------------------
# Test 2/3/4 - exact failure reasons per role
# ---------------------------------------------------------------------------

def test_cf03_only_branch_not_allowed():
    results = evaluate_all(SAMPLE_PROFILE)
    cf03 = next(r for r in results if r.role_id == "CF03")
    assert cf03.reasons == ["BRANCH_NOT_ALLOWED"]


def test_cf04_only_cgpa_below_minimum():
    results = evaluate_all(SAMPLE_PROFILE)
    cf04 = next(r for r in results if r.role_id == "CF04")
    assert cf04.reasons == ["CGPA_BELOW_MINIMUM"]


def test_cf05_complete_failure_reasons_in_order():
    results = evaluate_all(SAMPLE_PROFILE)
    cf05 = next(r for r in results if r.role_id == "CF05")
    assert cf05.reasons == [
        "GRADUATION_YEAR_NOT_ALLOWED",
        "TOO_MANY_ACTIVE_BACKLOGS",
        "MISSING_SKILL: Docker",
    ]


def test_eligible_role_has_no_reasons():
    results = evaluate_all(SAMPLE_PROFILE)
    cf01 = next(r for r in results if r.role_id == "CF01")
    assert cf01.reasons == []


# ---------------------------------------------------------------------------
# Test 5 - CGPA boundary (8.1 -> 8.5 makes CF04 eligible)
# ---------------------------------------------------------------------------

def test_cgpa_boundary_makes_cf04_eligible():
    profile = StudentProfile(
        branch="CSE", cgpa="8.5", grad_year="2027", backlogs="1",
        skills="Git, Python, SQL",
    )
    results = evaluate_all(profile)
    status = {r.role_id: r.eligible for r in results}
    assert status["CF01"] is True
    assert status["CF02"] is True
    assert status["CF04"] is True
    assert status["CF03"] is False
    assert status["CF05"] is False

    eligible, ineligible = counts(results)
    assert eligible == 3
    assert ineligible == 2

    eligible_ids_in_order = [r.role_id for r in results if r.eligible]
    assert eligible_ids_in_order == ["CF01", "CF04", "CF02"]


# ---------------------------------------------------------------------------
# Test 6 - invalid CGPA clears results
# ---------------------------------------------------------------------------

def test_invalid_cgpa_returns_none():
    profile = StudentProfile(
        branch="CSE", cgpa="10.5", grad_year="2027", backlogs="1",
        skills="Git, Python, SQL",
    )
    assert evaluate_all(profile) is None
    eligible, ineligible = counts(evaluate_all(profile))
    assert eligible is None
    assert ineligible is None


# ---------------------------------------------------------------------------
# Branch validation
# ---------------------------------------------------------------------------

def test_blank_branch_is_invalid():
    profile = StudentProfile(branch="   ", cgpa="8.1", grad_year="2027", backlogs="1", skills="Git")
    assert INVALID_BRANCH in validate_profile(profile)


# ---------------------------------------------------------------------------
# CGPA validation
# ---------------------------------------------------------------------------

def test_cgpa_valid_boundaries():
    for value in ["0", "7.5", "8.1", "10"]:
        profile = StudentProfile(branch="CSE", cgpa=value, grad_year="2027", backlogs="1", skills="Git")
        assert validate_profile(profile) == []


def test_cgpa_invalid_values():
    for value in ["-1", "10.5", "NaN", "Infinity", "-Infinity", "abc", ""]:
        profile = StudentProfile(branch="CSE", cgpa=value, grad_year="2027", backlogs="1", skills="Git")
        assert INVALID_CGPA in validate_profile(profile), f"expected INVALID_CGPA for {value!r}"


# ---------------------------------------------------------------------------
# Graduation year validation
# ---------------------------------------------------------------------------

def test_graduation_year_valid_boundaries():
    for value in ["2000", "2027", "2100"]:
        profile = StudentProfile(branch="CSE", cgpa="8.1", grad_year=value, backlogs="1", skills="Git")
        assert validate_profile(profile) == []


def test_graduation_year_invalid_values():
    for value in ["1999", "2101", "2027.5", "abc", ""]:
        profile = StudentProfile(branch="CSE", cgpa="8.1", grad_year=value, backlogs="1", skills="Git")
        assert INVALID_GRADUATION_YEAR in validate_profile(profile), f"expected error for {value!r}"


def test_disallowed_but_valid_graduation_year_is_not_a_validation_error():
    # 2099 is a *valid* year (within 2000-2100) even though no role allows it;
    # that is an eligibility failure (GRADUATION_YEAR_NOT_ALLOWED), not a
    # validation error.
    profile = StudentProfile(branch="CSE", cgpa="8.1", grad_year="2099", backlogs="1", skills="Git, Python, SQL")
    assert validate_profile(profile) == []
    results = evaluate_all(profile)
    cf01 = next(r for r in results if r.role_id == "CF01")
    assert "GRADUATION_YEAR_NOT_ALLOWED" in cf01.reasons


# ---------------------------------------------------------------------------
# Backlog validation
# ---------------------------------------------------------------------------

def test_backlog_valid_values():
    for value in ["0", "1", "5"]:
        profile = StudentProfile(branch="CSE", cgpa="8.1", grad_year="2027", backlogs=value, skills="Git")
        assert validate_profile(profile) == []


def test_backlog_invalid_values():
    for value in ["-1", "1.5", "abc", ""]:
        profile = StudentProfile(branch="CSE", cgpa="8.1", grad_year="2027", backlogs=value, skills="Git")
        assert INVALID_BACKLOG_COUNT in validate_profile(profile), f"expected error for {value!r}"


# ---------------------------------------------------------------------------
# Skill parsing (Section 6)
# ---------------------------------------------------------------------------

def test_parse_skills_trims_and_ignores_empty_pieces():
    assert parse_skills("Git,, Python, ,SQL") == ["Git", "Python", "SQL"]


def test_parse_skills_collapses_duplicates_case_insensitively():
    assert parse_skills("Git, Python, Git, SQL") == ["Git", "Python", "SQL"]
    assert parse_skills("git, Git, GIT") == ["git"]


def test_parse_skills_empty_string():
    assert parse_skills("") == []
    assert parse_skills("   ") == []


# ---------------------------------------------------------------------------
# Case-insensitive comparison
# ---------------------------------------------------------------------------

def test_branch_comparison_is_case_insensitive_and_trimmed():
    profile = StudentProfile(branch=" cse ", cgpa="8.1", grad_year="2027", backlogs="1", skills="Git, Python, SQL")
    results = evaluate_all(profile)
    cf01 = next(r for r in results if r.role_id == "CF01")
    assert cf01.eligible is True


def test_skill_comparison_is_case_insensitive_and_trimmed():
    profile = StudentProfile(branch="CSE", cgpa="8.1", grad_year="2027", backlogs="1", skills=" python , SQL, GIT ")
    results = evaluate_all(profile)
    cf01 = next(r for r in results if r.role_id == "CF01")
    assert cf01.eligible is True


def test_similar_skill_is_not_treated_as_match():
    # "PyTorch" must not satisfy a "Python" requirement.
    profile = StudentProfile(branch="CSE", cgpa="8.5", grad_year="2027", backlogs="1", skills="Git, PyTorch, SQL")
    results = evaluate_all(profile)
    cf04 = next(r for r in results if r.role_id == "CF04")
    assert cf04.eligible is False
    assert "MISSING_SKILL: Python" in cf04.reasons


# ---------------------------------------------------------------------------
# Missing-skill ordering
# ---------------------------------------------------------------------------

def test_missing_skills_sorted_case_insensitively():
    from eligibility import Role, evaluate_role

    role = Role(
        role_id="X",
        title="Test Role",
        allowed_branches=frozenset({"cse"}),
        min_cgpa=0,
        allowed_grad_years=frozenset({2027}),
        max_backlogs=5,
        required_skills=("Docker", "AWS", "GitHub Actions"),
    )
    result = evaluate_role(role, "CSE", 9.0, 2027, 0, [])
    assert result.reasons == [
        "MISSING_SKILL: AWS",
        "MISSING_SKILL: Docker",
        "MISSING_SKILL: GitHub Actions",
    ]


# ---------------------------------------------------------------------------
# Role ordering / title sorting
# ---------------------------------------------------------------------------

def test_builtin_result_ordering():
    results = evaluate_all(SAMPLE_PROFILE)
    assert [r.role_id for r in results] == ["CF01", "CF02", "CF03", "CF04", "CF05"]


# ---------------------------------------------------------------------------
# Reset / sample behaviour (logic-level: reloading sample gives builtin result)
# ---------------------------------------------------------------------------

def test_sample_profile_matches_spec_values():
    assert SAMPLE_PROFILE.branch == "CSE"
    assert SAMPLE_PROFILE.cgpa == "8.1"
    assert SAMPLE_PROFILE.grad_year == "2027"
    assert SAMPLE_PROFILE.backlogs == "1"
    assert parse_skills(SAMPLE_PROFILE.skills) == ["Git", "Python", "SQL"]


# ---------------------------------------------------------------------------
# Stale state: invalid profile clears results
# ---------------------------------------------------------------------------

def test_invalid_profile_after_valid_one_returns_none():
    valid = evaluate_all(SAMPLE_PROFILE)
    assert valid is not None

    invalid_profile = StudentProfile(branch="", cgpa="8.1", grad_year="2027", backlogs="1", skills="Git")
    assert evaluate_all(invalid_profile) is None
