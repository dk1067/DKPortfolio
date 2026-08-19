import sqlite3
import pandas as pd

DB_PATH = "nba.db"

print("SCRIPT STARTED")


def load_team_summary(conn):
    """One row per team: avg 3PT attempts, avg points, win %."""
    query = """
    SELECT
        team_id,
        AVG(fg3_pct) AS avg_3pt_made,
        AVG(pts) AS avg_points,
        SUM(CASE WHEN win_loss = 'W' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS win_pct
    FROM fact_team_games
    GROUP BY team_id
    """
    return pd.read_sql(query, conn)


def correlation_3pt_vs_wins(df):
    """
    Correlation coefficient ranges from -1 to 1.
    Close to 0 = no linear relationship; close to 1 = strong positive;
    close to -1 = strong negative. This does NOT prove causation -
    that's an important caveat to include in your storytelling section.
    """
    corr = df["avg_3pt_made"].corr(df["win_pct"])
    print(f"Correlation between 3PT made/game and win %: {corr:.3f}")
    return corr


def player_scoring_zscores(conn, min_games=20):
    """
    Z-score = (player's PPG - league average PPG) / league standard deviation.
    A z-score of +2 means a player scores 2 standard deviations above
    the average qualifying player - a simple way to flag outliers
    without just eyeballing a raw points column.
    """
    query = """
    SELECT p.player_id, p.full_name, AVG(f.pts) AS ppg, COUNT(*) AS games
    FROM fact_player_games f
    JOIN dim_players p ON f.player_id = p.player_id
    GROUP BY p.player_id, p.full_name
    HAVING games >= ?
    """
    df = pd.read_sql(query, conn, params=(min_games,))
    df["z_score"] = (df["ppg"] - df["ppg"].mean()) / df["ppg"].std()
    return df.sort_values("z_score", ascending=False)


def main():
    conn = sqlite3.connect(DB_PATH)

    team_df = load_team_summary(conn)
    correlation_3pt_vs_wins(team_df)

    z_df = player_scoring_zscores(conn)
    print("\nTop 10 scoring outliers (z-score):")
    print(z_df.head(10)[["player_id", "full_name", "ppg", "z_score"]].to_string(index=False))

    conn.close()


if __name__ == "__main__":
    main()
