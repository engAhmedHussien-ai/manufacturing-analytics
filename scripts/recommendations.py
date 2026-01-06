"""
Automated Operational Recommendations
-------------------------------------
Target: Henkel manufacturing analytics

This script converts analytical findings into
clear, actionable operational recommendations.
"""

import pandas as pd
from pathlib import Path


REPORTS_DIR = Path("reports")


def generate_recommendations():
    recommendations = []

    loss_df = pd.read_csv(REPORTS_DIR / "loss_analysis.csv")
    energy_kpis = pd.read_csv(REPORTS_DIR / "energy_sustainability_kpis.csv")

    # Downtime energy waste
    if loss_df["downtime_energy_kWh"].iloc[0] > 0:
        recommendations.append(
            "Reduce energy waste during downtime by improving shutdown procedures "
            "and minimizing idle energy consumption."
        )

    # Quality vs speed
    if loss_df["quality_loss_high_speed_pct"].iloc[0] > loss_df["quality_loss_normal_speed_pct"].iloc[0]:
        recommendations.append(
            "Avoid sustained operation above 95% line speed, as higher speeds "
            "significantly increase quality losses without proportional throughput gains."
        )

    # Energy intensity
    avg_energy_per_ton = energy_kpis["average_energy_per_ton"].iloc[0]
    if avg_energy_per_ton > energy_kpis["average_energy_per_ton"].median():
        recommendations.append(
            "Stabilize production around optimal operating points to reduce "
            "energy intensity and associated CO₂ emissions."
        )

    return recommendations


def main():
    recs = generate_recommendations()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPORTS_DIR / "RECOMMENDATIONS.txt"

    with open(output_path, "w") as f:
        for i, rec in enumerate(recs, 1):
            f.write(f"{i}. {rec}\n")

    print("Recommendations generated:")
    for r in recs:
        print(f"- {r}")


if __name__ == "__main__":
    main()
