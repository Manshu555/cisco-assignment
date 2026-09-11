# CLAUDE.md

The project is in **[career_fair_shortlist/](career_fair_shortlist/)** — start
there, not at this root.

- Full agent context: **[career_fair_shortlist/AGENTS.md](career_fair_shortlist/AGENTS.md)**
- Human setup/usage: [career_fair_shortlist/README.md](career_fair_shortlist/README.md)
- The authoritative specification: [SI26_P06-Career-Fair-Eligibility-Shortlist.md](SI26_P06-Career-Fair-Eligibility-Shortlist.md)

```bash
cd career_fair_shortlist
pip install -r requirements.txt
python -m streamlit run app.py    # not bare `streamlit` — see AGENTS.md section 2
pytest -q                         # 157 tests
```

This repo root also holds `resume.tex` and the interview guide, which are
unrelated to the application code.
