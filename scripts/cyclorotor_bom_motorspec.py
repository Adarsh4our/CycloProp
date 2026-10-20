"""Generate the preliminary mass budget and model-based electrical demand.

Supplier ratings and procurement quotes remain in the historical Stage 1 package.
Masses other than the shaft are estimates pending CAD/material verification.
"""
import csv
from collections import defaultdict

import matplotlib.pyplot as plt

from cyclorotor_sizing import CyclorotorAeroModel, CyclorotorGeometry
from project_config import BASELINE, ROOT, bom_rows


def main():
    rows = bom_rows(BASELINE)
    total_mass_g = sum(r["total_mass_g"] for r in rows)
    target = ROOT / "reports"
    target.mkdir(exist_ok=True)
    with (target / "bom.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["component", "category", "quantity", "unit_mass_g", "total_mass_g"], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print("PRELIMINARY MASS BUDGET - CAD verification pending")
    for row in rows:
        print(f"{row['component']:<30} {row['quantity']:>2} x {row['unit_mass_g']:7.3f} g = {row['total_mass_g']:8.3f} g")
    print(f"Total: {total_mass_g:.3f} g; margin to 400 g: {400-total_mass_g:.3f} g")
    print("Shaft is gross solid-stock mass. Other components retain provisional estimates.")
    geom = CyclorotorGeometry(**BASELINE["geometry"])
    op = BASELINE["operating"]
    result = CyclorotorAeroModel().solve_hover_direction(
        geom, op["rpm"], op["theta_0_deg"], thrust_direction_deg=op["thrust_direction_deg"],
        blockage_factor=op["blockage_factor"], pitch_schedule=op["pitch_schedule"],
    )
    print(f"Model thrust: {result['thrust_N']:.3f} N; T/W: {result['tw_ratio']:.3f}")
    print(f"Model electrical power: {result['P_elec_W']:.2f} W; current at {op['battery_voltage']} V: {result['P_elec_W']/op['battery_voltage']:.2f} A")
    print("These estimates do not establish motor thermal, servo, structural or flight compliance.")
    categories = defaultdict(float)
    for row in rows:
        categories[row["category"]] += row["total_mass_g"]
    figure, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].barh(list(categories), list(categories.values()))
    axes[0].set_xlabel("Estimated mass (g)")
    axes[1].pie(list(categories.values()), labels=list(categories), autopct="%1.1f%%")
    figure.suptitle(f"Preliminary BOM: {total_mass_g:.1f} g - CAD verification pending")
    figure.tight_layout()
    destination = ROOT / "figures" / "corrected"
    destination.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination / "bom_budget_chart.png", dpi=180)
    plt.close(figure)


if __name__ == "__main__":
    main()
