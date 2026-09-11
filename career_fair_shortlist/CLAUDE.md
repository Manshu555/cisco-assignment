# CLAUDE.md

The full project context lives in **[AGENTS.md](AGENTS.md)** — read it before
making changes. It is tool-agnostic on purpose, so Claude Code, Cursor,
Copilot and others all work from the same source of truth.

Three things that cause the most damage if missed:

1. **All business rules live in `eligibility.py`.** Never re-implement a rule,
   a threshold, a sort key, or a failure string in `app.py` or `cli.py`.
2. **`app.py` derives its display state every rerun.** Writing
   `st.session_state["results"]` outside the Evaluate branch re-opens a
   fixed spec §8 stale-results bug.
3. **Launch with `python -m streamlit run app.py`** — a broken Anaconda
   install shadows the bare `streamlit` command on the original machine.

Run `pytest -q` (157 tests) after any change. Keep the solution small: this is
an interview deliverable that must stay explainable and live-modifiable.
