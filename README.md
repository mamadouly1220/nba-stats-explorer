# NBA Stats Explorer

A learning project to practice the Git + GitHub + Claude Code workflow.
Pulls NBA player stats and makes a visualization.

Built by Mamadou Ly, Oct 2026.

## Install

Requires Python 3.9+.

```
pip install -r requirements.txt
```

## Run

From the repo root:

```
python scripts/explore_stats.py
```

The script pulls 2023-24 regular season per-game stats from stats.nba.com using
[nba_api](https://github.com/swar/nba_api), so it needs an internet connection.

## Output

- `data/top_players_2023_24.csv`: the top 50 players by total minutes played, with
  player name, team, points, assists, rebounds (all per game) and true shooting %
- `figures/scoring_vs_efficiency.png`: scatter plot of points per game vs true
  shooting %, with the top 10 scorers labeled

True shooting % is calculated as `PTS / (2 * (FGA + 0.44 * FTA))`.
