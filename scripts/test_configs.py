"""Configuration exploration using the production solver; see tests/ for regressions."""
from dataclasses import replace

from cyclorotor_sizing import CyclorotorAeroModel, CyclorotorGeometry
from project_config import BASELINE


def main():
    baseline = CyclorotorGeometry(**BASELINE["geometry"])
    model = CyclorotorAeroModel()
    configs = {
        "compact": replace(baseline, radius=0.085, span=0.200, chord=0.035),
        "baseline": baseline,
        "larger": replace(baseline, radius=0.100, span=0.230, chord=0.040),
        "wide": replace(baseline, radius=0.090, span=0.240, chord=0.036),
    }
    print("Preliminary model estimates; variant masses are not recalculated")
    print("Configuration RPM Thrust_N Electrical_W FM")
    for name, geometry in configs.items():
        for rpm in (2000, 2200, 2400, 2600, 2800):
            result = model.solve_hover_direction(geometry, rpm, BASELINE["operating"]["theta_0_deg"],
                                                 blockage_factor=BASELINE["operating"]["blockage_factor"])
            print(f"{name:12} {rpm:4} {result['thrust_N']:8.3f} {result['P_elec_W']:10.2f} {result['figure_of_merit']:6.3f}")


if __name__ == "__main__":
    main()
