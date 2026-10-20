"""Export current model estimates and their provenance, without claiming validation."""

import hashlib
import json

from cyclorotor_sizing import CyclorotorAeroModel, CyclorotorGeometry
from project_config import BASELINE, CONFIG_PATH, ROOT, bom_rows


def main():
    model = CyclorotorAeroModel()
    geometry = CyclorotorGeometry(**BASELINE["geometry"])
    op = BASELINE["operating"]
    result = model.solve_hover_direction(
        geometry, op["rpm"], op["theta_0_deg"],
        thrust_direction_deg=op["thrust_direction_deg"],
        blockage_factor=op["blockage_factor"], pitch_schedule=op["pitch_schedule"],
    )
    report = {
        "status": BASELINE["status"], "revision": BASELINE["revision"],
        "config_sha256": hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest(),
        "solver_sha256": hashlib.sha256((ROOT / "scripts/cyclorotor_sizing.py").read_bytes()).hexdigest(),
        "baseline": BASELINE, "bom": bom_rows(BASELINE), "performance": result,
        "limitations": [
            "Empirical Re-independent analytical coefficients and continuous stall approximation",
            "Uniform inflow and empirical blockage; cyclic pitching not CFD validated",
            "Shaft mass from gross solid geometry; other BOM masses remain estimates",
            "CAD mass, structural, thermal and hardware verification pending",
        ],
    }
    directory = ROOT / "reports"
    directory.mkdir(exist_ok=True)
    (directory / "baseline.json").write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
    rows = [
        ("Vertical thrust", f"{result['thrust_Z_N']:.3f} N"),
        ("Horizontal thrust", f"{result['thrust_X_N']:.6f} N"),
        ("Electrical power", f"{result['P_elec_W']:.2f} W"),
        ("Figure of merit", f"{result['figure_of_merit']:.4f}"),
        ("Estimated mass", f"{geometry.total_module_mass * 1000:.3f} g"),
        ("Thrust / module weight", f"{result['tw_ratio']:.3f}"),
        ("Pitch phase for vertical thrust", f"{result['phi_0_deg']:.3f} deg"),
        ("Reynolds range", f"{result['min_Re']:.0f} to {result['max_Re']:.0f}"),
    ]
    text = "# Current preliminary calculation\n\n" + BASELINE["status"] + ".\n\n"
    text += "| Quantity | Estimate |\n| --- | ---: |\n"
    text += "\n".join(f"| {name} | {value} |" for name, value in rows)
    text += "\n\n" + "\n".join(f"- {item}" for item in report["limitations"]) + "\n"
    text += "\nRegenerate with `python scripts/generate_baseline_report.py`. Full inputs and hashes: [baseline.json](baseline.json).\n"
    (directory / "BASELINE.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
