-- queries.sql
-- Stage 2: SQL Analysis
-- Run these against nba.db (e.g. `sqlite3 nba.db` then `.read queries.sql`,
-- or open nba.db in a SQLite GUI like DB Browser for SQLite).
-- Ordered roughly from easiest to hardest so you can learn as you go.

    SELECT COUNT(*) FROM dim_players;-- sanity check: should return 123,000 rows

-- 1. Top 10 scorers by total points this season (simple aggregate)
    SELECT p.full_name, SUM(f.pts) AS total_points
    FROM fact_player_games f
    JOIN dim_players p ON f.player_id = p.player_id
    GROUP BY p.full_name
    ORDER BY total_points DESC
    LIMIT 10;

-- Test A: GROUP BY + LIMIT, no ORDER BY
   SELECT p.full_name, SUM(f.pts) AS total_points
   FROM fact_player_games f
   JOIN dim_players p ON f.player_id = p.player_id
   GROUP BY p.full_name
   LIMIT 3;

-- 2. Players averaging 25+ points per game, min. 20 games played (GROUP BY + HAVING)
SELECT p.full_name,
       ROUND(AVG(f.pts), 1) AS ppg,
       COUNT(*) AS games_played
FROM fact_player_games f
JOIN dim_players p ON f.player_id = p.player_id
GROUP BY p.full_name
HAVING games_played >= 20 AND ppg >= 25
ORDER BY ppg DESC;

-- 3. Team win totals for the season
SELECT t.full_name, COUNT(*) AS wins
FROM fact_team_games f
JOIN dim_teams t ON f.team_id = t.team_id
WHERE f.win_loss = 'W'
GROUP BY t.full_name
ORDER BY wins DESC;

SELECT * FROM dim_teams LIMIT 2;

SELECT * FROM dim_players LIMIT 5;
SELECT * FROM fact_player_games LIMIT 5;

SELECT SUM(losses) AS total_losses_league_wide
FROM (
    SELECT t.full_name, COUNT(*) AS losses
    FROM fact_team_games f
    JOIN dim_teams t ON f.team_id = t.team_id
    WHERE f.win_loss = 'L'
    GROUP BY t.full_name
);

SELECT COUNT(*) AS total_loss_rows
FROM fact_team_games
WHERE win_loss = 'L';

SELECT COUNT(*) FROM fact_team_games;

-- 4. Full game log for one player, joined to team name (multi-table JOIN)
SELECT p.full_name, t.full_name AS team, f.game_date, f.min, f.pts, f.ast, f.reb
FROM fact_player_games f
JOIN dim_players p ON f.player_id = p.player_id
JOIN dim_teams t ON f.team_id = t.team_id
WHERE p.full_name = 'LeBron James'
ORDER BY f.game_date;

--testing
-- SELECT p.full_name, count(*) AS loss_count
-- FROM fact_player_games f
-- JOIN dim_players p ON f.player_id = p.player_id
-- JOIN dim_teams t ON f.team_id = t.team_id
-- WHERE f.win_loss = 'L' AND p.full_name = 'LeBron James'
-- GROUP BY p.full_name;


-- SELECT * FROM dim_players WHERE full_name = 'LeBron James';

-- 5. Rolling 5-game scoring average (window function: AVG() OVER)
SELECT
    p.full_name,
    f.game_date,
    f.pts,
    ROUND(AVG(f.pts) OVER (
        PARTITION BY f.player_id
        ORDER BY f.game_date
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ), 1) AS rolling_5g_avg
FROM fact_player_games f
JOIN dim_players p ON f.player_id = p.player_id
WHERE p.full_name = 'Stephen Curry'
ORDER BY f.game_date;

-- 6. Each night's top scorer league-wide (window function + CTE)
WITH ranked AS (
    SELECT
        f.game_date,
        p.full_name,
        f.pts,
        RANK() OVER (PARTITION BY f.game_date ORDER BY f.pts DESC) AS scoring_rank
    FROM fact_player_games f
    JOIN dim_players p ON f.player_id = p.player_id
)
SELECT * FROM ranked
WHERE scoring_rank = 1
ORDER BY game_date;

-- 7. Season rank by total points (DENSE_RANK + CTE)
WITH totals AS (
    SELECT p.full_name, SUM(f.pts) AS total_points
    FROM fact_player_games f
    JOIN dim_players p ON f.player_id = p.player_id
    GROUP BY p.full_name
)
SELECT full_name, total_points,
       DENSE_RANK() OVER (ORDER BY total_points DESC) AS season_rank
FROM totals
ORDER BY season_rank
LIMIT 20;

-- 8. Team 3-point attempt rate vs win percentage (feeds Stage 3 stats question)
SELECT
    t.full_name,
    ROUND(AVG(f.fg3a), 1) AS avg_3pt_attempts,
    ROUND(100.0 * SUM(CASE WHEN f.win_loss = 'W' THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_pct
FROM fact_team_games f
JOIN dim_teams t ON f.team_id = t.team_id
GROUP BY t.full_name
ORDER BY win_pct DESC;

-- 9. Players with the best average plus/minus (min. 20 games)
SELECT p.full_name,
       ROUND(AVG(f.plus_minus), 1) AS avg_plus_minus,
       COUNT(*) AS games
FROM fact_player_games f
JOIN dim_players p ON f.player_id = p.player_id
GROUP BY p.full_name
HAVING games >= 20
ORDER BY avg_plus_minus DESC
LIMIT 15;

-- 10. Month-over-month scoring trend for one team (date functions)
SELECT
    t.full_name,
    strftime('%Y-%m', f.game_date) AS month,
    ROUND(AVG(f.pts), 1) AS avg_team_points
FROM fact_team_games f
JOIN dim_teams t ON f.team_id = t.team_id
WHERE t.full_name = 'Golden State Warriors'
GROUP BY month
ORDER BY month;

SELECT
        team_id,
        AVG(fg3a) AS avg_3pt_attempts,
        AVG(pts) AS avg_points,
        SUM(CASE WHEN win_loss = 'W' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS win_pct
    FROM fact_team_games
    GROUP BY team_id

    SELECT MIN(fg3_pct), MAX(fg3_pct), AVG(fg3_pct) FROM fact_team_games
