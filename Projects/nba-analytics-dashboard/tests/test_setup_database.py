import sqlite3
from pathlib import Path

import pytest

from setup_database import create_schema, load_teams

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def conn(monkeypatch):
    monkeypatch.chdir(PROJECT_ROOT)
    conn = sqlite3.connect(":memory:")
    create_schema(conn)
    yield conn
    conn.close()


def test_dim_teams_primary_key_is_enforced(conn):
    conn.execute("INSERT INTO dim_teams (team_id, full_name) VALUES (1, 'Team A')")
    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO dim_teams (team_id, full_name) VALUES (1, 'Duplicate Team')"
        )


def test_load_teams_preserves_primary_key_constraint(conn):
    # to_sql(if_exists="replace") silently drops the PRIMARY KEY on rebuild.
    load_teams(conn)

    columns = conn.execute("PRAGMA table_info(dim_teams)").fetchall()
    pk_columns = [col for col in columns if col[5] > 0]  # column[5] is the pk flag

    assert pk_columns, "dim_teams lost its PRIMARY KEY constraint after loading"


def test_load_teams_does_not_duplicate_rows_on_rerun(conn):
    load_teams(conn)
    first_count = conn.execute("SELECT COUNT(*) FROM dim_teams").fetchone()[0]

    load_teams(conn)
    second_count = conn.execute("SELECT COUNT(*) FROM dim_teams").fetchone()[0]

    assert first_count == 30
    assert second_count == first_count
