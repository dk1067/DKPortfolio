import sqlite3
from pathlib import Path

import pandas as pd

FILES_DIR = Path(__file__).resolve().parent
DB_PATH = FILES_DIR / "nba.db"
DATA_DIR = FILES_DIR.parent / "data"

SCHEMA = """
CREATE TABLE IF NOT EXISTS dim_teams (
    team_id INTEGER PRIMARY KEY,
    full_name TEXT,
    abbreviation TEXT,
    city TEXT,
    year_founded INTEGER
);

CREATE TABLE IF NOT EXISTS dim_players (
    player_id INTEGER PRIMARY KEY,
    full_name TEXT,
    is_active INTEGER
);

CREATE TABLE IF NOT EXISTS fact_team_games (
    game_id TEXT,
    team_id INTEGER,
    season TEXT,
    game_date TEXT,
    matchup TEXT,
    win_loss TEXT,
    pts INTEGER,
    fgm INTEGER, fga INTEGER, fg_pct REAL,
    fg3m INTEGER, fg3a INTEGER, fg3_pct REAL,
    ftm INTEGER, fta INTEGER, ft_pct REAL,
    oreb INTEGER, dreb INTEGER, reb INTEGER,
    ast INTEGER, stl INTEGER, blk INTEGER, tov INTEGER, pf INTEGER,
    plus_minus REAL,
    PRIMARY KEY (game_id, team_id),
    FOREIGN KEY (team_id) REFERENCES dim_teams(team_id)
);

CREATE TABLE IF NOT EXISTS fact_player_games (
    game_id TEXT,
    player_id INTEGER,
    team_id INTEGER,
    season TEXT,
    game_date TEXT,
    matchup TEXT,
    win_loss TEXT,
    min REAL,
    pts INTEGER,
    fgm INTEGER, fga INTEGER, fg_pct REAL,
    fg3m INTEGER, fg3a INTEGER, fg3_pct REAL,
    ftm INTEGER, fta INTEGER, ft_pct REAL,
    oreb INTEGER, dreb INTEGER, reb INTEGER,
    ast INTEGER, stl INTEGER, blk INTEGER, tov INTEGER, pf INTEGER,
    plus_minus REAL,
    PRIMARY KEY (game_id, player_id),
    FOREIGN KEY (player_id) REFERENCES dim_players(player_id),
    FOREIGN KEY (team_id) REFERENCES dim_teams(team_id)
);
"""


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def load_teams(conn: sqlite3.Connection) -> None:
    df = pd.read_csv(f"{DATA_DIR}/teams.csv")
    df = df.rename(columns={"id": "team_id"})
    df = df[["team_id", "full_name", "abbreviation", "city", "year_founded"]]
    conn.execute("DELETE FROM dim_teams")
    df.to_sql("dim_teams", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into dim_teams")


def load_players(conn: sqlite3.Connection) -> None:
    df = pd.read_csv(f"{DATA_DIR}/players.csv")
    df = df.rename(columns={"id": "player_id"})
    df = df[["player_id", "full_name", "is_active"]]
    conn.execute("DELETE FROM dim_players")
    df.to_sql("dim_players", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into dim_players")


def _rename_stat_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={
        "GAME_ID": "game_id", "TEAM_ID": "team_id", "PLAYER_ID": "player_id",
        "SEASON_ID": "season", "GAME_DATE": "game_date", "MATCHUP": "matchup",
        "WL": "win_loss", "MIN": "min", "PTS": "pts",
        "FGM": "fgm", "FGA": "fga", "FG_PCT": "fg_pct",
        "FG3M": "fg3m", "FG3A": "fg3a", "FG3_PCT": "fg3_pct",
        "FTM": "ftm", "FTA": "fta", "FT_PCT": "ft_pct",
        "OREB": "oreb", "DREB": "dreb", "REB": "reb",
        "AST": "ast", "STL": "stl", "BLK": "blk", "TOV": "tov", "PF": "pf",
        "PLUS_MINUS": "plus_minus",
    })


def load_team_games(conn: sqlite3.Connection) -> None:
    df = _rename_stat_columns(pd.read_csv(f"{DATA_DIR}/team_game_logs.csv"))
    cols = ["game_id", "team_id", "season", "game_date", "matchup", "win_loss",
            "pts", "fgm", "fga", "fg_pct", "fg3m", "fg3a", "fg3_pct",
            "ftm", "fta", "ft_pct", "oreb", "dreb", "reb", "ast", "stl", "blk",
            "tov", "pf", "plus_minus"]
    df = df[cols]
    conn.execute("DELETE FROM fact_team_games")
    df.to_sql("fact_team_games", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into fact_team_games")


def load_player_games(conn: sqlite3.Connection) -> None:
    df = _rename_stat_columns(pd.read_csv(f"{DATA_DIR}/player_game_logs.csv"))
    cols = ["game_id", "player_id", "team_id", "season", "game_date", "matchup",
            "win_loss", "min", "pts", "fgm", "fga", "fg_pct", "fg3m", "fg3a",
            "fg3_pct", "ftm", "fta", "ft_pct", "oreb", "dreb", "reb", "ast",
            "stl", "blk", "tov", "pf", "plus_minus"]
    df = df[cols]
    conn.execute("DELETE FROM fact_player_games")
    df.to_sql("fact_player_games", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into fact_player_games")


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)
    load_teams(conn)
    load_players(conn)
    load_team_games(conn)
    load_player_games(conn)
    conn.commit()
    conn.close()
    print(f"\nDatabase ready at {DB_PATH}")


if __name__ == "__main__":
    main()
