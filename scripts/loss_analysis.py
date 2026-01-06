"""
Loss Analysis & Inefficiency Quantification
-------------------------------------------
Target: Henkel manufacturing performance analytics

This script quantifies operational losses related to
downtime, quality loss, and inefficient operating speeds.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# =========================
# Configuration
# =========================
DATA_PATH = Path("data/manufacturing_line_data.csv")
REPORTS_DIR = Path("reports")

ENERGY_COST_PER_KWH = 0.12    # EUR/kWh (example industrial rate)


# =========================
# Load Data
# =========================
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    df.set_index("timestamp", inplace=True)
    return df


# =========================
# Loss Calculations
# =========================
def compute_losses(df: pd.DataFrame):
    losses = {}

    # Energy wasted during downtime
    downtime_energy = df[df["downtime_flag"] == 1]["energy_kWh"].sum()
    losses["downtime_energy_kWh"] = downtime_energy
    losses["downtime_energy_cost_EUR"] = downtime_energy * ENERGY_COST_PER_KWH

    # Quality loss impact (proxy)
    avg_quality_loss = df["quality_loss_pct"].mean()
    losses["average_quality_loss_pct"] = avg_quality_loss

    # Speed vs quality trade-off
    high_speed = df[df["line_speed_mpm"] > 95]
    normal_speed = df[(df["line_speed_mpm"] > 70) & (df["line_speed_mpm"] <= 95)]

    losses["quality_loss_high_speed_pct"] = high_speed["quality_loss_pct"].mean()
    losses["quality_loss_normal_speed_pct"] = normal_speed["quality_loss_pct"].mean()

    return pd.DataFrame([losses])


# =========================
# Plotting
# =========================
def plot_speed_quality_tradeoff(df: pd.DataFrame):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.scatter(df["line_speed_mpm"], df["quality_loss_pct"], alpha=0.3)
    plt.xlabel("Line Speed (m/min)")
    plt.ylabel("Quality Loss (%)")
    plt.title("Speed vs Quality Loss Trade-off")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "speed_vs_quality.png")
    plt.close()


# =========================
# Main
# =========================
def main():
    print("Loading data...")
    df = load_data()

    print("Computing losses...")
    loss_df = compute_losses(df)

    print("Saving loss metrics...")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    loss_df.to_csv(REPORTS_DIR / "loss_analysis.csv", index=False)

    print("Generating plots...")
    plot_speed_quality_tradeoff(df)

    print("Loss analysis complete.")
    print(loss_df)


if __name__ == "__main__":
    main()
