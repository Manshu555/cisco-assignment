# Student Guide: AI-Assisted Coding Interview

## Overview

Welcome to the **AI-assisted coding interview**!

This interview format recognizes that modern software development heavily leverages AI tools such as **ChatGPT, GitHub Copilot, Claude, Cursor, and others**.

Your goal is to demonstrate how effectively you can use these tools while showing **sound engineering judgment** and producing **original work**.

---

## What to Expect

### Timeline

- **Pre-interview:** You will receive a coding problem **24 hours before the interview**.
- **Interview:** The interview itself will last approximately **30–40 minutes**.

### Format

#### Pre-interview

- Solve the problem using AI tools.
- Prepare all required deliverables.
- Document your AI-assisted development process.

#### Interview Day

- Present your solution.
- Explain your approach and engineering decisions.
- Complete a **live modification** to your solution.

### What Is Being Evaluated?

The focus is on your **AI-assisted development workflow**, not just the final code.

You should be able to demonstrate:

- How you think through a problem.
- How you collaborate with AI.
- How you evaluate and refine AI-generated suggestions.
- How you test and validate your implementation.
- How well you understand and own the final code.

---

# How to Approach the Problem with AI

## 1. Start With Problem Understanding

Use AI to help you:

- Break down the requirements.
- Identify key components.
- Clarify ambiguities.
- Identify constraints and assumptions.
- Think through potential edge cases.

**Do not immediately ask AI to write the entire solution.**

First make sure you understand what needs to be built.

---

## 2. Design Before Coding

Work with AI to plan the solution before implementation.

Consider:

- Architecture.
- Data structures.
- APIs or interfaces.
- Technology choices.
- Error handling.
- Testing strategy.

Prioritize **simplicity and technologies you already understand well**.

---

## 3. Use Iterative Prompting

Do not rely on a single broad prompt.

Start with a high-level request and progressively add constraints and context.

For example:

```text
First, analyze this problem and identify the core requirements.
Do not write code yet.
```

Then refine:

```text
Now propose a simple architecture using technologies I am familiar with.
Prioritize maintainability and avoid unnecessary abstractions.
```

Then:

```text
Implement the core functionality based on this architecture.
Include error handling and keep the implementation easy to explain in an interview.
```

Finally:

```text
Review this implementation for bugs, edge cases, and unnecessary complexity.
Suggest specific improvements.
```

Save important prompts and iterations for discussion during the interview.

---

## 4. Verify and Understand

Never blindly accept AI-generated code.

For every significant piece of generated code:

- Read it carefully.
- Understand how it works.
- Ask AI to explain unfamiliar sections.
- Check assumptions.
- Verify APIs and library behavior.
- Look for potential bugs.
- Modify the code yourself where appropriate.

You should be able to explain **every important part of your final implementation**.

---

## 5. Test Continuously

Testing should happen throughout development rather than only at the end.

Use AI to help generate:

- Normal test cases.
- Boundary cases.
- Invalid inputs.
- Empty inputs.
- Large inputs.
- Failure scenarios.
- Regression tests.

Run the tests yourself and verify the results.

---

## 6. Document Your Process

Keep a record of your AI-assisted workflow.

Useful evidence includes:

- Initial prompts.
- Refined prompts.
- AI-generated suggestions.
- Important design discussions.
- Debugging conversations.
- Test-generation prompts.
- Examples where you rejected or modified an AI recommendation.

The goal is to demonstrate **thoughtful collaboration**, not simply the amount of AI-generated code.

---

# Required Deliverables

## 1. Working Solution

Your solution should include:

### Functional Core Features

Focus on making the main functionality work reliably.

Do not spend excessive time on features that are outside the core requirements.

### Running Instructions

Provide clear instructions explaining:

1. Prerequisites.
2. Installation steps.
3. Configuration, if required.
4. How to start the application.
5. How to run tests.

### Sample Data

Include realistic sample data that demonstrates the application's functionality.

---

## 2. AI Interaction Documentation

Document your interaction with AI tools.

### Prompt History

Save screenshots or copy-paste important prompts.

Include prompts that demonstrate:

- Problem analysis.
- Architecture planning.
- Implementation.
- Testing.
- Debugging.
- Refinement.

### Iteration Examples

Show how your prompts evolved.

A good example is:

```text
Initial prompt
    ↓
AI response
    ↓
Identify missing requirement
    ↓
Refined prompt with constraints
    ↓
Improved response
```

This demonstrates that you are actively directing the AI rather than blindly accepting its output.

### Problem-Solving Examples

Document situations where AI helped you:

- Find a bug.
- Understand an error.
- Improve an algorithm.
- Identify an edge case.
- Simplify an implementation.
- Improve test coverage.

Also explain what **you verified or changed** after receiving the AI suggestion.

---

# 3. Design Summary

Prepare a short design document covering the following.

## Architecture Decisions

Explain:

- Main components.
- How they interact.
- Data flow.
- Technology choices.
- Why the architecture is appropriate for the scope.

Prefer **simple, maintainable architecture** over unnecessary complexity.

## AI Influence

Explain how AI recommendations affected your design.

For example:

- AI suggested a particular data structure.
- AI identified a simpler API design.
- AI recommended additional edge cases.
- AI suggested an alternative architecture that you evaluated.

Be honest about what came from AI and what you decided yourself.

## Trade-offs

Explain what you prioritized and what you intentionally deferred.

Examples:

- Simplicity vs. scalability.
- Development speed vs. abstraction.
- Feature completeness vs. reliability.
- Performance vs. implementation complexity.

A strong solution does not need to solve every possible future problem.

---

# 4. Test Evidence

## Test Plan

Document how you tested the application.

Include:

- Core functionality tests.
- Integration tests, if applicable.
- Input validation.
- Error handling.
- Regression testing.

A simple table can be useful:

| Test | Input / Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| Basic operation | Valid input | Successful result | Successful result | ✅ |
| Empty input | Empty value | Validation error | Validation error | ✅ |
| Invalid input | Malformed data | Graceful failure | Graceful failure | ✅ |
| Edge case | Boundary value | Correct result | Correct result | ✅ |

## Edge Case Handling

Show that you considered failure scenarios and unusual inputs.

Examples:

- Empty input.
- Null or missing values.
- Duplicate data.
- Invalid formats.
- Boundary values.
- Very large inputs.
- Network/API failures.
- Unexpected user behavior.

---

# 5. Development Environment Ready

Your development environment should be ready for the interview.

## Live Modification Capability

Keep your project open and ready for changes.

You should be able to:

- Locate relevant files quickly.
- Make changes efficiently.
- Run the application.
- Run tests.
- Debug failures.

## Quick Startup

Verify that your application can be started quickly.

Before the interview:

- Test the setup from a clean terminal.
- Confirm dependencies are installed.
- Confirm environment variables/configuration are available.
- Make sure sample data is ready.
- Make sure tests run successfully.

## AI Tools Accessible

Have your preferred AI assistant ready to use during the interview.

Examples include:

- ChatGPT.
- GitHub Copilot.
- Claude.
- Cursor.
- Other approved AI development tools.

## Technology Familiarity

Choose technologies you can confidently:

- Explain.
- Debug.
- Modify.
- Test.

Do not select a technology simply because AI recommended it.

---

# ✅ What We're Looking For

## Thoughtful AI Collaboration

We want to see:

- Clear prompts.
- Relevant context.
- Specific constraints.
- Iterative refinement.
- Critical evaluation of AI responses.

## Code Ownership

You should understand and be able to modify the final solution.

You should be able to explain:

- Why the code works.
- Why you chose the approach.
- What alternatives you considered.
- Where potential weaknesses exist.

## Practical Design Choices

Choose an architecture that is:

- Simple.
- Maintainable.
- Appropriate for the problem.
- Easy to test.
- Easy to explain.

## Testing Mindset

Demonstrate that you:

- Test continuously.
- Think about edge cases.
- Validate AI-generated code.
- Fix problems rather than assuming the output is correct.

## Transparent Process

Be honest about your AI usage.

AI assistance is **expected**.

The important thing is demonstrating that you are the engineer directing, evaluating, testing, and improving the solution.

---

# ⚠️ Areas to Avoid

## Blind Copy-Paste

Do not accept AI-generated code without understanding it.

You should be able to explain and modify the code during the interview.

## Over-Engineering

Avoid:

- Unnecessary frameworks.
- Excessive abstraction.
- Complex architecture for simple problems.
- Features that are not required.

A **working, simple solution** is better than a complex, broken one.

## No Validation

Do not submit a solution without:

- Running it.
- Testing it.
- Checking edge cases.
- Verifying AI-generated code.

## Prompt Stagnation

Do not rely on one generic prompt.

Iterate and improve your prompts as you learn more about the problem.

## Ethics Violations

Do not:

- Copy solutions from external repositories.
- Present someone else's work as your own.
- Hide or misrepresent AI assistance.

AI should be treated as a development partner, not as a replacement for engineering judgment.

---

# Final Reminders

- **Focus on functionality over perfection.**
- **Document your development journey.**
- **Be transparent about AI assistance.**
- **Understand your final code.**
- **Test thoroughly.**
- **Keep the architecture simple.**
- **Be ready to modify your solution live.**
- **Use AI deliberately rather than blindly.**

> **A working, simple solution that you fully understand is better than a sophisticated solution you cannot explain.**

---

# Pre-Interview Checklist

Before the interview, verify that you have:

- [ ] Working solution.
- [ ] Clear README / running instructions.
- [ ] Realistic sample data.
- [ ] Prompt history saved.
- [ ] AI iteration examples documented.
- [ ] At least one debugging/problem-solving example.
- [ ] Design summary completed.
- [ ] Architecture decisions documented.
- [ ] Trade-offs documented.
- [ ] Test plan completed.
- [ ] Edge cases tested.
- [ ] Development environment ready.
- [ ] Application starts quickly.
- [ ] AI assistant accessible.
- [ ] All important code understood.
- [ ] Project is ready for live modification.

**Good luck!**

Remember: the interview evaluates not only **what you build**, but **how effectively you use AI as a development partner while maintaining engineering rigor and ownership of your work**.
