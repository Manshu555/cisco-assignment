"""
Career Fair Eligibility Shortlist - pure domain logic.

No UI imports here on purpose. This module is evaluated independently
of Streamlit/CLI so it can be unit tested in isolation and reused by
any front end without duplicating the eligibility rules.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Role:
    role_id: str
    title: str
    allowed_branches: frozenset  # normalized (casefolded) branch names
    min_cgpa: float
    allowed_grad_years: frozenset  # ints
    max_backlogs: int
    required_skills: tuple  # original-cased skill names, in spec order


@dataclass
class StudentProfile:
    branch: str = ""
    cgpa: str = ""
    grad_year: str = ""
    backlogs: str = ""
    skills: str = ""


@dataclass
class RoleResult:
    role_id: str
    title: str
    eligible: bool
    reasons: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Fixed local role data (Section 3 of the spec)
# ---------------------------------------------------------------------------

ROLES: tuple = (
    Role(
        role_id="CF01",
        title="Data Operations Intern",
        allowed_branches=frozenset({"cse", "it"}),
        min_cgpa=7.5,
        allowed_grad_years=frozenset({2027}),
        max_backlogs=1,
        required_skills=("Python", "SQL"),
    ),
    Role(
        role_id="CF02",
        title="QA Automation Intern",
        allowed_branches=frozenset({"cse", "ece", "it"}),
        min_cgpa=7.0,
        allowed_grad_years=frozenset({2027, 2028}),
        max_backlogs=1,
        required_skills=("Git",),
    ),
    Role(
        role_id="CF03",
        title="Embedded Systems Intern",
        allowed_branches=frozenset({"ece", "eee"}),
        min_cgpa=7.5,
        allowed_grad_years=frozenset({2027}),
        max_backlogs=1,
        required_skills=("Git",),
    ),
    Role(
        role_id="CF04",
        title="Machine Learning Intern",
        allowed_branches=frozenset({"cse", "it"}),
        min_cgpa=8.5,
        allowed_grad_years=frozenset({2027}),
        max_backlogs=1,
        required_skills=("Python",),
    ),
    Role(
        role_id="CF05",
        title="Platform Engineering Intern",
        allowed_branches=frozenset({"cse", "ece"}),
        min_cgpa=7.0,
        allowed_grad_years=frozenset({2026}),
        max_backlogs=0,
        required_skills=("Docker", "Git"),
    ),
)

# Built-in sample student profile (Section 2 of the spec)
SAMPLE_PROFILE = StudentProfile(
    branch="CSE",
    cgpa="8.1",
    grad_year="2027",
    backlogs="1",
    skills="Git, Python, SQL",
)


# ---------------------------------------------------------------------------
# Normalization (Section 6)
# ---------------------------------------------------------------------------

def normalize_token(value: str) -> str:
    """Trim and casefold a single branch/skill token for comparison."""
    return value.strip().casefold()


def parse_skills(raw: str) -> list:
    """
    Split a comma-separated skill string into a clean, de-duplicated list.

    - Trims whitespace from each piece.
    - Drops empty pieces (from stray/leading/trailing commas).
    - Collapses duplicates (case-insensitively) while keeping the first
      original-cased spelling encountered, and preserving first-seen order.
    """
    seen = set()
    result = []
    for piece in raw.split(","):
        cleaned = piece.strip()
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
    return result


# ---------------------------------------------------------------------------
# Validation (Section 7)
# ---------------------------------------------------------------------------

# Validation error codes, in a fixed field order for deterministic display.
INVALID_BRANCH = "INVALID_BRANCH"
INVALID_CGPA = "INVALID_CGPA"
INVALID_GRADUATION_YEAR = "INVALID_GRADUATION_YEAR"
INVALID_BACKLOG_COUNT = "INVALID_BACKLOG_COUNT"


def _parse_finite_float(raw: str) -> Optional[float]:
    """Return a finite float, or None if raw is not a finite number."""
    try:
        value = float(raw.strip())
    except (ValueError, AttributeError):
        return None
    if not math.isfinite(value):
        return None
    return value


def _parse_whole_number(raw: str) -> Optional[int]:
    """Return an int if raw is a whole number (e.g. '5', '5.0'), else None."""
    try:
        value = float(raw.strip())
    except (ValueError, AttributeError):
        return None
    if not math.isfinite(value):
        return None
    if value != math.floor(value):
        return None
    return int(value)


def validate_profile(profile: StudentProfile) -> list:
    """
    Validate a raw (string-based) student profile.

    Returns a list of validation error codes (empty list means valid).
    Every field is checked independently so all problems can be reported.
    """
    errors = []

    if not profile.branch.strip():
        errors.append(INVALID_BRANCH)

    cgpa = _parse_finite_float(profile.cgpa)
    if cgpa is None or cgpa < 0 or cgpa > 10:
        errors.append(INVALID_CGPA)

    grad_year = _parse_whole_number(profile.grad_year)
    if grad_year is None or grad_year < 2000 or grad_year > 2100:
        errors.append(INVALID_GRADUATION_YEAR)

    backlogs = _parse_whole_number(profile.backlogs)
    if backlogs is None or backlogs < 0:
        errors.append(INVALID_BACKLOG_COUNT)

    return errors


# ---------------------------------------------------------------------------
# Eligibility evaluation (Sections 5, 9, 10)
# ---------------------------------------------------------------------------

def evaluate_role(role: Role, branch: str, cgpa: float, grad_year: int,
                   backlogs: int, skills: list) -> RoleResult:
    """
    Evaluate a single role against an already-validated, normalized profile.

    Every rule is checked independently (no short-circuiting) so that an
    ineligible role reports *every* failed rule, not just the first one.
    Reasons are appended in the exact required order (Section 9).
    """
    reasons = []

    if normalize_token(branch) not in role.allowed_branches:
        reasons.append("BRANCH_NOT_ALLOWED")

    if cgpa < role.min_cgpa:
        reasons.append("CGPA_BELOW_MINIMUM")

    if grad_year not in role.allowed_grad_years:
        reasons.append("GRADUATION_YEAR_NOT_ALLOWED")

    if backlogs > role.max_backlogs:
        reasons.append("TOO_MANY_ACTIVE_BACKLOGS")

    student_skill_keys = {normalize_token(s) for s in skills}
    missing = [
        skill for skill in role.required_skills
        if normalize_token(skill) not in student_skill_keys
    ]
    missing.sort(key=str.casefold)
    for skill in missing:
        reasons.append(f"MISSING_SKILL: {skill}")

    return RoleResult(
        role_id=role.role_id,
        title=role.title,
        eligible=not reasons,
        reasons=reasons,
    )


def evaluate_all(profile: StudentProfile) -> Optional[list]:
    """
    Validate and evaluate the profile against all fixed roles.

    Returns None if the profile is invalid (caller should show validation
    errors and clear any stale results). Otherwise returns a list of
    RoleResult in the required display order:
      1. Eligible roles before ineligible roles.
      2. Within each group, ascending by title (case-insensitive).
      3. Ties broken by ascending role_id.
    """
    if validate_profile(profile):
        return None

    cgpa = _parse_finite_float(profile.cgpa)
    grad_year = _parse_whole_number(profile.grad_year)
    backlogs = _parse_whole_number(profile.backlogs)
    skills = parse_skills(profile.skills)

    results = [
        evaluate_role(role, profile.branch, cgpa, grad_year, backlogs, skills)
        for role in ROLES
    ]

    results.sort(key=lambda r: (0 if r.eligible else 1, r.title.casefold(), r.role_id))
    return results


def counts(results: Optional[list]) -> tuple:
    """Return (eligible_count, ineligible_count) for a results list (or Nones)."""
    if results is None:
        return None, None
    eligible = sum(1 for r in results if r.eligible)
    return eligible, len(results) - eligible
