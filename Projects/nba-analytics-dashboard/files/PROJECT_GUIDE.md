# NBA Analytics Dashboard — Project Deep Dive

A beginner-friendly, end-to-end walkthrough for building a resume-worthy
analytics project: data engineering → SQL → statistics → visualization →
storytelling.

**Files in this project:**
| File | Purpose |
|---|---|
| `fetch_nba_data.py` | Stage 1 — pulls raw season data from the NBA stats API |
| `setup_database.py` | Stage 1 — loads raw CSVs into a normalized SQLite database |
| `queries.sql` | Stage 2 — 10 practice queries, easy → advanced |
| `stats_analysis.py` | Stage 3 — correlation + z-score analysis |
| `dashboard_app.py` | Stage 4 — Streamlit dashboard |
| `requirements.txt` | Python dependencies |

---

## 0. Environment Setup (do this once)

1. **Install Python 3.10+** if you don't have it: [python.org/downloads](https://www.python.org/downloads/)
2. **Install VS Code** (free): [code.visualstudio.com](https://code.visualstudio.com/) — install the "Python" extension from the marketplace once it's open.
3. **Create a project folder** and a virtual environment (keeps this project's packages separate from everything else on your machine):
   ```bash
   mkdir nba-analytics-dashboard
   cd nba-analytics-dashboard
   python3 -m venv venv

   # Activate it:
   source venv/bin/activate      # Mac/Linux
   venv\Scripts\activate         # Windows
   ```
   You'll know it worked because your terminal prompt will show `(venv)` at the start.
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Put all the files above into this folder**, then you're ready for Stage 1.
6. **Create a GitHub repo** for this project now, even before you've written much — commit early and often. This repo *is* your portfolio piece.

---

## Stage 1 — Data Engineering

### What "data engineering" actually means here
Two jobs: **get the data** (extraction) and **put it somewhere queryable and
clean** (loading). This is the unglamorous plumbing that every analytics
project depends on — and it's a real, separately-valuable skill.

### 1a. Extraction — `fetch_nba_data.py`
This uses the `nba_api` package, a community-built wrapper around the same
API stats.nba.com's own website uses. Run:
```bash
python fetch_nba_data.py
```
What it does:
- Pulls the static list of all 30 teams and all players (no season needed for these — they're reference/lookup data)
- Pulls **one row per team per game** for the season (team box scores)
- Pulls **one row per player per game** for the season (player box scores)
- Saves everything as CSVs in a `data/` folder

This will take a minute or two — it's talking to a real API, be patient.
If a request fails, just re-run the script; the NBA's API occasionally
rate-limits or times out on individual calls.

**Beginner tip:** open each resulting CSV in Excel or VS Code once it's
done and just look at it. Understanding your raw data before you touch it
with code saves hours of confusion later.

### 1b. Loading — `setup_database.py`
This is where the real "data engineering" thinking happens. Instead of
just dumping the CSVs into a single flat table, we build a **normalized
schema**:

- **Dimension tables** (`dim_teams`, `dim_players`) — descriptive info that
  doesn't change per game: a player's name, a team's city.
- **Fact tables** (`fact_team_games`, `fact_player_games`) — the actual
  measurements that change every game: points, rebounds, assists.

This "star schema" pattern (dimensions + facts) is exactly how real data
warehouses are structured, and naming it correctly in an interview signals
you understand *why* data is organized this way, not just that you can
write `CREATE TABLE`.

Run:
```bash
python setup_database.py
```
This creates `nba.db`, a single-file SQLite database — no server to
install or configure, which is exactly what you want for a solo learning
project.

**Beginner tip:** install "DB Browser for SQLite" (free, GUI) so you can
click around `nba.db` visually instead of only querying it from the
command line.

---

## Stage 2 — SQL Analysis (`queries.sql`)

Open `queries.sql` and work through the 10 queries **in order** — they're
sequenced from basic to advanced on purpose:

1. **Simple aggregate** (`SUM`, `GROUP BY`) — total points per player
2. **`GROUP BY` + `HAVING`** — filtering on an aggregated value, not a raw column
3. **Basic `JOIN`** — combining wins with team names
4. **Multi-table `JOIN`** — player + team + game stats together
5. **Window function** (`AVG() OVER... ROWS BETWEEN`) — rolling averages *without* collapsing rows the way `GROUP BY` does
6. **`RANK()` + CTE** — finding "the best X per group"
7. **`DENSE_RANK()` + CTE** — season-long leaderboard
8. **Aggregation feeding a hypothesis** — sets up Stage 3
9. **Filtering on an aggregate with a minimum threshold** — avoids small-sample noise
10. **Date functions** (`strftime`) — trend over time

**Why window functions matter for your resume:** `GROUP BY` collapses
rows down to one per group. Window functions (`OVER (...)`) let you keep
every row *and* attach a calculated value to each one — like "this game's
points, plus this player's rolling average as of this game." This is one
of the most common things interviewers screen for in a SQL round, and
most beginners never touch it. Getting comfortable with #5–7 alone will
put you ahead of a lot of other junior candidates.

Run these either with `sqlite3 nba.db` on the command line + `.read
queries.sql`, or by opening `nba.db` in DB Browser for SQLite and pasting
queries into its "Execute SQL" tab.

---

## Stage 3 — Statistics (`stats_analysis.py`)

Run:
```bash
python stats_analysis.py
```

Two concrete techniques, deliberately kept simple:

- **Correlation** — does a team's average 3-point attempts per game move
  together with its win percentage? A correlation near 0 means no
  relationship; near ±1 means a strong one. **Important:** correlation is
  not causation — a team that shoots a lot of threes might also just
  have better talent overall. Say this explicitly in your write-up; it's
  a sign of statistical maturity, not a weakness.
- **Z-scores** — instead of just sorting players by raw points-per-game,
  a z-score tells you how many standard deviations above or below the
  *average qualifying player* someone is. It's a more honest way to talk
  about "who's an outlier" than a raw leaderboard.

**Stretch goal once you're comfortable:** a simple linear regression
(`scikit-learn`'s `LinearRegression` or `numpy.polyfit`) predicting a
player's points-per-game from their minutes and shot attempts. Not
required for a strong project, but a nice "I went further" flourish if
you want it.

---

## Stage 4 — Visualization (`dashboard_app.py`)

Run:
```bash
streamlit run dashboard_app.py
```
A browser tab opens automatically at `localhost:8501`. The starter app
lets you pick a player from a dropdown and see their scoring trend plus
season averages, pulling live from `nba.db`.

**Once the skeleton works, extend it** — a few ideas, roughly in order of
effort:
- Add a second page/tab for team-vs-team comparison
- Add a date range filter
- Swap `st.line_chart` for `plotly` if you want interactive hover tooltips
- Add the correlation/z-score numbers from Stage 3 as a dedicated "Stats"
  tab

**Deploying it (do this — a live link is worth far more on a resume than
a screenshot):** push your repo to GitHub, then deploy for free at
[share.streamlit.io](https://share.streamlit.io) (Streamlit Community
Cloud). Note: you'll need to either commit `nba.db` to the repo (fine for
a project this size) or add a small setup step that runs
`fetch_nba_data.py` + `setup_database.py` on first load.

---

## Stage 5 — Storytelling

This is the part that turns "I made some charts" into "I did analysis."
Pick **one specific, falsifiable question** your dashboard can actually
answer — for example:

> *"Is 3-point volume actually correlated with winning, or is it a myth
> from watching one really good team shoot a lot of threes?"*

> *"Which players are outperforming their raw box-score reputation once
> you adjust for role/usage?"*

Structure your README (or a blog-post-style write-up) like a short
investigation, not a list of charts:

1. **The question** — stated plainly, one sentence
2. **The data** — what season, what source, any caveats (sample size,
   missing playoff data, etc.)
3. **What you found** — lead with the one chart or number that actually
   answers the question
4. **What surprised you** — genuine investigations have a moment where
   the data pushed back on your assumption; naming it is what makes this
   read as real analysis rather than a foregone conclusion
5. **The caveat** — correlation vs. causation, small sample sizes,
   anything a sharp reader would push back on. Naming it yourself first
   is more credible than hoping nobody asks.

This write-up becomes both your GitHub README and your talking points in
an interview — when someone asks "tell me about a project," you want a
30-second version of this story ready, not "I made a dashboard."

---

## Putting it on your resume

A structure like this works well:

> **NBA Analytics Dashboard** — Built an end-to-end pipeline (Python,
> SQLite, SQL) ingesting a full season of NBA game data into a normalized
> schema; wrote analytical SQL (window functions, CTEs) and statistical
> analysis (correlation, z-scores) to investigate [your specific
> question]; delivered findings via an interactive Streamlit dashboard
> deployed at [your link].

Fill in the bracket with your *actual* finding once you have one — a
specific claim ("shooting volume explains less of winning than expected")
is much stronger than a generic description of the tech stack.

---

## Suggested pace

| Stage | Realistic time for a beginner |
|---|---|
| 0. Setup | 30–60 min |
| 1. Data engineering | 1–2 sessions |
| 2. SQL analysis | 2–3 sessions (this is where real learning happens — don't rush it) |
| 3. Statistics | 1 session |
| 4. Visualization | 1–2 sessions |
| 5. Storytelling + deploy | 1 session |

There's no need to rush — a project you can actually explain in depth
beats a rushed one with more features every time in an interview.
