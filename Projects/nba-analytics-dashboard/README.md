# NBA Analytics Dashboard

An interactive Streamlit dashboard for exploring NBA player trends, built on a data pipeline that ingests a full season of box scores into a normalized SQLite database.

[![Tests](https://github.com/dk1067/DKPortfolio/actions/workflows/nba-dashboard-tests.yml/badge.svg)](https://github.com/dk1067/DKPortfolio/actions/workflows/nba-dashboard-tests.yml)

**Live demo:** [dkportfolio2012.streamlit.app](https://dkportfolio2012.streamlit.app/)
**Screenshot:** _add a screenshot or short GIF of the dashboard here_

---

## The question

Does a team's 3-point shot *volume* predict winning — or does *accuracy* matter more?

**Finding:** across the 2024–25 regular season, how often a team shoots threes barely correlates with win percentage (r ≈ 0.12), but how accurately they shoot them does (r ≈ 0.86). Taking more threes doesn't reliably win games — making them does.

**Caveat:** this is a correlation from one season across 30 teams, not a causal claim — teams that shoot well are also generally more talented, better coached, and better on defense, so accuracy is likely a proxy for overall team quality rather than an isolated lever. Small sample size (30 teams) also means single-team outliers can move the number more than they would in a larger dataset.

## Tech stack

- **Python / pandas** — data pipeline and transformation
- **SQLite** — normalized star schema (dimension + fact tables)
- **Streamlit** — interactive dashboard UI
- **nba_api** — data source (wraps stats.nba.com)
- **pytest + GitHub Actions** — automated tests, run on every push

## Running it locally

```bash
cd Projects/nba-analytics-dashboard
python3 -m venv venv && source venv/bin/activate
pip install -r files/requirements.txt

python files/fetch_nba_data.py    # pulls a season of box scores -> data/
python files/setup_database.py    # builds files/nba.db
streamlit run files/dashboard_app.py
```

## Running the test suite:

```bash
pip install -r requirements-dev.txt
pytest
```

Want the full build-it-yourself walkthrough (stage by stage, with explanations of *why*)? See [`files/PROJECT_GUIDE.md`](files/PROJECT_GUIDE.md).

## Data & architecture

```
fetch_nba_data.py  →  data/*.csv  →  setup_database.py  →  nba.db  →  dashboard_app.py / stats_analysis.py
   (NBA Stats API)      (raw)         (normalize + load)   (SQLite)      (query + serve)
```

`nba.db` is a small star schema:

- `dim_teams`, `dim_players` — descriptive lookup tables (name, city, active status)
- `fact_team_games`, `fact_player_games` — one row per team/player per game, with box score stats (points, rebounds, shooting splits, etc.)

Both fact tables carry a composite `PRIMARY KEY` (`game_id` + `team_id`/`player_id`) and `FOREIGN KEY`s back to their dimension tables, enforced at the SQLite level — not just implied by column naming.

## Limitations

- Single season only (2024–25) — no year-over-year trends yet.
- Correlation ≠ causation, and a 30-team sample is small (see caveat above).
- Dashboard currently covers per-player scoring trends; team comparisons and a dedicated stats view are natural next additions.
