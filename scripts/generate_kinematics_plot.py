"""Plot the current model's pitch and section aerodynamics at vertical thrust."""
import numpy as np
import matplotlib.pyplot as plt

from cyclorotor_sizing import CyclorotorAeroModel, CyclorotorGeometry
from project_config import BASELINE, ROOT


def main():
    model = CyclorotorAeroModel()
    geometry = CyclorotorGeometry(**BASELINE["geometry"])
    op = BASELINE["operating"]
    state = model.solve_hover_direction(
        geometry, op["rpm"], op["theta_0_deg"], thrust_direction_deg=op["thrust_direction_deg"],
        blockage_factor=op["blockage_factor"], pitch_schedule=op["pitch_schedule"],
    )
    azimuth = model.evaluate_azimuth(
        geometry, op["rpm"], op["theta_0_deg"], phi_0_deg=state["phi_0_deg"],
        v_i=state["inflow_XZ"], pitch_schedule=op["pitch_schedule"],
    )
    fig, axes = plt.subplots(2, 1, figsize=(11, 8))
    for blade in range(geometry.num_blades):
        shift = blade * len(azimuth["psi"]) // geometry.num_blades
        axes[0].plot(azimuth["psi_deg"], np.roll(azimuth["theta_deg"], shift), label=f"Blade {blade+1}")
    axes[0].set_ylabel("Pitch (deg)")
    axes[0].legend()
    axes[1].plot(azimuth["psi_deg"], azimuth["alpha_eff_deg"], color="tab:blue", label="Effective angle")
    axes[1].set_ylabel("Effective angle (deg)")
    right = axes[1].twinx()
    right.plot(azimuth["psi_deg"], azimuth["cl"], color="tab:orange", label="Lift coefficient")
    right.set_ylabel("Lift coefficient")
    for ax in axes:
        ax.set_xlabel("Azimuth (deg): 0 = +X, 90 = +Z")
        ax.grid(alpha=0.3)
    fig.suptitle(f"Preliminary analytical model - {op['rpm']:g} RPM, phase {state['phi_0_deg']:.2f} deg")
    fig.tight_layout()
    destination = ROOT / "figures" / "corrected"
    destination.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination / "Fig_Kinematics_Plot.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
