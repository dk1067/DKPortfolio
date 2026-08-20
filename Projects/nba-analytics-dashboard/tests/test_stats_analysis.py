import sqlite3

import pandas as pd
import pytest

from stats_analysis import correlation_3pt_vs_wins, player_scoring_zscores


@pytest.fixture
def conn():
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE dim_players (player_id INTEGER PRIMARY KEY, full_name TEXT);
        CREATE TABLE fact_player_games (game_id TEXT, player_id INTEGER, pts INTEGER);
        """
    )
    yield conn
    conn.close()


def _insert_player_games(conn, player_id, games, pts):
    conn.executemany(
        "INSERT INTO fact_player_games (game_id, player_id, pts) VALUES (?, ?, ?)",
        [(f"g{player_id}-{i}", player_id, pts) for i in range(games)],
    )


def test_player_scoring_zscores_ranks_top_scorer_highest(conn):
    conn.executemany(
        "INSERT INTO dim_players VALUES (?, ?)",
        [(1, "High Scorer"), (2, "Average Scorer"), (3, "Low Scorer")],
    )
    _insert_player_games(conn, 1, games=20, pts=30)
    _insert_player_games(conn, 2, games=20, pts=15)
    _insert_player_games(conn, 3, games=20, pts=5)
    conn.commit()

    result = player_scoring_zscores(conn, min_games=20)

    assert result.iloc[0]["full_name"] == "High Scorer"
    assert result.iloc[0]["z_score"] > result.iloc[-1]["z_score"]


def test_player_scoring_zscores_excludes_players_under_min_games(conn):
    conn.execute("INSERT INTO dim_players VALUES (1, 'Benchwarmer')")
    _insert_player_games(conn, 1, games=5, pts=10)
    conn.commit()

    result = player_scoring_zscores(conn, min_games=20)

    assert result.empty


def test_correlation_perfect_positive_relationship():
    df = pd.DataFrame({"avg_3pt_made": [1, 2, 3, 4], "win_pct": [0.1, 0.2, 0.3, 0.4]})

    assert correlation_3pt_vs_wins(df) == pytest.approx(1.0)


def test_correlation_perfect_negative_relationship():
    df = pd.DataFrame({"avg_3pt_made": [1, 2, 3, 4], "win_pct": [0.4, 0.3, 0.2, 0.1]})

    assert correlation_3pt_vs_wins(df) == pytest.approx(-1.0)
