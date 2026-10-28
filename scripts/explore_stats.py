"""
NBA Stats Explorer

Pulls 2023-24 regular season per-game stats from stats.nba.com (via nba_api),
keeps the top 50 players by total minutes played, saves a CSV, and plots
points per game against true shooting percentage.

Run from the repo root:
    python scripts/explore_stats.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # render to file without needing a display
import matplotlib.pyplot as plt
from nba_api.stats.endpoints import leaguedashplayerstats

SEASON = "2023-24"
TOP_N_PLAYERS = 50
TOP_N_LABELS = 10

# Resolve output paths relative to the repo root so the script works from any directory
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
FIGURES_DIR = REPO_ROOT / "figures"
CSV_PATH = DATA_DIR / "top_players_2023_24.csv"
PLOT_PATH = FIGURES_DIR / "scoring_vs_efficiency.png"


def fetch_per_game_stats():
    """Fetch per-game stats for every player in the 2023-24 regular season."""
    response = leaguedashplayerstats.LeagueDashPlayerStats(
        season=SEASON,
        season_type_all_star="Regular Season",
        per_mode_detailed="PerGame",
        timeout=60,
    )
    return response.get_data_frames()[0]


def build_top_players_table(stats):
    """Pick the top players by total minutes and compute true shooting %."""
    stats = stats.copy()

    # MIN is minutes per game here, so multiply by games played to rank by
    # total minutes. This keeps players with only a few games from sneaking in.
    stats["TOTAL_MIN"] = stats["MIN"] * stats["GP"]
    top = stats.nlargest(TOP_N_PLAYERS, "TOTAL_MIN")

    # True shooting % = PTS / (2 * (FGA + 0.44 * FTA))
    # It credits 3-pointers and free throws, unlike plain FG%.
    top["TS_PCT"] = top["PTS"] / (2 * (top["FGA"] + 0.44 * top["FTA"]))

    table = top[["PLAYER_NAME", "TEAM_ABBREVIATION", "PTS", "AST", "REB", "TS_PCT"]]
    table = table.rename(
        columns={
            "PLAYER_NAME": "player",
            "TEAM_ABBREVIATION": "team",
            "PTS": "points",
            "AST": "assists",
            "REB": "rebounds",
            "TS_PCT": "true_shooting_pct",
        }
    )
    table["true_shooting_pct"] = table["true_shooting_pct"].round(3)
    return table.reset_index(drop=True)


def plot_scoring_vs_efficiency(table):
    """Scatter plot of PPG vs TS%, labeling the top scorers."""
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(table["points"], table["true_shooting_pct"], s=40, alpha=0.75)

    # Label only the top scorers so the chart stays readable
    for _, row in table.nlargest(TOP_N_LABELS, "points").iterrows():
        ax.annotate(
            row["player"],
            (row["points"], row["true_shooting_pct"]),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=8,
        )

    ax.set_xlabel("Points per game")
    ax.set_ylabel("True shooting %")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.set_title(f"Scoring vs Efficiency — Top {TOP_N_PLAYERS} by Minutes, {SEASON}")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOT_PATH, dpi=150)
    plt.close(fig)


def main():
    DATA_DIR.mkdir(exist_ok=True)
    FIGURES_DIR.mkdir(exist_ok=True)

    print(f"Fetching {SEASON} per-game stats from stats.nba.com...")
    stats = fetch_per_game_stats()

    table = build_top_players_table(stats)
    table.to_csv(CSV_PATH, index=False)
    print(f"Saved {len(table)} players to {CSV_PATH.relative_to(REPO_ROOT)}")

    plot_scoring_vs_efficiency(table)
    print(f"Saved plot to {PLOT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
