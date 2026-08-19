import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "nba.db"


@st.cache_data
def load_players(_conn):
    query = """
    SELECT DISTINCT p.full_name
    FROM dim_players p
    JOIN fact_player_games f ON p.player_id = f.player_id
    ORDER BY p.full_name
    """
    return pd.read_sql(query, _conn)


@st.cache_data
def load_player_games(_conn, player_name):
    query = """
    SELECT f.game_date, f.pts, f.ast, f.reb, f.min, t.full_name AS team_name
    FROM fact_player_games f
    JOIN dim_players p ON f.player_id = p.player_id
    JOIN dim_teams t ON f.team_id = t.team_id
    WHERE p.full_name = ?
    ORDER BY f.game_date
    """
    return pd.read_sql(query, _conn, params=(player_name,))


def main():
    st.set_page_config(page_title="NBA Analytics Dashboard", layout="wide")
    st.title("NBA Player Trends Dashboard")

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    players_df = load_players(conn)

    player_name = st.selectbox("Choose a player", players_df["full_name"])
    games_df = load_player_games(conn, player_name)

    current_team = games_df["team_name"].iloc[-1]
    st.subheader(f"{current_team}")

    if games_df.empty:
        st.warning("No games found for this player.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("PPG", round(games_df["pts"].mean(), 1))
    col2.metric("APG", round(games_df["ast"].mean(), 1))
    col3.metric("RPG", round(games_df["reb"].mean(), 1))

    st.subheader(f"{player_name} - Points per Game Over Time")
    st.line_chart(games_df.set_index("game_date")["pts"])

    st.subheader("Raw Game Log")
    st.dataframe(games_df)

if __name__ == "__main__":
    main()
