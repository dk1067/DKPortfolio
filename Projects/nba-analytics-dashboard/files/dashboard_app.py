import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from stats_analysis import correlation_3pt_vs_wins, load_team_summary, player_scoring_zscores

DB_PATH = Path(__file__).resolve().parent / "nba.db"


@st.cache_data
def load_players(_conn: sqlite3.Connection) -> pd.DataFrame:
    query = """
    SELECT DISTINCT p.full_name
    FROM dim_players p
    JOIN fact_player_games f ON p.player_id = f.player_id
    ORDER BY p.full_name
    """
    return pd.read_sql(query, _conn)


@st.cache_data
def load_player_games(_conn: sqlite3.Connection, player_name: str) -> pd.DataFrame:
    query = """
    SELECT f.game_date, f.pts, f.ast, f.reb, f.min, t.full_name AS team_name
    FROM fact_player_games f
    JOIN dim_players p ON f.player_id = p.player_id
    JOIN dim_teams t ON f.team_id = t.team_id
    WHERE p.full_name = ?
    ORDER BY f.game_date
    """
    return pd.read_sql(query, _conn, params=(player_name,))


@st.cache_data
def load_team_stats(_conn: sqlite3.Connection) -> pd.DataFrame:
    return load_team_summary(_conn)


@st.cache_data
def load_scoring_outliers(_conn: sqlite3.Connection, min_games: int = 20) -> pd.DataFrame:
    return player_scoring_zscores(_conn, min_games)


def render_player_trends_tab(conn: sqlite3.Connection) -> None:
    players_df = load_players(conn)

    player_name = st.selectbox("Choose a player", players_df["full_name"])
    games_df = load_player_games(conn, player_name)

    if games_df.empty:
        st.warning("No games found for this player.")
        return

    current_team = games_df["team_name"].iloc[-1]
    st.subheader(f"{current_team}")

    col1, col2, col3 = st.columns(3)
    col1.metric("PPG", round(games_df["pts"].mean(), 1))
    col2.metric("APG", round(games_df["ast"].mean(), 1))
    col3.metric("RPG", round(games_df["reb"].mean(), 1))

    st.subheader(f"{player_name} - Points per Game Over Time")
    st.line_chart(games_df.set_index("game_date")["pts"])

    st.subheader("Raw Game Log")
    st.dataframe(games_df)


def render_league_stats_tab(conn: sqlite3.Connection) -> None:
    st.subheader("Does 3-Point Shooting Predict Winning?")

    team_df = load_team_stats(conn)
    accuracy_corr = correlation_3pt_vs_wins(team_df)
    volume_corr = team_df["avg_3pt_attempts"].corr(team_df["win_pct"])

    col1, col2 = st.columns(2)
    col1.metric("3PT Volume vs Win %", f"{volume_corr:.2f}")
    col2.metric("3PT Accuracy vs Win %", f"{accuracy_corr:.2f}")
    st.caption(
        "Correlation coefficient, -1 to 1. Volume = avg 3PT attempts/game. "
        "Accuracy = avg 3PT shooting %. Correlation isn't causation."
    )

    st.scatter_chart(team_df, x="avg_3pt_made", y="win_pct")

    st.subheader("Top Scoring Outliers (Z-Score)")
    st.caption("Players averaging 20+ games, ranked by how far above league-average PPG they sit.")

    outliers_df = load_scoring_outliers(conn).head(10)
    st.dataframe(
        outliers_df[["full_name", "ppg", "games", "z_score"]]
        .round(2)
        .rename(columns={
            "full_name": "Player",
            "ppg": "PPG",
            "games": "Games",
            "z_score": "Z-Score",
        }),
        hide_index=True,
    )


def main() -> None:
    st.set_page_config(page_title="NBA Analytics Dashboard", layout="wide")
    st.title("NBA Analytics Dashboard")

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    player_tab, stats_tab = st.tabs(["Player Trends", "League Stats"])

    with player_tab:
        render_player_trends_tab(conn)

    with stats_tab:
        render_league_stats_tab(conn)


if __name__ == "__main__":
    main()
