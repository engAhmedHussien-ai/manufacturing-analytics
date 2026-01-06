"""
Line Performance & OEE-Style KPI Analysis
----------------------------------------
Target: Henkel manufacturing analytics

This script computes availability, performance,
and quality-related KPIs at line and shift level.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# =========================
# Configuration
# =========================
DATA_PATH = Path("data/manufacturing_line_data.csv")
REPORTS_DIR = Path("reports")

DESIGN_SPEED_MPM = 100        # Nominal design line speed
MINUTES_PER_SAMPLE = 1


# =========================
# Load Data
# =========================
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    df.set_index("timestamp", inplace=True)
    return df


# =========================
# KPI Calculations
# =========================
def compute_oee_kpis(df: pd.DataFrame) -> pd.DataFrame:
    total_time_min = len(df) * MINUTES_PER_SAMPLE
    runtime_min = (df["downtime_flag"] == 0).sum() * MINUTES_PER_SAMPLE

    availability = runtime_min / total_time_min

    actual_speed = df.loc[df["downtime_flag"] == 0, "line_speed_mpm"].mean()
    performance = actual_speed / DESIGN_SPEED_MPM

    quality = 1 - df["quality_loss_pct"].mean() / 100

    return pd.DataFrame([{
        "availability": availability,
        "performance": performance,
        "quality": quality
    }])


def compute_shift_kpis(df: pd.DataFrame) -> pd.DataFrame:
    results = []

    for shift, g in df.groupby("shift"):
        total_time = len(g) * MINUTES_PER_SAMPLE
        runtime = (g["downtime_flag"] == 0).sum() * MINUTES_PER_SAMPLE

        availability = runtime / total_time
        avg_speed = g.loc[g["downtime_flag"] == 0, "line_speed_mpm"].mean()
        performance = avg_speed / DESIGN_SPEED_MPM
        quality = 1 - g["quality_loss_pct"].mean() / 100

        results.append({
            "shift": shift,
            "availability": availability,
            "performance": performance,
            "quality": quality
        })

    return pd.DataFrame(results)


# =========================
# Plotting
# =========================
def plot_shift_comparison(shift_df: pd.DataFrame):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    shift_df.set_index("shift")[["availability", "performance", "quality"]].plot(
        kind="bar",
        figsize=(8, 5),
        ylim=(0, 1.1)
    )

    plt.title("OEE-Style KPIs by Shift")
    plt.ylabel("Ratio")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "shift_oee_comparison.png")
    plt.close()


# =========================
# Main
# =========================
def main():
    print("Loading data...")
    df = load_data()

    print("Computing line-level KPIs...")
    line_kpis = compute_oee_kpis(df)

    print("Computing shift-level KPIs...")
    shift_kpis = compute_shift_kpis(df)

    print("Saving KPI tables...")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    line_kpis.to_csv(REPORTS_DIR / "line_oee_kpis.csv", index=False)
    shift_kpis.to_csv(REPORTS_DIR / "shift_oee_kpis.csv", index=False)

    print("Generating plots...")
    plot_shift_comparison(shift_kpis)

    print("OEE-style analysis complete.")
    print("\nLine KPIs:")
    print(line_kpis)
    print("\nShift KPIs:")
    print(shift_kpis)


if __name__ == "__main__":
    main()
