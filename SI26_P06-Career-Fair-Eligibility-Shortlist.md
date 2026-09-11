# SI26_P06: Career Fair Eligibility Shortlist

## AI-Assisted Coding Interview Problem

---

# 1. Problem Statement

Build a compact **Career Fair Eligibility Shortlist** for a university placement team.

The application should compare **one student's academic profile and skills** against a fixed local list of career-fair roles.

It must show:

- Which roles the student is eligible for.
- Every failed rule for each ineligible role.
- An editable student profile.
- The five fixed role requirements.
- An **Evaluate** action.
- A result list.
- Eligible/ineligible counts.
- A validation message.
- Sample/reset controls.

Use **one attractive primary screen or report**.

You may implement the solution using:

- Browser application.
- Desktop application.
- Mobile application.
- Spreadsheet.
- Notebook.
- CLI that produces a clear visual or tabular report.

### Not Required

The application does **not** need:

- Ranking.
- Application tracking.
- Sensitive personal attributes.
- Interview scheduling.
- Booking.
- User accounts.
- Backend services.
- Network services.
- External job feeds.

---

# 2. Built-In Student Profile

The application must load this profile as the built-in sample:

| Field | Value |
|---|---|
| Branch | CSE |
| CGPA | 8.1 |
| Graduation Year | 2027 |
| Active Backlogs | 1 |
| Skills | Git, Python, SQL |

---

# 3. Fixed Career-Fair Roles

These roles are fixed local data and should not require an external job feed.

| Role ID | Role | Allowed Branches | Minimum CGPA | Allowed Graduation Years | Maximum Active Backlogs | Required Skills |
|---|---|---|---:|---|---:|---|
| CF01 | Data Operations Intern | CSE, IT | 7.5 | 2027 | 1 | Python, SQL |
| CF02 | QA Automation Intern | CSE, ECE, IT | 7.0 | 2027, 2028 | 1 | Git |
| CF03 | Embedded Systems Intern | ECE, EEE | 7.5 | 2027 | 1 | Git |
| CF04 | Machine Learning Intern | CSE, IT | 8.5 | 2027 | 1 | Python |
| CF05 | Platform Engineering Intern | CSE, ECE | 7.0 | 2026 | 0 | Docker, Git |

---

# 4. Built-In Expected Result

With the built-in student profile:

- **CF01** → ELIGIBLE
- **CF02** → ELIGIBLE
- **CF03** → INELIGIBLE
  - `BRANCH_NOT_ALLOWED`
- **CF04** → INELIGIBLE
  - `CGPA_BELOW_MINIMUM`
- **CF05** → INELIGIBLE
  - `GRADUATION_YEAR_NOT_ALLOWED`
  - `TOO_MANY_ACTIVE_BACKLOGS`
  - `MISSING_SKILL: Docker`

Therefore:

| Status | Count |
|---|---:|
| Eligible | 2 |
| Ineligible | 3 |

The application must display the roles in the required ordering.

---

# 5. Eligibility Rules

A role is **ELIGIBLE** only when **all** of the following rules pass:

1. Student branch is in the role's allowed branch set.
2. Student CGPA is greater than or equal to the role's minimum CGPA.
3. Student graduation year is in the role's allowed graduation years.
4. Student active backlogs are less than or equal to the role's maximum allowed backlogs.
5. Every required skill is present in the student's skill list.

If any rule fails, the role is **INELIGIBLE**.

---

# 6. Input Normalization Contracts

## Branches and Skills

Trim surrounding spaces from:

- Branch values.
- Skill values.

Compare branches and skills:

- Case-insensitively.
- After trimming.

Do **not** infer:

- Branch aliases.
- Related branches.
- Similar skills.
- Skill synonyms.

For example:

```text
" Python "
"python"
"PYTHON"
```

should all compare as the same skill.

However:

```text
"Python"
"PyTorch"
```

must remain different skills.

---

## Skill List Parsing

Split an entered skill list on commas.

Example:

```text
Git, Python, SQL
```

Empty pieces should be ignored.

Example:

```text
Git,, Python, ,SQL
```

becomes:

```text
Git
Python
SQL
```

Duplicates should be collapsed.

Example:

```text
Git, Python, Git, SQL
```

becomes:

```text
Git
Python
SQL
```

---

# 7. Input Validation

## Branch

A blank branch is invalid.

Report:

```text
INVALID_BRANCH
```

---

## CGPA

CGPA must be:

- A finite number.
- Greater than or equal to `0`.
- Less than or equal to `10`.

Valid examples:

```text
0
7.5
8.1
10
```

Invalid examples:

```text
-1
10.5
NaN
Infinity
```

An invalid CGPA must report:

```text
INVALID_CGPA
```

---

## Graduation Year

Graduation year must be:

- A whole number.
- Between `2000` and `2100`, inclusive.

Invalid values must report:

```text
INVALID_GRADUATION_YEAR
```

---

## Active Backlogs

Active backlogs must be:

- A whole number.
- Greater than or equal to `0`.

Invalid values must report:

```text
INVALID_BACKLOG_COUNT
```

---

# 8. Invalid Profile Behavior

If **any student-profile field is invalid**:

1. Clear all previous role results.
2. Clear eligible count.
3. Clear ineligible count.
4. Display the appropriate validation message.
5. Do not leave stale results visible.

This is important because the UI and internal state must remain synchronized.

---

# 9. Failure Reason Rules

Every role must be evaluated independently.

For an ineligible role, list **every failed rule exactly once**.

Failure reasons must appear in this exact order:

1. `BRANCH_NOT_ALLOWED`
2. `CGPA_BELOW_MINIMUM`
3. `GRADUATION_YEAR_NOT_ALLOWED`
4. `TOO_MANY_ACTIVE_BACKLOGS`
5. `MISSING_SKILL: <skill>`

Multiple missing skills must be sorted in:

> Case-insensitive alphabetical order.

### Example

If the missing skills are:

```text
Docker
AWS
GitHub Actions
```

the output must be:

```text
MISSING_SKILL: AWS
MISSING_SKILL: Docker
MISSING_SKILL: GitHub Actions
```

An eligible role must show **no failure reasons**.

---

# 10. Result Ordering

Results must be divided into two groups.

## First: ELIGIBLE

All eligible roles appear first.

## Second: INELIGIBLE

All ineligible roles appear second.

Within each status group:

1. Sort by role title in case-insensitive ascending order.
2. If titles are equal, sort by role ID in ascending order.

For the built-in profile, the expected ordering is:

```text
ELIGIBLE
1. CF01 — Data Operations Intern
2. CF02 — QA Automation Intern

INELIGIBLE
3. CF03 — Embedded Systems Intern
4. CF04 — Machine Learning Intern
5. CF05 — Platform Engineering Intern
```

---

# 11. Required UI

The primary screen/report should contain:

## Student Profile

Editable fields for:

- Branch.
- CGPA.
- Graduation Year.
- Active Backlogs.
- Skills.

## Role Requirements

Display all five fixed roles and their requirements.

## Actions

Include:

- **Evaluate**
- **Load Sample**
- **Reset**

## Validation

Display validation status/messages clearly.

## Results

Show:

- Role ID.
- Role title.
- Eligibility status.
- Failure reasons for ineligible roles.

## Counts

Display:

- Eligible count.
- Ineligible count.

---

# 12. Acceptance Criteria

## Test 1 — Built-In Profile

Load the built-in profile in one action.

Expected:

```text
CF01 → ELIGIBLE
CF02 → ELIGIBLE
CF03 → INELIGIBLE
CF04 → INELIGIBLE
CF05 → INELIGIBLE
```

Counts:

```text
Eligible: 2
Ineligible: 3
```

---

## Test 2 — CF03 Failure

CF03 must show **only**:

```text
BRANCH_NOT_ALLOWED
```

---

## Test 3 — CF04 Failure

CF04 must show **only**:

```text
CGPA_BELOW_MINIMUM
```

---

## Test 4 — CF05 Complete Failure Reasons

CF05 must show exactly:

```text
GRADUATION_YEAR_NOT_ALLOWED
TOO_MANY_ACTIVE_BACKLOGS
MISSING_SKILL: Docker
```

and in that exact order.

---

## Test 5 — CGPA Boundary

Change only the CGPA:

```text
8.1 → 8.5
```

Expected:

```text
CF01 → ELIGIBLE
CF04 → ELIGIBLE
CF02 → ELIGIBLE
```

Eligible count:

```text
3
```

Ineligible count:

```text
2
```

Eligible roles must be ordered by title:

```text
CF01 — Data Operations Intern
CF04 — Machine Learning Intern
CF02 — QA Automation Intern
```

---

## Test 6 — Invalid CGPA

Enter:

```text
10.5
```

Expected validation message:

```text
INVALID_CGPA
```

The application must:

- Clear all role results.
- Clear eligible count.
- Clear ineligible count.
- Avoid displaying stale results.

---

## Test 7 — Built-In Data Synchronization

Verify that the following remain synchronized:

- Student profile.
- Fixed role requirements.
- Evaluation results.
- Eligibility statuses.
- Failure reasons.
- Eligible count.
- Ineligible count.
- Validation message.
- Sample/reset actions.

---

# 13. Focused Test Plan

A minimum focused test suite should cover:

| Test Area | What to Verify |
|---|---|
| Built-in result | 2 eligible, 3 ineligible |
| Branch validation | Blank branch → `INVALID_BRANCH` |
| CGPA validation | 10.5 → `INVALID_CGPA` |
| CGPA boundary | 8.5 makes CF04 eligible |
| Graduation year | Invalid and disallowed years |
| Backlog validation | Negative/non-whole values rejected |
| Skill parsing | Spaces, empty entries, duplicates |
| Case handling | Branches and skills compared case-insensitively |
| Missing skills | Every missing skill reported once |
| Failure ordering | Reasons appear in exact required order |
| Role ordering | Eligible first, then ineligible |
| Title sorting | Case-insensitive ascending order |
| Counts | Counts match result statuses |
| Reset | Built-in profile and role list restored |
| Stale state | Invalid profile clears old results |

---

# 14. Optional Feature

You may add a compact **role-card view**.

If implemented, it must be driven by the **same eligibility results** as the primary result list.

Do not create a second eligibility implementation for the role cards.

---

# 15. AI-Assisted Development Requirement

Use AI coding assistants during development.

Examples include:

- ChatGPT.
- Claude.
- GitHub Copilot.
- Cursor.
- Other approved AI coding tools.

The interview evaluates **how effectively you use AI as a development partner**, not merely whether AI generated code for you.

---

# 16. Required Development Plan

Before implementation, create a short **3–5 step implementation plan**.

Example:

```text
1. Model the student profile and fixed role requirements.
2. Implement input normalization and validation.
3. Implement independent eligibility evaluation and deterministic sorting.
4. Build the primary UI and synchronized result/count state.
5. Add focused tests for acceptance criteria and edge cases.
```

For each step, define a useful checkpoint.

Example:

```text
Step 1 checkpoint:
All five roles and the built-in student profile load correctly.

Step 2 checkpoint:
Invalid inputs produce the required validation codes.

Step 3 checkpoint:
Built-in evaluation produces the exact expected statuses and reasons.

Step 4 checkpoint:
UI results, counts, validation state, and controls remain synchronized.

Step 5 checkpoint:
All acceptance tests pass.
```

---

# 17. AI Prompting Strategy

Prepare to show the prompts you used to translate the problem statement into technical specifications.

Good prompts should contain:

- Relevant requirements.
- Constraints.
- Expected behavior.
- Technology choices.
- Testing requirements.
- Explicit instructions to avoid unnecessary complexity.

### Example Initial Prompt

```text
Analyze this Career Fair Eligibility Shortlist problem.

Do not write code yet.

Extract:
1. Functional requirements.
2. Input validation rules.
3. Eligibility rules.
4. Result ordering rules.
5. Failure reason ordering.
6. Required acceptance tests.
7. Important edge cases.

Keep the proposed solution simple enough to explain and modify during a 30–40 minute interview.
```

### Example Architecture Prompt

```text
Based on the requirements, propose a simple architecture.

Use a small, maintainable design with clear separation between:
- Input validation
- Normalization
- Eligibility evaluation
- Sorting
- UI state

Avoid unnecessary frameworks, backend services, databases, authentication, or external APIs.

Explain the trade-offs.
```

### Example Implementation Prompt

```text
Implement the eligibility evaluation logic from the specification.

Requirements:
- Evaluate every rule independently.
- Return every failure reason.
- Preserve the required failure-reason order.
- Sort missing skills case-insensitively.
- Compare branches and skills case-insensitively after trimming.
- Do not infer aliases or related skills.
- Keep the implementation deterministic and easy to test.
```

### Example Testing Prompt

```text
Generate focused tests for this implementation.

Cover:
- Built-in profile.
- CGPA 8.5 boundary.
- Invalid CGPA 10.5.
- Complete CF05 failure reasons.
- Failure-reason ordering.
- Role ordering.
- Skill trimming and duplicate removal.
- Empty skill entries.
- Case-insensitive comparison.
- Invalid numeric fields.
- Clearing stale results after invalid input.

Do not modify the implementation yet.
```

---

# 18. AI Iteration Documentation

Document meaningful iterations.

A useful structure is:

| Iteration | Prompt Goal | AI Recommendation | What I Changed | Why |
|---|---|---|---|---|
| 1 | Understand requirements | Extracted rules | Verified against specification | Avoid missed requirements |
| 2 | Architecture | Suggested component structure | Simplified it | Keep scope manageable |
| 3 | Eligibility logic | Proposed evaluator | Added independent rule checks | Required by contract |
| 4 | Testing | Generated edge cases | Selected focused tests | Prioritize acceptance criteria |
| 5 | Debugging | Found ordering issue | Corrected sorting | Match specification |

The goal is to demonstrate **active engineering judgment**.

---

# 19. AI-Influenced Decision Making

Be prepared to discuss:

## Trade-offs

Examples:

- Simple architecture vs. scalability.
- Fast implementation vs. extensive abstraction.
- Client-side state vs. backend persistence.
- Generic components vs. focused components.
- Full test suite vs. focused acceptance tests.

For this problem, unnecessary infrastructure should generally be avoided.

## Assumptions

Document assumptions such as:

- Roles are fixed local data.
- Only one student profile is evaluated.
- No persistence is required.
- No authentication is required.
- No external API is required.
- Eligibility is deterministic.
- Role data does not change during evaluation.

## AI Recommendations

Explain which AI suggestions you:

- Accepted.
- Modified.
- Rejected.

Most importantly, explain **why**.

---

# 20. Testing and Validation Evidence

Prepare evidence that demonstrates the solution works.

Possible evidence:

- Automated test output.
- Screenshots.
- Terminal output.
- Browser screenshots.
- Notebook output.
- Spreadsheet results.
- Manual test checklist.

At minimum, demonstrate:

1. Built-in result.
2. CGPA 8.5 boundary.
3. Invalid CGPA.
4. Complete CF05 failure reasons.
5. Correct result ordering.
6. Correct counts.
7. Reset behavior.

---

# 21. Live Modification Capability

Be prepared to make **one small live modification**, and possibly a second if time permits.

Keep your development environment ready.

Before the interview:

- Open the project.
- Ensure dependencies are installed.
- Confirm the application starts quickly.
- Keep the AI assistant available.
- Know where the eligibility logic lives.
- Know where the UI renders results.
- Confirm tests can be run quickly.

### Good Live-Modification Strategy

When given a modification:

1. Clarify the requirement.
2. Identify the smallest affected component.
3. Ask AI for a focused change.
4. Review the generated change.
5. Implement it.
6. Run the relevant tests.
7. Demonstrate the result.

Avoid making broad architectural changes during the live portion.

---

# 22. What You Should Be Able to Explain

During the interview, be prepared to explain:

### Problem

- What the application does.
- What makes a role eligible.
- How invalid inputs are handled.

### Architecture

- Main components.
- Data structures.
- Data flow.
- Why you chose the technology stack.

### Eligibility Logic

- Why every rule is evaluated independently.
- How failure reasons are ordered.
- How missing skills are determined.
- How case-insensitive comparison works.

### Sorting

- Why eligible roles appear first.
- How title sorting works.
- How role IDs break ties.

### Validation

- How invalid numeric values are detected.
- Why `10.5` is invalid.
- How stale results are cleared.

### Testing

- Which tests you wrote.
- Which edge cases you considered.
- How you verified the acceptance criteria.

### AI Usage

- What prompts you used.
- How you refined them.
- What AI recommendations you accepted.
- What you changed yourself.
- How you verified AI-generated code.

---

# 23. Areas to Avoid

## Blind Copy-Paste

Do not use AI-generated code without understanding it.

## Over-Engineering

Avoid adding:

- Backend servers.
- Databases.
- Authentication.
- External APIs.
- Job feeds.
- Complex state-management systems.
- Unnecessary design patterns.

unless they are genuinely needed.

## Ranking

Do not introduce ranking or scoring.

The task is about **eligibility**, not candidate ranking.

## External Job Data

Do not depend on an external job feed.

The five roles are fixed local data.

## Stale State

Never leave old results visible after invalid student input.

## Incomplete Failure Reasons

Do not stop after finding the first failed rule.

Every rule must be evaluated independently.

---

# 24. Final Interview Checklist

## Solution

- [ ] Built-in student profile loads correctly.
- [ ] Five fixed roles are present.
- [ ] Student profile is editable.
- [ ] Evaluate action works.
- [ ] Reset action works.
- [ ] Sample data works.
- [ ] Results display eligibility status.
- [ ] Eligible/ineligible counts are displayed.
- [ ] Validation messages are displayed.

## Eligibility

- [ ] CF01 is eligible with built-in data.
- [ ] CF02 is eligible with built-in data.
- [ ] CF03 has only `BRANCH_NOT_ALLOWED`.
- [ ] CF04 has only `CGPA_BELOW_MINIMUM`.
- [ ] CF05 has all three required failure reasons.
- [ ] Failure reasons use the required order.
- [ ] Missing skills use case-insensitive alphabetical ordering.

## Validation

- [ ] Branch is trimmed and case-insensitive.
- [ ] Skills are trimmed and case-insensitive.
- [ ] Empty skill entries are ignored.
- [ ] Duplicate skills are collapsed.
- [ ] CGPA accepts only finite values from 0–10.
- [ ] Graduation year is a whole number from 2000–2100.
- [ ] Active backlogs are whole numbers ≥ 0.
- [ ] Invalid fields clear stale results and counts.

## Ordering

- [ ] Eligible roles appear first.
- [ ] Ineligible roles appear second.
- [ ] Titles sort case-insensitively.
- [ ] Role ID breaks title ties.

## Testing

- [ ] Built-in result tested.
- [ ] CGPA 8.5 boundary tested.
- [ ] CGPA 10.5 invalid case tested.
- [ ] Complete CF05 failure tested.
- [ ] Ordering tested.
- [ ] Counts tested.
- [ ] Reset tested.
- [ ] Edge cases tested.

## AI Workflow

- [ ] 3–5 step implementation plan prepared.
- [ ] Important prompts saved.
- [ ] Prompt iterations documented.
- [ ] Debugging example documented.
- [ ] AI-influenced decisions documented.
- [ ] Trade-offs documented.
- [ ] All generated code understood.

## Interview Readiness

- [ ] Application starts quickly.
- [ ] Development environment is open.
- [ ] AI assistant is accessible.
- [ ] Relevant files can be located quickly.
- [ ] Tests can be run quickly.
- [ ] Ready for live modification.

---

# 25. Final Goal

The strongest submission is **not necessarily the most sophisticated one**.

The goal is to demonstrate that you can:

> **Understand the requirements → plan the solution → use AI effectively → verify its output → build a maintainable implementation → test it thoroughly → explain your decisions → modify it confidently.**

A small, reliable solution that you fully understand is better than a complex solution that you cannot explain or modify.
