"""
CLI behaviour tests.

The CLI is a reporting surface over eligibility.py, so these tests cover
argument handling and report shape, not the eligibility rules themselves
(those live in test_eligibility.py and test_acceptance.py).
"""

import argparse

import cli
from eligibility import SAMPLE_PROFILE


def _args(**overrides):
    """An argparse.Namespace with every flag absent unless overridden."""
    fields = {"branch": None, "cgpa": None, "grad_year": None,
              "backlogs": None, "skills": None}
    fields.update(overrides)
    return argparse.Namespace(**fields)


def test_no_flags_yields_the_builtin_sample_profile():
    assert cli.build_profile_from_args(_args()) == SAMPLE_PROFILE


def test_single_flag_overlays_onto_the_sample_profile():
    """Spec Test 5 is "change only the CGPA: 8.1 -> 8.5", which must be
    expressible as a single flag rather than requiring all five."""
    profile = cli.build_profile_from_args(_args(cgpa="8.5"))

    assert profile.cgpa == "8.5"
    assert profile.branch == SAMPLE_PROFILE.branch
    assert profile.grad_year == SAMPLE_PROFILE.grad_year
    assert profile.backlogs == SAMPLE_PROFILE.backlogs
    assert profile.skills == SAMPLE_PROFILE.skills


def test_explicit_empty_string_is_honoured_not_defaulted():
    """`--branch ""` must stay empty so the INVALID_BRANCH path is reachable."""
    profile = cli.build_profile_from_args(_args(branch=""))

    assert profile.branch == ""
    assert profile.cgpa == SAMPLE_PROFILE.cgpa


def test_all_flags_supplied_are_used_verbatim():
    profile = cli.build_profile_from_args(
        _args(branch="ECE", cgpa="7.0", grad_year="2028",
              backlogs="0", skills="Git")
    )

    assert (profile.branch, profile.cgpa, profile.grad_year,
            profile.backlogs, profile.skills) == ("ECE", "7.0", "2028", "0", "Git")


def test_report_for_sample_profile_shows_spec_counts_and_order(capsys):
    cli.print_report(SAMPLE_PROFILE)
    out = capsys.readouterr().out

    assert "Eligible: 2   Ineligible: 3" in out
    # Eligible group first, then ineligible, each title-sorted.
    order = [line.split(".")[1].strip().split(" ")[0]
             for line in out.splitlines() if line.strip()[:2] in
             ("1.", "2.", "3.", "4.", "5.")]
    assert order == ["CF01", "CF02", "CF03", "CF04", "CF05"]
    assert "MISSING_SKILL: Docker" in out


def test_report_for_invalid_profile_prints_codes_and_no_results(capsys):
    cli.print_report(cli.build_profile_from_args(_args(cgpa="10.5")))
    out = capsys.readouterr().out

    assert "INVALID_CGPA" in out
    assert "profile is invalid" in out
    assert "ELIGIBLE" not in out
    assert "Eligible:" not in out
