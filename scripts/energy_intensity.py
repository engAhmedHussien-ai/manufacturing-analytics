"""
Energy Intensity & Sustainability KPI Analysis
----------------------------------------------
Target: Henkel manufacturing & sustainability analytics

This script evaluates energy efficiency, peak tariff exposure,
and CO2 proxy indicators based on production output.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# =========================
# Configuration
# =========================
DATA_PATH = Path("data/manufacturing_line_data.csv")
REPORTS_DIR = Path("reports")

CO2_FACTOR_KG_PER_KWH = 0.42   # typical grid emission factor
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
def compute_energy_kpis(df: pd.DataFrame):
    # Remove downtime samples
    runtime_df = df[df["downtime_flag"] == 0]

    kpis = {
        "total_energy_kWh": runtime_df["energy_kWh"].sum(),
        "total_throughput_ton": runtime_df["throughput_kg_h"].sum() / 1000,
        "average_energy_per_ton": runtime_df["energy_per_ton"].mean(),
        "peak_energy_kWh": runtime_df[runtime_df["tariff"] == "peak"]["energy_kWh"].sum(),
        "offpeak_energy_kWh": runtime_df[runtime_df["tariff"] == "off-peak"]["energy_kWh"].sum(),
    }

    kpis["co2_emissions_kg"] = kpis["total_energy_kWh"] * CO2_FACTOR_KG_PER_KWH

    return pd.DataFrame([kpis])


def compute_shift_energy(df: pd.DataFrame):
    results = []

    for shift, g in df[df["downtime_flag"] == 0].groupby("shift"):
        energy = g["energy_kWh"].sum()
        throughput = g["throughput_kg_h"].sum() / 1000
        energy_per_ton = energy / throughput if throughput > 0 else None

        results.append({
            "shift": shift,
            "energy_kWh": energy,
            "throughput_ton": throughput,
            "energy_per_ton": energy_per_ton
        })

    return pd.DataFrame(results)


# =========================
# Plotting
# =========================
def plot_energy_intensity(df: pd.DataFrame):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    df_runtime = df[df["downtime_flag"] == 0]

    plt.figure(figsize=(10, 4))
    plt.plot(df_runtime.index, df_runtime["energy_per_ton"])
    plt.title("Energy Intensity (kWh / ton)")
    plt.ylabel("kWh / ton")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "energy_per_ton_trend.png")
    plt.close()


def plot_tariff_split(kpi_df: pd.DataFrame):
    plt.figure(figsize=(5, 4))
    plt.bar(
        ["Peak", "Off-Peak"],
        [
            kpi_df["peak_energy_kWh"].iloc[0],
            kpi_df["offpeak_energy_kWh"].iloc[0],
        ],
    )
    plt.title("Energy Consumption by Tariff")
    plt.ylabel("kWh")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "tariff_energy_split.png")
    plt.close()


# =========================
# Main
# =========================
def main():
    print("Loading data...")
    df = load_data()

    print("Computing energy & sustainability KPIs...")
    energy_kpis = compute_energy_kpis(df)
    shift_energy = compute_shift_energy(df)

    print("Saving KPI tables...")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    energy_kpis.to_csv(REPORTS_DIR / "energy_sustainability_kpis.csv", index=False)
    shift_energy.to_csv(REPORTS_DIR / "shift_energy_intensity.csv", index=False)

    print("Generating plots...")
    plot_energy_intensity(df)
    plot_tariff_split(energy_kpis)

    print("Energy intensity analysis complete.")
    print("\nEnergy KPIs:")
    print(energy_kpis)
    print("\nShift Energy Intensity:")
    print(shift_energy)


if __name__ == "__main__":
    main()
