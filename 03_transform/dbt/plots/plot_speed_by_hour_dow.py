"""Heatmap of avg_speed_mph by hour of day x day of week, from fct_trips.

Answers QUESTIONS.md #5 — does speed (a congestion proxy) track known NYC
traffic patterns, slower during rush hours and faster overnight?

Run `dbt build` first so fct_trips exists in nyc_taxi.duckdb, then:

    python plot_speed_by_hour_dow.py
"""

import logging
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import seaborn as sns

DB_PATH = Path(__file__).parent / "../nyc_taxi.duckdb"
OUTPUT_PATH = Path(__file__).parent / "speed_by_hour_dow.png"
LOG_PATH = Path(__file__).parent / "plot_speed_by_hour_dow.log"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

# isodow: 1=Monday ... 7=Sunday, so the pivoted heatmap reads Mon->Sun top to bottom
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute(
        """
        select
            isodow(pickup_at) as day_of_week,
            hour(pickup_at)   as hour_of_day,
            avg(avg_speed_mph) as avg_speed_mph
        from fct_trips
        group by 1, 2
        order by 1, 2
        """
    ).df()
    con.close()

    pivot = df.pivot(index="day_of_week", columns="hour_of_day", values="avg_speed_mph")
    pivot.index = [DAY_NAMES[d - 1] for d in pivot.index]

    sns.set_theme(style="white")
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(
        pivot,
        cmap="RdYlGn",
        annot=True,
        fmt=".1f",
        linewidths=0.5,
        cbar_kws={"label": "Avg Speed (mph)"},
        ax=ax,
    )

    ax.set_title("NYC Yellow Taxi Avg Speed by Hour of Day and Day of Week (2025)")
    ax.set_xlabel("Pickup Hour (0-23)")
    ax.set_ylabel("Day of Week")

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=150)
    print(f"Saved plot to {OUTPUT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("plot_speed_by_hour_dow failed")
        raise


