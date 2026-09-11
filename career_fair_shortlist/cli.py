"""
Career Fair Eligibility Shortlist - CLI report.

Prints a tabular eligibility report for the built-in sample profile using
the exact same eligibility.py logic as the Streamlit app. Useful as quick,
screenshot-able test evidence and for demoing without a browser.

Any flag you omit keeps its built-in sample value, so one flag expresses a
single-field change.

Usage:
    python cli.py                  # the built-in sample profile
    python cli.py --cgpa 8.5       # sample profile, CGPA changed (spec Test 5)
    python cli.py --cgpa 10.5      # sample profile, invalid CGPA (spec Test 6)
    python cli.py --branch CSE --cgpa 8.5 --grad-year 2027 --backlogs 1 --skills "Git, Python, SQL"
"""

import argparse
import sys
from typing import Optional

from eligibility import SAMPLE_PROFILE, StudentProfile, evaluate_all, counts, validate_profile

# Windows terminals often default to a legacy codepage that can't render
# the em dash used in role listings; force UTF-8 so output is consistent
# across platforms.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def build_profile_from_args(args: argparse.Namespace) -> StudentProfile:
    """
    Overlay any supplied flags onto the built-in sample profile.

    Each field falls back to its sample value when the flag is absent, so a
    partial override reads as "the sample profile, but with this one change" -
    which is how the spec phrases its scenarios (Test 5 is literally "change
    only the CGPA: 8.1 -> 8.5", i.e. `--cgpa 8.5`).

    An explicitly supplied empty string is honoured rather than replaced, so
    `--branch ""` still exercises the INVALID_BRANCH path.
    """
    def pick(supplied: Optional[str], sample: str) -> str:
        return sample if supplied is None else supplied

    return StudentProfile(
        branch=pick(args.branch, SAMPLE_PROFILE.branch),
        cgpa=pick(args.cgpa, SAMPLE_PROFILE.cgpa),
        grad_year=pick(args.grad_year, SAMPLE_PROFILE.grad_year),
        backlogs=pick(args.backlogs, SAMPLE_PROFILE.backlogs),
        skills=pick(args.skills, SAMPLE_PROFILE.skills),
    )


def print_report(profile: StudentProfile) -> None:
    print("Student Profile")
    print(f"  Branch:           {profile.branch}")
    print(f"  CGPA:             {profile.cgpa}")
    print(f"  Graduation Year:  {profile.grad_year}")
    print(f"  Active Backlogs:  {profile.backlogs}")
    print(f"  Skills:           {profile.skills}")
    print()

    errors = validate_profile(profile)
    if errors:
        print("VALIDATION FAILED:")
        for code in errors:
            print(f"  - {code}")
        print("\n(No role results — profile is invalid.)")
        return

    results = evaluate_all(profile)
    eligible_count, ineligible_count = counts(results)

    print(f"Eligible: {eligible_count}   Ineligible: {ineligible_count}")
    print()

    eligible = [r for r in results if r.eligible]
    ineligible = [r for r in results if not r.eligible]

    if eligible:
        print("ELIGIBLE")
        for i, r in enumerate(eligible, start=1):
            print(f"  {i}. {r.role_id} — {r.title}")
        print()

    if ineligible:
        print("INELIGIBLE")
        offset = len(eligible)
        for i, r in enumerate(ineligible, start=1):
            print(f"  {offset + i}. {r.role_id} — {r.title}")
            for reason in r.reasons:
                print(f"       - {reason}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Career Fair Eligibility Shortlist CLI report")
    parser.epilog = "Omitted flags keep their built-in sample value."
    parser.add_argument("--branch", help=f"default: {SAMPLE_PROFILE.branch}")
    parser.add_argument("--cgpa", help=f"default: {SAMPLE_PROFILE.cgpa}")
    parser.add_argument("--grad-year", dest="grad_year",
                        help=f"default: {SAMPLE_PROFILE.grad_year}")
    parser.add_argument("--backlogs", help=f"default: {SAMPLE_PROFILE.backlogs}")
    parser.add_argument("--skills", help=f"default: {SAMPLE_PROFILE.skills}")
    args = parser.parse_args()

    profile = build_profile_from_args(args)
    print_report(profile)


if __name__ == "__main__":
    main()
