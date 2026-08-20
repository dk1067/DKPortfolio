import os
import time
import pandas as pd
from nba_api.stats.endpoints import leaguegamelog
from nba_api.stats.static import teams as static_teams
from nba_api.stats.static import players as static_players

SEASON = "2024-25"     # just a hard code, change if want"
OUTPUT_DIR = "data"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_team_game_logs(season: str = SEASON) -> pd.DataFrame:
    """One row per team per game played that season (team box scores)."""
    print(f"Fetching team game logs for {season}...")
    log = leaguegamelog.LeagueGameLog(
        season=season,
        season_type_all_star="Regular Season",
        player_or_team_abbreviation="T",   # (btw) 'T' = team-level rows
    )
    return log.get_data_frames()[0]


def fetch_player_game_logs(season: str = SEASON) -> pd.DataFrame:
    """One row per player per game played that season (player box scores)."""
    print(f"Fetching player game logs for {season}...")
    log = leaguegamelog.LeagueGameLog(
        season=season,
        season_type_all_star="Regular Season",
        player_or_team_abbreviation="P",   # (btw) 'P' = player-level rows
    )
    return log.get_data_frames()[0]


def fetch_teams() -> pd.DataFrame:
    """Static reference list of all NBA franchises (no season needed)."""
    return pd.DataFrame(static_teams.get_teams())


def fetch_players() -> pd.DataFrame:
    """Static reference list of all NBA players, active + historical."""
    return pd.DataFrame(static_players.get_players())


def main() -> None:
    teams_df = fetch_teams()
    teams_df.to_csv(f"{OUTPUT_DIR}/teams.csv", index=False)
    print(f"Saved {len(teams_df)} teams -> {OUTPUT_DIR}/teams.csv")

    players_df = fetch_players()
    players_df.to_csv(f"{OUTPUT_DIR}/players.csv", index=False)
    print(f"Saved {len(players_df)} players -> {OUTPUT_DIR}/players.csv")

    # Small delay between calls so don't hammer API
    time.sleep(1)

    team_games_df = fetch_team_game_logs()
    team_games_df.to_csv(f"{OUTPUT_DIR}/team_game_logs.csv", index=False)
    print(f"Saved {len(team_games_df)} team-game rows -> {OUTPUT_DIR}/team_game_logs.csv")

    time.sleep(1)

    player_games_df = fetch_player_game_logs()
    player_games_df.to_csv(f"{OUTPUT_DIR}/player_game_logs.csv", index=False)
    print(f"Saved {len(player_games_df)} player-game rows -> {OUTPUT_DIR}/player_game_logs.csv")

    print("\nDone! Raw data saved in ./data/")


if __name__ == "__main__":
    main()
