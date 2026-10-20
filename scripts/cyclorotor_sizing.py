"""
CycloProp: Advanced Cycloidal Rotor Sizing & Aerodynamic Performance Model
==========================================================================
Project Context: PUSHPAK Grand Challenge 2026 (MeitY / IIT Bombay Drone Centre)
Target Requirements:
  - Net Thrust F_T >= 10 N (Baseline design target: 12 - 15 N)
  - Thrust-to-Weight Ratio T/W > 2.5 (Target T/W >= 3.5)
  - Total Module Mass <= 400 g (Design target: 280 - 320 g)
  - 4-blade cycloidal rotor undergoing cyclic pitch: theta(psi) = theta_0 * sin(psi - phi_0)

Key Aerodynamic Features:
  1. Preliminary blade-element model with uniform vector momentum inflow.
  2. Curvilinear flow virtual camber correction: kappa = c / (2R) -> delta_alpha = c / (4R).
  3. Dynamic pitch-rate damping & virtual pitching effect.
  4. Empirical instantaneous stall-delay approximation; not a validated unsteady model.
  5. 3D finite aspect ratio tip-loss & induced drag polar correction (C_Di = C_L^2 / (pi * AR * e)).
  6. Endplate parasitic friction & shaft bearing tare torque modeling.
  7. Multi-variable parametric sweeps (Radius, Span, Chord, RPM, Pitch Amplitude).
  8. Dynamic blade hinge moment & cyclic pitch servo torque analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, replace
from typing import Dict, List, Tuple, Optional
from project_config import BASELINE, ROOT


class ConvergenceError(RuntimeError):
    """The induced-flow or thrust-direction iteration did not converge."""


class InvalidPerformanceError(RuntimeError):
    """The calculated power fails the model's hover consistency checks."""

# Matplotlib formatting for publication-grade figures
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'sans-serif',
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 14,
    'lines.linewidth': 2.0,
    'grid.alpha': 0.4,
    'grid.linestyle': '--'
})


@dataclass
class CyclorotorGeometry:
    """Rotor geometric parameters."""
    radius: float       # Rotor radius R [m]
    span: float         # Blade span b [m]
    chord: float        # Blade chord c [m]
    num_blades: int = 4 # Number of blades N
    airfoil: str = BASELINE["geometry"]["airfoil"]
    pivot_ratio: float = 0.25 # Pivot axis location from leading edge (x/c)
    blade_mass_each: float = 0.0125 # Mass of single blade [kg] (12.5 g)
    total_module_mass: float = BASELINE["geometry"]["total_module_mass"]

    def __post_init__(self):
        for name in ("radius", "span", "chord", "blade_mass_each", "total_module_mass"):
            value = getattr(self, name)
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if not isinstance(self.num_blades, int) or self.num_blades < 1:
            raise ValueError("num_blades must be a positive integer")
        if not np.isfinite(self.pivot_ratio) or not 0 <= self.pivot_ratio <= 1:
            raise ValueError("pivot_ratio must be between zero and one")

    @property
    def diameter(self) -> float:
        return 2.0 * self.radius

    @property
    def swept_area(self) -> float:
        """Projected frontal swept area A = 2 * R * b [m^2]."""
        return 2.0 * self.radius * self.span

    @property
    def solidity(self) -> float:
        """Rotor solidity sigma = N * c / (pi * R)."""
        return (self.num_blades * self.chord) / (np.pi * self.radius)

    @property
    def aspect_ratio(self) -> float:
        """Blade aspect ratio AR = b / c."""
        return self.span / self.chord

    @property
    def virtual_camber(self) -> float:
        """Virtual camber ratio kappa = c / (2 * R)."""
        return self.chord / (2.0 * self.radius)

    @property
    def virtual_alpha_camber(self) -> float:
        """Effective virtual zero-lift AoA shift (rad) due to circular flow curvature."""
        return self.chord / (4.0 * self.radius)


class CyclorotorAeroModel:
    """
    Aerodynamic, Kinematic, and Power Solver for Cycloidal Rotors.
    """
    def __init__(self, rho: float = BASELINE["fluid"]["rho"],
                 mu: float = BASELINE["fluid"]["mu"]):
        if not np.isfinite(rho) or not np.isfinite(mu) or rho <= 0 or mu <= 0:
            raise ValueError("Density and viscosity must be finite and positive")
        self.rho = rho          # Air density [kg/m^3]
        self.mu = mu            # Dynamic viscosity [Pa*s]
        self.eta_motor = BASELINE["efficiencies"]["motor"]
        self.eta_mech = BASELINE["efficiencies"]["mechanical"]
        self.eta_esc = BASELINE["efficiencies"]["esc"]
        self.e_oswald = 0.85    # Oswald span efficiency factor
        self.tip_loss_factor = 0.90 # Tip-loss factor with endplate tip-vortex mitigation

    def get_airfoil_polars(self, alpha_eff: np.ndarray, Re: np.ndarray, 
                           k_reduced: np.ndarray, dalpha_dt: np.ndarray,
                           aspect_ratio: float,
                           airfoil: str = "NACA 0015") -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate Lift, Drag, and Pitching Moment coefficients including Dynamic Stall delay and 3D induced drag.
        Supports: 'NACA 0015' (standard), 'NACA 0012' (reduced profile drag), 'Eppler E374' (low-Re laminar bucket).
        """
        if airfoil == "NACA 0012":
            alpha_ss_deg = 12.8  # Static stall angle [deg]
            cl_alpha_2d = 2.0 * np.pi * 0.91  # Slender boundary layer slope
            cd0 = 0.016  # Reduced profile drag at t/c = 12%
            cd_profile_quad = 1.15
        elif airfoil in ["Eppler E374", "E374"]:
            alpha_ss_deg = 13.0
            cl_alpha_2d = 2.0 * np.pi * 0.92
            cd0 = 0.013  # Low-drag laminar bucket at Re ~ 100,000
            cd_profile_quad = 1.05
        elif airfoil == "NACA 0015":
            alpha_ss_deg = 13.5  # Static stall angle [deg]
            cl_alpha_2d = 2.0 * np.pi * 0.88  # 2D lift curve slope with low-Re viscous boundary layer deficit
            cd0 = 0.020  # Base zero-lift profile drag coefficient at Re ~ 100,000
            cd_profile_quad = 1.25
        else:
            raise ValueError(f"No analytical polar for {airfoil!r}; supply accepted CFD data")

        alpha_ss = np.radians(alpha_ss_deg)

        # Dynamic Stall Angle & Cl_max enhancement (modified Leishman-Beddoes / Gormont model)
        gamma = 0.75
        delta_alpha_ds = gamma * np.sqrt(np.clip(k_reduced, 0.0, 0.25)) * np.sign(dalpha_dt)
        alpha_ds = alpha_ss + np.abs(delta_alpha_ds)

        cl = np.zeros_like(alpha_eff)
        cd = np.zeros_like(alpha_eff)
        cm = np.zeros_like(alpha_eff)

        for i in range(len(alpha_eff)):
            a = alpha_eff[i]
            abs_a = np.abs(a)
            sgn = np.sign(a) if a != 0 else 1.0
            a_ds = alpha_ds[i]

            if abs_a <= a_ds:
                # Pre-stall linear / weakly non-linear regime with 3D tip loss
                cl_2d = cl_alpha_2d * a
                cl[i] = self.tip_loss_factor * cl_2d
                # Profile drag + 3D induced drag
                cd_profile = cd0 + cd_profile_quad * (a ** 2)
                cd_induced = (cl[i] ** 2) / (np.pi * aspect_ratio * self.e_oswald)
                cd[i] = cd_profile + cd_induced
                cm[i] = -0.05 * a  # Pitch damping about quarter-chord
            else:
                # Empirical continuous join; calibration against unsteady data is pending.
                cl_max_dyn = self.tip_loss_factor * cl_alpha_2d * a_ds
                cd_max = 1.60
                delta = abs_a - a_ds
                attached_weight = np.exp(-1.4 * delta)
                cl[i] = sgn * (cl_max_dyn * np.cos(delta) * attached_weight +
                                0.5 * cd_max * np.sin(2.0 * abs_a) * (1 - attached_weight))
                cd_profile = cd0 + (attached_weight * cd_profile_quad * a_ds**2 +
                                    (1 - attached_weight) * (cd_max - cd0) * np.sin(abs_a)**2)
                cd_induced = (cl[i] ** 2) / (np.pi * aspect_ratio * self.e_oswald)
                cd[i] = cd_profile + cd_induced
                cm[i] = -sgn * (0.05 * a_ds * attached_weight + 0.22 * np.sin(delta))

        return cl, cd, cm

    def evaluate_azimuth(self, geom: CyclorotorGeometry, rpm: float, 
                          theta_0_deg: float, phi_0_deg: float = 0.0,
                          v_i: float = 0.0, num_azimuth: int = 360,
                          pitch_schedule: str = "sinusoidal") -> Dict[str, np.ndarray]:
        """
        Evaluate full revolution kinematics and blade forces across azimuth psi in [0, 2*pi].
        Supports 'sinusoidal' (standard eccentric ring) and 'asymmetric_cam' (higher-harmonic dwell).
        """
        if not all(np.isfinite(v) for v in (rpm, theta_0_deg, phi_0_deg)) or rpm <= 0:
            raise ValueError("RPM must be positive and operating inputs finite")
        if not 0 <= theta_0_deg < 90:
            raise ValueError("Pitch amplitude must be in [0, 90) degrees")
        if not isinstance(num_azimuth, int) or num_azimuth < 8 or num_azimuth % geom.num_blades:
            raise ValueError("Azimuth count must be >= 8 and divisible by blade count")
        if pitch_schedule not in ("sinusoidal", "asymmetric_cam"):
            raise ValueError(f"Unknown pitch schedule: {pitch_schedule}")
        # v_i is opposite the air velocity, in global (X, Z). Scalar callers
        # explicitly request vertical inflow; solved states use both components.
        inflow = np.array([0.0, v_i] if np.ndim(v_i) == 0 else v_i, dtype=float)
        if inflow.shape != (2,) or not np.all(np.isfinite(inflow)):
            raise ValueError("Induced velocity must be a finite scalar or (X, Z) pair")
        omega = 2.0 * np.pi * rpm / 60.0  # Rotational velocity [rad/s]
        theta_0 = np.radians(theta_0_deg)
        phi_0 = np.radians(phi_0_deg)
        
        psi = np.linspace(0, 2.0 * np.pi, num_azimuth, endpoint=False)
        dpsi = psi[1] - psi[0]
        dt = dpsi / omega

        if pitch_schedule == "asymmetric_cam":
            # Higher-harmonic cam profile with extended dwell on the advancing stroke
            # 3rd harmonic adds flattened dwell at peak pitch; cosine term biases advancing arc
            raw_cam = np.sin(psi - phi_0) + 0.15 * np.sin(3.0 * (psi - phi_0))
            theta = theta_0 * (raw_cam / np.max(np.abs(raw_cam)))
            dtheta_dpsi = (np.roll(theta, -1) - np.roll(theta, 1)) / (2 * dpsi)
            dtheta_dt = omega * dtheta_dpsi
            d2theta_dt2 = (np.roll(dtheta_dt, -1) - np.roll(dtheta_dt, 1)) / (2 * dt)
        else:
            # Pure sinusoidal eccentric ring
            theta = theta_0 * np.sin(psi - phi_0)
            dtheta_dpsi = theta_0 * np.cos(psi - phi_0)
            dtheta_dt = omega * dtheta_dpsi
            d2theta_dt2 = - (omega ** 2) * theta

        # Tangential and radial velocity components of oncoming flow relative to blade:
        # Rotation is CCW; at psi=0 (3 o'clock), blade moves along +Z.
        # Flow blows against motion (+V_flow_T along tangent) and downward (+Z thrust -> -Z induced downwash).
        V_flow_T = omega * geom.radius - inflow[0] * np.sin(psi) + inflow[1] * np.cos(psi)
        V_flow_N = inflow[0] * np.cos(psi) + inflow[1] * np.sin(psi)
        
        U_rel = np.sqrt(V_flow_T**2 + V_flow_N**2)
        phi_inf = np.arctan2(V_flow_N, V_flow_T)

        # Geometric Angle of Attack
        alpha_geom = theta - phi_inf

        # Curvilinear Virtual Camber Correction
        delta_alpha_camber = geom.virtual_alpha_camber

        # Virtual Pitch Rate Effect
        delta_alpha_rate = (geom.chord / (2.0 * np.maximum(U_rel, 1.0))) * dtheta_dt

        # Total Effective Angle of Attack
        alpha_eff = alpha_geom + delta_alpha_camber + delta_alpha_rate
        # Periodic central difference avoids a special derivative at the seam.
        dalpha_dt = (np.roll(alpha_eff, -1) - np.roll(alpha_eff, 1)) / (2 * dt)

        # Reduced frequency k = |dalpha/dt| * c / (2 * U_rel)
        k_reduced = np.abs(dalpha_dt) * geom.chord / (2.0 * np.maximum(U_rel, 1.0))

        # Reynolds number
        Re = (self.rho * U_rel * geom.chord) / self.mu

        # Aerodynamic Polars with 3D effects
        cl, cd, cm = self.get_airfoil_polars(alpha_eff, Re, k_reduced, dalpha_dt, geom.aspect_ratio, airfoil=geom.airfoil)

        # Dynamic Pressure q = 0.5 * rho * U_rel^2
        q = 0.5 * self.rho * (U_rel ** 2)
        blade_area = geom.chord * geom.span

        # Section Aerodynamic Forces
        dL = q * blade_area * cl
        dD = q * blade_area * cd
        dM_pitch = q * blade_area * geom.chord * cm

        # Force decomposition in blade coordinate system:
        # Tangential force Ft (along motion tangent): drag and induced downwash oppose motion
        # Normal force Fn (radially outward): lift acts outward/inward
        Ft = - dL * np.sin(phi_inf) - dD * np.cos(phi_inf)
        Fn =   dL * np.cos(phi_inf) - dD * np.sin(phi_inf)

        # Global Cartesian Forces: X (horizontal right) and Z (vertical upward)
        # Position: X = R*cos(psi), Z = R*sin(psi)
        # Tangent: t_hat = [-sin(psi), cos(psi)], Normal: n_hat = [cos(psi), sin(psi)]
        F_X_single = -Ft * np.sin(psi) + Fn * np.cos(psi)
        F_Z_single =  Ft * np.cos(psi) + Fn * np.sin(psi)

        # Shaft Torque resisting rotation: Q_single = - Ft * R > 0
        Q_single = - Ft * geom.radius

        # Total multi-blade integration (summing all N blades shifted by 2*pi/N)
        F_X_multi = np.zeros_like(psi)
        F_Z_multi = np.zeros_like(psi)
        Q_multi = np.zeros_like(psi)

        for k in range(geom.num_blades):
            shift = int(k * num_azimuth / geom.num_blades)
            F_X_multi += np.roll(F_X_single, shift)
            F_Z_multi += np.roll(F_Z_single, shift)
            Q_multi += np.roll(Q_single, shift)

        # Endplate & Hub Disk Parasitic Friction Torque:
        # C_f_endplate ~ 0.005 for carbon disk spinning at omega in air
        Q_endplates = 2.0 * (0.5 * 0.005 * self.rho * ((omega * geom.radius) ** 2) * (np.pi * (geom.radius ** 2)) * geom.radius)
        Q_multi += Q_endplates

        # Blade Inertial Pitching Moment (for servo sizing):
        I_blade = (1.0 / 12.0) * geom.blade_mass_each * (geom.chord ** 2)
        M_inertial = I_blade * d2theta_dt2
        M_pitch_total = dM_pitch - M_inertial

        return {
            'psi': psi,
            'psi_deg': np.degrees(psi),
            'theta_deg': np.degrees(theta),
            'alpha_eff_deg': np.degrees(alpha_eff),
            'U_rel': U_rel,
            'Re': Re,
            'dL': dL,
            'dD': dD,
            'cl': cl,
            'cd': cd,
            'F_X_single': F_X_single,
            'F_Z_single': F_Z_single,
            'F_X_multi': F_X_multi,
            'F_Z_multi': F_Z_multi,
            'Q_multi': Q_multi,
            'M_pitch_single': M_pitch_total,
            'omega': omega,
            'v_i': float(np.linalg.norm(inflow)),
            'inflow_XZ': inflow
        }

    def solve_hover_state(self, geom: CyclorotorGeometry, rpm: float, 
                          theta_0_deg: float, phi_0_deg: float = 0.0,
                          pitch_schedule: str = "sinusoidal",
                          blockage_factor: float = BASELINE["operating"]["blockage_factor"],
                          max_iter: int = 200, tol: float = 1e-6,
                          strict: bool = True) -> Dict[str, float]:
        """
        Solve self-consistent hover induced velocity v_i and rotor performance metrics.
        Includes aerodynamic blockage factor from frame structure and supports non-sinusoidal cam scheduling.
        """
        if not np.isfinite(blockage_factor) or not 0 < blockage_factor <= 1:
            raise ValueError("blockage_factor must be in (0, 1]")
        if not isinstance(max_iter, int) or max_iter < 1 or not np.isfinite(tol) or tol <= 0:
            raise ValueError("Iteration limit and tolerance must be positive")
        phase = np.radians(phi_0_deg)
        inflow = 3.5 * np.array([-np.sin(phase), np.cos(phase)])
        relaxation = 0.2
        for iteration in range(1, max_iter + 1):
            res = self.evaluate_azimuth(
                geom, rpm, theta_0_deg, phi_0_deg, v_i=inflow, pitch_schedule=pitch_schedule
            )
            force = np.array([np.mean(res['F_X_multi']), np.mean(res['F_Z_multi'])])
            magnitude = np.linalg.norm(force)
            if not np.isfinite(magnitude):
                raise ConvergenceError("Nonfinite blade force during inflow iteration")
            target = (force / np.sqrt(2 * self.rho * geom.swept_area * magnitude)
                      if magnitude > 1e-12 else np.zeros(2))
            residual = float(np.linalg.norm(target - inflow))
            if residual < tol:
                break
            inflow += relaxation * (target - inflow)
        else:
            raise ConvergenceError(
                f"Inflow did not converge after {max_iter} iterations; residual={residual:.6g} m/s"
            )
        v_i = float(np.linalg.norm(inflow))
        F_X_raw = float(np.mean(res['F_X_multi']))
        F_Z_raw = float(np.mean(res['F_Z_multi']))
        F_net_raw = float(np.sqrt(F_X_raw**2 + F_Z_raw**2))
        Q_mean = float(np.mean(res['Q_multi']))
        
        # Apply structural aerodynamic blockage factor (e.g. 0.92 unfaired cage, 0.96 faired)
        F_net = F_net_raw * blockage_factor
        F_X_mean = F_X_raw * blockage_factor
        F_Z_mean = F_Z_raw * blockage_factor

        # Aerodynamic and Electrical Power
        omega = 2.0 * np.pi * rpm / 60.0
        P_aero = Q_mean * omega  # Total aerodynamic power [W]
        P_induced = F_net * v_i  # Induced power [W]
        P_profile = P_aero - P_induced
        
        # Ideal momentum power
        P_ideal = (F_net ** 1.5) / np.sqrt(2.0 * self.rho * geom.swept_area)
        figure_of_merit = float(P_ideal / P_aero) if P_aero != 0 else float("nan")
        physical_consistent = bool(
            np.isfinite(figure_of_merit) and P_aero > 0
            and 0 <= figure_of_merit <= 1 and P_profile >= -1e-6
        )
        if strict and not physical_consistent:
            raise InvalidPerformanceError(
                f"Invalid hover power: P={P_aero:.6g} W, FM={figure_of_merit:.6g}, "
                f"profile power={P_profile:.6g} W"
            )

        # Electrical power consumed from battery
        P_elec = P_aero / (self.eta_motor * self.eta_mech * self.eta_esc)
        
        # Power loading (g/W)
        thrust_grams = (F_net / 9.80665) * 1000.0
        power_loading_aero = thrust_grams / np.maximum(P_aero, 1e-3)
        power_loading_elec = thrust_grams / np.maximum(P_elec, 1e-3)

        # Thrust-to-weight ratio
        tw_ratio = F_net / (geom.total_module_mass * 9.80665)

        # Peak blade pitching moment (for servo sizing)
        max_M_pitch_single = float(np.max(np.abs(res['M_pitch_single'])))

        return {
            'rpm': rpm,
            'theta_0_deg': theta_0_deg,
            'thrust_N': F_net,
            'thrust_raw_N': F_net_raw,
            'blockage_factor': blockage_factor,
            'thrust_X_N': F_X_mean,
            'thrust_Z_N': F_Z_mean,
            'thrust_grams': thrust_grams,
            'v_i': float(v_i),
            'inflow_XZ': inflow.tolist(),
            'phi_0_deg': float(phi_0_deg),
            'thrust_direction_deg': float(np.degrees(np.arctan2(F_X_mean, F_Z_mean))),
            'converged': True,
            'iterations': iteration,
            'inflow_residual_m_s': residual,
            'physical_consistent': physical_consistent,
            'validation_status': 'preliminary model; aerodynamic validation pending',
            'polar_model': 'empirical Re-independent analytical approximation',
            'torque_Nm': Q_mean,
            'P_aero_W': P_aero,
            'P_induced_W': P_induced,
            'P_profile_W': P_profile,
            'P_elec_W': P_elec,
            'figure_of_merit': figure_of_merit,
            'power_loading_elec_g_W': power_loading_elec,
            'power_loading_aero_g_W': power_loading_aero,
            'tw_ratio': tw_ratio,
            'max_pitch_moment_Nm': max_M_pitch_single,
            'tip_speed_m_s': float(omega * geom.radius),
            'mean_Re': float(np.mean(res['Re'])),
            'min_Re': float(np.min(res['Re'])),
            'max_Re': float(np.max(res['Re'])),
            'min_alpha_deg': float(np.min(res['alpha_eff_deg'])),
            'max_alpha_deg': float(np.max(res['alpha_eff_deg'])),
            'pitch_schedule': pitch_schedule,
            'airfoil': geom.airfoil
        }

    def solve_hover_direction(self, geom, rpm, theta_0_deg,
                              thrust_direction_deg=0.0, **kwargs):
        """Calibrate phase for a requested direction: 0 = +Z, 90 = +X.

        The uniform-inflow model is rotationally invariant. Re-evaluation
        checks the phase adjustment against finite azimuth discretization.
        """
        if not np.isfinite(thrust_direction_deg):
            raise ValueError("Thrust direction must be finite")
        phase = 0.0
        for _ in range(12):
            result = self.solve_hover_state(geom, rpm, theta_0_deg, phi_0_deg=phase, **kwargs)
            if result["thrust_N"] < 1e-8:
                raise ConvergenceError("Thrust direction is undefined at zero thrust")
            error = (result["thrust_direction_deg"] - thrust_direction_deg + 180) % 360 - 180
            if abs(error) < 1e-3:
                return result
            phase += error
        raise ConvergenceError("Pitch phase did not reach the requested thrust direction")


def run_parametric_sweeps(save_dir: str = "figures") -> Dict[str, any]:
    """
    Execute comprehensive multi-variable sweeps and export publication figures.
    """
    os.makedirs(save_dir, exist_ok=True)
    aero = CyclorotorAeroModel()

    # Recommended Baseline Geometry (Rev 3.0)
    baseline_geom = CyclorotorGeometry(**BASELINE["geometry"])

    print("=" * 80)
    print("CYCLOPROP BASELINE GEOMETRIC SPECIFICATIONS:")
    print(f"  - Rotor Radius (R):        {baseline_geom.radius * 1000:.1f} mm (Diameter: {baseline_geom.diameter * 1000:.1f} mm)")
    print(f"  - Blade Span (b):          {baseline_geom.span * 1000:.1f} mm")
    print(f"  - Blade Chord (c):         {baseline_geom.chord * 1000:.1f} mm")
    print(f"  - Number of Blades (N):    {baseline_geom.num_blades}")
    print(f"  - Rotor Solidity (sigma):  {baseline_geom.solidity:.3f} (Target optimal range: 0.50 - 0.85)")
    print(f"  - Aspect Ratio (AR):       {baseline_geom.aspect_ratio:.2f} (Target: 5 - 8)")
    print(f"  - Virtual Camber (kappa):  {baseline_geom.virtual_camber:.3f}")
    print(f"  - Total Module Mass:       {baseline_geom.total_module_mass * 1000:.1f} g (Target: 280 - 320 g)")
    print("=" * 80)

    # -------------------------------------------------------------
    # 1. Sweep 1: Thrust & Power vs RPM for various Pitch Amplitudes
    # -------------------------------------------------------------
    rpm_range = np.linspace(1800, 3000, 25)
    pitch_amplitudes = [25.0, 30.0, 35.0, 40.0]
    
    sweep_pitch_results = {th0: [] for th0 in pitch_amplitudes}
    for th0 in pitch_amplitudes:
        for rpm in rpm_range:
            res = aero.solve_hover_direction(baseline_geom, rpm, theta_0_deg=th0)
            sweep_pitch_results[th0].append(res)

    # Plot 1: Thrust vs RPM & Power vs Thrust
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    colors = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd']

    for idx, th0 in enumerate(pitch_amplitudes):
        thrusts = [r['thrust_N'] for r in sweep_pitch_results[th0]]
        ax1.plot(rpm_range, thrusts, label=f'$\\theta_0 = {th0}^\\circ$', color=colors[idx], marker='o', markersize=4)

    ax1.axhline(y=10.0, color='black', linestyle='--', linewidth=1.5, label='Min Required (10 N)')
    ax1.axhline(y=12.0, color='green', linestyle=':', linewidth=1.5, label='Baseline Design Target (12 N)')
    ax1.axhline(y=15.0, color='purple', linestyle='-.', linewidth=1.2, label='Max Thrust Margin (15 N)')
    ax1.set_xlabel('Rotor Speed (RPM)')
    ax1.set_ylabel('Net Thrust $F_T$ (N)')
    ax1.set_title('Thrust vs. Rotor RPM across Cyclic Pitch Amplitude')
    ax1.grid(True)
    ax1.legend(loc='upper left')

    for idx, th0 in enumerate(pitch_amplitudes):
        thrusts = [r['thrust_N'] for r in sweep_pitch_results[th0]]
        p_elec = [r['P_elec_W'] for r in sweep_pitch_results[th0]]
        ax2.plot(thrusts, p_elec, label=f'$\\theta_0 = {th0}^\\circ$', color=colors[idx], marker='s', markersize=4)

    ax2.axvline(x=10.0, color='black', linestyle='--', linewidth=1.5, label='10 N Thrust')
    ax2.axvline(x=12.0, color='green', linestyle=':', linewidth=1.5, label='12 N Baseline')
    ax2.set_xlabel('Net Thrust $F_T$ (N)')
    ax2.set_ylabel('Total Electrical Power $P_{\\mathrm{elec}}$ (W)')
    ax2.set_title('Electrical Power Required vs. Net Thrust')
    ax2.grid(True)
    ax2.legend(loc='upper left')

    plt.tight_layout()
    fig_path1 = os.path.join(save_dir, 'thrust_power_vs_rpm.png')
    plt.savefig(fig_path1, dpi=300)
    plt.close()
    print(f"[SAVED] {fig_path1}")

    # -------------------------------------------------------------
    # 2. Sweep 2: Azimuth Kinematics & Aerodynamic State (at 12 N Hover)
    # -------------------------------------------------------------
    op_rpm = BASELINE["operating"]["rpm"]
    op_theta0 = BASELINE["operating"]["theta_0_deg"]
    op_state = aero.solve_hover_direction(baseline_geom, op_rpm, theta_0_deg=op_theta0)
    azimuth_data = aero.evaluate_azimuth(baseline_geom, op_rpm, theta_0_deg=op_theta0, v_i=op_state['inflow_XZ'], phi_0_deg=op_state['phi_0_deg'])

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

    # Subplot A: Pitch Angle & Effective AoA vs Azimuth
    axs[0, 0].plot(azimuth_data['psi_deg'], azimuth_data['theta_deg'], 'b-', label='Cyclic Pitch $\\theta(\\psi)$')
    axs[0, 0].plot(azimuth_data['psi_deg'], azimuth_data['alpha_eff_deg'], 'r--', label='Effective AoA $\\alpha_{\\mathrm{eff}}(\\psi)$')
    axs[0, 0].set_xlabel('Azimuth Angle $\\psi$ (deg)')
    axs[0, 0].set_ylabel('Angle (deg)')
    axs[0, 0].set_title('Blade Pitch & Effective AoA over 1 Revolution')
    axs[0, 0].set_xticks(np.arange(0, 361, 45))
    axs[0, 0].grid(True)
    axs[0, 0].legend()

    # Subplot B: Lift and Drag Coefficients
    axs[0, 1].plot(azimuth_data['psi_deg'], azimuth_data['cl'], 'g-', label='Dynamic $C_L(\\psi)$')
    axs[0, 1].plot(azimuth_data['psi_deg'], azimuth_data['cd'], 'm--', label='Dynamic $C_D(\\psi)$')
    axs[0, 1].set_xlabel('Azimuth Angle $\\psi$ (deg)')
    axs[0, 1].set_ylabel('Aerodynamic Coefficients')
    axs[0, 1].set_title('Section $C_L$ and $C_D$ vs. Azimuth')
    axs[0, 1].set_xticks(np.arange(0, 361, 45))
    axs[0, 1].grid(True)
    axs[0, 1].legend()

    # Subplot C: Single Blade & 4-Blade Total Thrust Forces
    axs[1, 0].plot(azimuth_data['psi_deg'], azimuth_data['F_Z_single'] * op_state['blockage_factor'], 'b:', alpha=0.7, label='Single Blade $F_Z(\\psi)$')
    axs[1, 0].plot(azimuth_data['psi_deg'], azimuth_data['F_Z_multi'] * op_state['blockage_factor'], 'navy', linewidth=2.5, label='Total 4-Blade Net Lift $F_Z(\\psi)$')
    axs[1, 0].axhline(y=op_state['thrust_Z_N'], color='r', linestyle='--', label=f'Mean $F_Z = {op_state["thrust_Z_N"]:.2f}$ N')
    axs[1, 0].set_xlabel('Azimuth Angle $\\psi$ (deg)')
    axs[1, 0].set_ylabel('Vertical Force $F_Z$ (N)')
    axs[1, 0].set_title('Instantaneous & Mean Rotor Lift Generation')
    axs[1, 0].set_xticks(np.arange(0, 361, 45))
    axs[1, 0].grid(True)
    axs[1, 0].legend()

    # Subplot D: Dynamic Pitching Moment for Servo Sizing
    axs[1, 1].plot(azimuth_data['psi_deg'], azimuth_data['M_pitch_single'] * 1000.0, 'darkorange', label='Blade Pitch Moment $M_{\\mathrm{pitch}}$ (N*mm)')
    axs[1, 1].axhline(y=op_state['max_pitch_moment_Nm'] * 1000.0, color='red', linestyle=':', label=f'Peak = {op_state["max_pitch_moment_Nm"]*1000.0:.1f} N*mm')
    axs[1, 1].axhline(y=-op_state['max_pitch_moment_Nm'] * 1000.0, color='red', linestyle=':')
    axs[1, 1].set_xlabel('Azimuth Angle $\\psi$ (deg)')
    axs[1, 1].set_ylabel('Hinge Moment (N*mm)')
    axs[1, 1].set_title('Aerodynamic + Inertial Pitching Hinge Moment')
    axs[1, 1].set_xticks(np.arange(0, 361, 45))
    axs[1, 1].grid(True)
    axs[1, 1].legend()

    plt.tight_layout()
    fig_path2 = os.path.join(save_dir, 'azimuth_aerodynamics_detailed.png')
    plt.savefig(fig_path2, dpi=300)
    plt.close()
    print(f"[SAVED] {fig_path2}")

    # -------------------------------------------------------------
    # 3. Sweep 3: Geometric Parametric Sweeps (Radius, Chord, Span)
    # -------------------------------------------------------------
    r_sweep = np.linspace(0.065, 0.115, 15)
    r_results = [aero.solve_hover_direction(replace(baseline_geom, radius=r), rpm=2500.0, theta_0_deg=35.0) for r in r_sweep]

    b_sweep = np.linspace(0.150, 0.250, 15)
    b_results = [aero.solve_hover_direction(replace(baseline_geom, span=b), rpm=2500.0, theta_0_deg=35.0) for b in b_sweep]

    c_sweep = np.linspace(0.025, 0.045, 15)
    c_results = [aero.solve_hover_direction(replace(baseline_geom, chord=c), rpm=2500.0, theta_0_deg=35.0) for c in c_sweep]

    fig, axs = plt.subplots(1, 3, figsize=(16, 5))

    # Subplot 1: Radius Sweep
    axs[0].plot(r_sweep * 1000.0, [res['thrust_N'] for res in r_results], 'b-o', label='Thrust $F_T$')
    ax0_twin = axs[0].twinx()
    ax0_twin.plot(r_sweep * 1000.0, [res['P_elec_W'] for res in r_results], 'r--s', label='Elec Power')
    axs[0].set_xlabel('Rotor Radius $R$ (mm)')
    axs[0].set_ylabel('Net Thrust (N)', color='blue')
    ax0_twin.set_ylabel('Power (W)', color='red')
    axs[0].set_title('Effect of Rotor Radius ($b=220$ mm, $c=38$ mm)')
    axs[0].axvline(x=95.0, color='green', linestyle=':', label='Baseline $R=95$ mm')
    axs[0].grid(True)

    # Subplot 2: Span Sweep
    axs[1].plot(b_sweep * 1000.0, [res['thrust_N'] for res in b_results], 'b-o')
    ax1_twin = axs[1].twinx()
    ax1_twin.plot(b_sweep * 1000.0, [res['P_elec_W'] for res in b_results], 'r--s')
    axs[1].set_xlabel('Blade Span $b$ (mm)')
    axs[1].set_ylabel('Net Thrust (N)', color='blue')
    ax1_twin.set_ylabel('Power (W)', color='red')
    axs[1].set_title('Effect of Blade Span ($R=95$ mm, $c=38$ mm)')
    axs[1].axvline(x=220.0, color='green', linestyle=':', label='Baseline $b=220$ mm')
    axs[1].grid(True)

    # Subplot 3: Chord Sweep & Solidity
    axs[2].plot(c_sweep * 1000.0, [res['thrust_N'] for res in c_results], 'b-o')
    ax2_twin = axs[2].twinx()
    ax2_twin.plot(c_sweep * 1000.0, [res['figure_of_merit'] for res in c_results], 'g-^', label='Figure of Merit')
    axs[2].set_xlabel('Blade Chord $c$ (mm)')
    axs[2].set_ylabel('Net Thrust (N)', color='blue')
    ax2_twin.set_ylabel('Figure of Merit (FM)', color='green')
    axs[2].set_title('Effect of Blade Chord & Solidity')
    axs[2].axvline(x=38.0, color='green', linestyle=':', label='Baseline $c=38$ mm')
    axs[2].grid(True)

    plt.tight_layout()
    fig_path3 = os.path.join(save_dir, 'geometric_parameter_sweeps.png')
    plt.savefig(fig_path3, dpi=300)
    plt.close()
    print(f"[SAVED] {fig_path3}")

    # -------------------------------------------------------------
    # 4. Sweep 4: Figure of Merit & Power Loading Map
    # -------------------------------------------------------------
    fig, (ax_fm, ax_pl) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    for idx, th0 in enumerate(pitch_amplitudes):
        thrusts = [r['thrust_N'] for r in sweep_pitch_results[th0]]
        fms = [r['figure_of_merit'] for r in sweep_pitch_results[th0]]
        pls = [r['power_loading_elec_g_W'] for r in sweep_pitch_results[th0]]
        
        ax_fm.plot(thrusts, fms, label=f'$\\theta_0 = {th0}^\\circ$', color=colors[idx], marker='o', markersize=4)
        ax_pl.plot(thrusts, pls, label=f'$\\theta_0 = {th0}^\\circ$', color=colors[idx], marker='s', markersize=4)

    ax_fm.axvline(x=10.0, color='black', linestyle='--', label='10 N Min Thrust')
    ax_fm.axvline(x=12.0, color='green', linestyle=':', label='12 N Baseline')
    ax_fm.set_xlabel('Net Thrust $F_T$ (N)')
    ax_fm.set_ylabel('Figure of Merit ($FM = P_{\\mathrm{ideal}} / P_{\\mathrm{aero}}$)')
    ax_fm.set_title('Rotor Hover Efficiency (Figure of Merit)')
    ax_fm.grid(True)
    ax_fm.legend(loc='lower left')

    ax_pl.axvline(x=10.0, color='black', linestyle='--', label='10 N Min Thrust')
    ax_pl.axvline(x=12.0, color='green', linestyle=':', label='12 N Baseline')
    ax_pl.set_xlabel('Net Thrust $F_T$ (N)')
    ax_pl.set_ylabel('Electrical Power Loading (g/W)')
    ax_pl.set_title('Power Loading vs. Net Thrust')
    ax_pl.grid(True)
    ax_pl.legend(loc='upper right')

    plt.tight_layout()
    fig_path4 = os.path.join(save_dir, 'figure_of_merit_power_loading.png')
    plt.savefig(fig_path4, dpi=300)
    plt.close()
    print(f"[SAVED] {fig_path4}")

    # -------------------------------------------------------------
    # Detailed Operating Point Performance Summary Table
    # -------------------------------------------------------------
    print("\n" + "=" * 95)
    print(f"{'OPERATING POINT PERFORMANCE MATRIX (Baseline R=95mm, b=220mm, c=38mm, theta_0=35 deg)':^95}")
    print("=" * 95)
    print(f"{'Condition':<22} | {'RPM':<6} | {'Thrust (N)':<10} | {'T/W':<6} | {'Torque (Nm)':<11} | {'P_aero (W)':<10} | {'P_elec (W)':<10} | {'FM':<6} | {'PL (g/W)':<8}")
    print("-" * 95)

    target_thrusts = [8.0, 10.0, 12.0, 14.0, 15.0]
    for ft_target in target_thrusts:
        rpms = np.linspace(1800, 3100, 50)
        t_list = [aero.solve_hover_direction(baseline_geom, r, 35.0)['thrust_N'] for r in rpms]
        if not np.all(np.diff(t_list) > 0):
            raise ValueError("Thrust sweep must be increasing before inverse interpolation")
        if not t_list[0] <= ft_target <= t_list[-1]:
            print(f"{ft_target:.1f} N target lies outside the sampled RPM envelope")
            continue
        req_rpm = float(np.interp(ft_target, t_list, rpms))
        perf = aero.solve_hover_direction(baseline_geom, req_rpm, 35.0)
        
        tag = ""
        if abs(ft_target - 10.0) < 0.1:
            tag = "(Target Min)"
        elif abs(ft_target - 12.0) < 0.1:
            tag = "(Baseline Target)"
        elif abs(ft_target - 15.0) < 0.1:
            tag = "(Max Power Margin)"

        print(f"{f'{ft_target:.1f} N Thrust {tag}':<22} | {req_rpm:<6.0f} | {perf['thrust_N']:<10.2f} | {perf['tw_ratio']:<6.2f} | {perf['torque_Nm']:<11.4f} | {perf['P_aero_W']:<10.1f} | {perf['P_elec_W']:<10.1f} | {perf['figure_of_merit']:<6.3f} | {perf['power_loading_elec_g_W']:<8.2f}")
    print("=" * 95 + "\n")

    return {
        'baseline_geom': baseline_geom,
        'figures': [fig_path1, fig_path2, fig_path3, fig_path4]
    }


def run_airfoil_and_cam_study(save_dir: str = "figures") -> Dict[str, any]:
    """
    Execute comprehensive comparison across Airfoils (NACA 0015, NACA 0012, Eppler E374),
    Blockage Recovery (0.92 raw cage vs 0.96 faired vs 1.00 ideal), and
    Pitch Schedule (Sinusoidal vs Asymmetric Cam-Track).
    """
    os.makedirs(save_dir, exist_ok=True)
    aero = CyclorotorAeroModel()

    # Geometry variants
    geom_0012 = CyclorotorGeometry(**BASELINE["geometry"])
    geom_0015 = replace(geom_0012, airfoil="NACA 0015")
    geom_e374 = replace(geom_0012, airfoil="Eppler E374")

    rpm_eval = BASELINE["operating"]["rpm"]
    theta0_eval = BASELINE["operating"]["theta_0_deg"]

    # 1. Evaluate baseline and variants at 2640 RPM
    res_base_ideal = aero.solve_hover_direction(geom_0015, rpm_eval, theta0_eval, pitch_schedule="sinusoidal", blockage_factor=1.0)
    res_base_block = aero.solve_hover_direction(geom_0015, rpm_eval, theta0_eval, pitch_schedule="sinusoidal", blockage_factor=0.92)
    res_faired_0015 = aero.solve_hover_direction(geom_0015, rpm_eval, theta0_eval, pitch_schedule="sinusoidal", blockage_factor=0.96)
    res_faired_0012 = aero.solve_hover_direction(geom_0012, rpm_eval, theta0_eval, pitch_schedule="sinusoidal", blockage_factor=0.96)
    res_faired_e374 = aero.solve_hover_direction(geom_e374, rpm_eval, theta0_eval, pitch_schedule="sinusoidal", blockage_factor=0.96)
    res_cam_track = aero.solve_hover_direction(geom_0012, rpm_eval, theta0_eval, pitch_schedule="asymmetric_cam", blockage_factor=0.96)

    # Azimuthal detailed data for plotting
    az_sin = aero.evaluate_azimuth(geom_0015, rpm_eval, theta0_eval, v_i=res_base_ideal['inflow_XZ'], phi_0_deg=res_base_ideal['phi_0_deg'], pitch_schedule="sinusoidal")
    az_cam = aero.evaluate_azimuth(geom_0012, rpm_eval, theta0_eval, v_i=res_cam_track['inflow_XZ'], phi_0_deg=res_cam_track['phi_0_deg'], pitch_schedule="asymmetric_cam")

    # Generate 4-panel publication plot
    fig, axs = plt.subplots(2, 2, figsize=(15, 11))

    # Panel A: Airfoil Polar Comparison (Cl and Cd vs AoA at Re=100k)
    alphas_deg = np.linspace(-30, 30, 200)
    alphas_rad = np.radians(alphas_deg)
    zeros_arr = np.zeros_like(alphas_rad)
    cl_15, cd_15, _ = aero.get_airfoil_polars(alphas_rad, np.full_like(alphas_rad, 1e5), zeros_arr, zeros_arr, 5.79, airfoil="NACA 0015")
    cl_12, cd_12, _ = aero.get_airfoil_polars(alphas_rad, np.full_like(alphas_rad, 1e5), zeros_arr, zeros_arr, 5.79, airfoil="NACA 0012")
    cl_e374, cd_e374, _ = aero.get_airfoil_polars(alphas_rad, np.full_like(alphas_rad, 1e5), zeros_arr, zeros_arr, 5.79, airfoil="Eppler E374")

    axs[0, 0].plot(alphas_deg, cl_15, 'b-', label='NACA 0015 ($t/c=15\\%$, $C_{d0}=0.020$)')
    axs[0, 0].plot(alphas_deg, cl_12, 'g--', label='NACA 0012 ($t/c=12\\%$, $C_{d0}=0.016$)')
    axs[0, 0].plot(alphas_deg, cl_e374, 'r-.', label='Eppler E374 ($t/c=11\\%$, $C_{d0}=0.013$)')
    axs[0, 0].set_xlabel('Angle of Attack $\\alpha$ (deg)')
    axs[0, 0].set_ylabel('Lift Coefficient $C_L$')
    axs[0, 0].set_title('A: Low-Re Airfoil Polars Comparison (Re = 100,000)')
    axs[0, 0].grid(True)
    axs[0, 0].legend(loc='upper left', fontsize=9)

    # Panel B: Pitch Kinematics: Sinusoidal vs Asymmetric Cam
    axs[0, 1].plot(az_sin['psi_deg'], az_sin['theta_deg'], 'b-', linewidth=2.2, label='Sinusoidal Eccentric Ring $\\theta(\\psi)$')
    axs[0, 1].plot(az_cam['psi_deg'], az_cam['theta_deg'], 'r--', linewidth=2.2, label='Asymmetric Cam Pitch $\\theta(\\psi)$ (Flattened Dwell)')
    axs[0, 1].plot(az_sin['psi_deg'], az_sin['alpha_eff_deg'], 'b:', alpha=0.6, label='Sinusoidal Effective $\\alpha_{\\mathrm{eff}}$')
    axs[0, 1].plot(az_cam['psi_deg'], az_cam['alpha_eff_deg'], 'r:', alpha=0.6, label='Cam-Track Effective $\\alpha_{\\mathrm{eff}}$')
    axs[0, 1].set_xlabel('Azimuth Angle $\\psi$ (deg)')
    axs[0, 1].set_ylabel('Angle (deg)')
    axs[0, 1].set_title('B: Pitch Schedule Kinematics Comparison')
    axs[0, 1].set_xticks(np.arange(0, 361, 45))
    axs[0, 1].grid(True)
    axs[0, 1].legend(loc='lower left', fontsize=9)

    # Panel C: Multi-Blade Lift Generation over Azimuth
    axs[1, 0].plot(az_sin['psi_deg'], az_sin['F_Z_multi'], 'b-', label=f'Sinusoidal 4-Blade Lift ($F_Z = {res_base_ideal["thrust_Z_N"]:.2f}$ N)')
    axs[1, 0].plot(az_cam['psi_deg'], az_cam['F_Z_multi'] * res_cam_track['blockage_factor'], 'r-', linewidth=2.2, label=f'Cam-Track 4-Blade Lift ($F_Z = {res_cam_track["thrust_Z_N"]:.2f}$ N)')
    axs[1, 0].set_xlabel('Azimuth Angle $\\psi$ (deg)')
    axs[1, 0].set_ylabel('Vertical Lift Force $F_Z$ (N)')
    axs[1, 0].set_title('C: Azimuthal Lift Production & Dwell Effect')
    axs[1, 0].set_xticks(np.arange(0, 361, 45))
    axs[1, 0].grid(True)
    axs[1, 0].legend(loc='upper right', fontsize=9)

    # Panel D: Performance Synthesis Bar Chart
    configs = [
        'Baseline 0015\n(Ideal)',
        'Baseline 0015\n(8% Blockage)',
        'Rev 3.0 0015\n(Faired)',
        'Rev 3.0 0012\n(Faired)',
        'Rev 3.0 Cam\n(Asymmetric)'
    ]
    thrust_vals = [
        res_base_ideal['thrust_N'],
        res_base_block['thrust_N'],
        res_faired_0015['thrust_N'],
        res_faired_0012['thrust_N'],
        res_cam_track['thrust_N']
    ]
    fm_vals = [
        res_base_ideal['figure_of_merit'],
        res_base_block['figure_of_merit'],
        res_faired_0015['figure_of_merit'],
        res_faired_0012['figure_of_merit'],
        res_cam_track['figure_of_merit']
    ]
    x_idx = np.arange(len(configs))
    width = 0.35

    ax_bar1 = axs[1, 1]
    ax_bar2 = ax_bar1.twinx()
    bars1 = ax_bar1.bar(x_idx - width/2, thrust_vals, width, color='#1f77b4', alpha=0.85, label='Net Thrust (N)')
    bars2 = ax_bar2.bar(x_idx + width/2, fm_vals, width, color='#2ca02c', alpha=0.85, label='Figure of Merit')

    ax_bar1.axhline(10.0, color='red', linestyle='--', linewidth=1.2, label='10N Min Req.')
    ax_bar1.set_ylabel('Net Thrust $F_T$ (N)', color='#1f77b4')
    ax_bar2.set_ylabel('Figure of Merit ($FM$)', color='#2ca02c')
    ax_bar1.set_title('D: Architecture Performance Progression')
    ax_bar1.set_xticks(x_idx)
    ax_bar1.set_xticklabels(configs, fontsize=9)
    ax_bar1.set_ylim(0, 16)
    ax_bar2.set_ylim(0, 1.0)
    ax_bar1.grid(True, axis='y')

    # Value labels on bars
    for b in bars1:
        h = b.get_height()
        ax_bar1.annotate(f'{h:.2f}N', xy=(b.get_x() + b.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
    for b in bars2:
        h = b.get_height()
        ax_bar2.annotate(f'{h:.3f}', xy=(b.get_x() + b.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    fig_path5 = os.path.join(save_dir, 'airfoil_and_cam_pitch_study.png')
    plt.savefig(fig_path5, dpi=300)
    plt.close()
    print(f"[SAVED] {fig_path5}")

    # Print summary table
    print("\n" + "=" * 105)
    print(f"{'CYCLOPROP REV 3.0 ARCHITECTURAL UPGRADE & TRADE STUDY SUMMARY (at 2640 RPM)':^105}")
    print("=" * 105)
    print(f"{'Configuration':<28} | {'Airfoil':<12} | {'Schedule':<15} | {'Blockage':<9} | {'Thrust (N)':<11} | {'P_elec (W)':<11} | {'FM':<6} | {'T/W':<6}")
    print("-" * 105)
    print(f"{'1. Baseline (Ideal BEMT)':<28} | {'NACA 0015':<12} | {'Sinusoidal':<15} | {'1.00':<9} | {res_base_ideal['thrust_N']:<11.2f} | {res_base_ideal['P_elec_W']:<11.1f} | {res_base_ideal['figure_of_merit']:<6.3f} | {res_base_ideal['tw_ratio']:<6.2f}")
    print(f"{'2. Baseline (8% Blockage)':<28} | {'NACA 0015':<12} | {'Sinusoidal':<15} | {'0.92':<9} | {res_base_block['thrust_N']:<11.2f} | {res_base_block['P_elec_W']:<11.1f} | {res_base_block['figure_of_merit']:<6.3f} | {res_base_block['tw_ratio']:<6.2f}")
    print(f"{'3. Rev 3.0 Faired Pillars':<28} | {'NACA 0015':<12} | {'Sinusoidal':<15} | {'0.96':<9} | {res_faired_0015['thrust_N']:<11.2f} | {res_faired_0015['P_elec_W']:<11.1f} | {res_faired_0015['figure_of_merit']:<6.3f} | {res_faired_0015['tw_ratio']:<6.2f}")
    print(f"{'4. Rev 3.0 Faired + NACA0012':<28} | {'NACA 0012':<12} | {'Sinusoidal':<15} | {'0.96':<9} | {res_faired_0012['thrust_N']:<11.2f} | {res_faired_0012['P_elec_W']:<11.1f} | {res_faired_0012['figure_of_merit']:<6.3f} | {res_faired_0012['tw_ratio']:<6.2f}")
    print(f"{'5. Rev 3.0 Cam-Track Concept':<28} | {'NACA 0012':<12} | {'Asymmetric Cam':<15} | {'0.96':<9} | {res_cam_track['thrust_N']:<11.2f} | {res_cam_track['P_elec_W']:<11.1f} | {res_cam_track['figure_of_merit']:<6.3f} | {res_cam_track['tw_ratio']:<6.2f}")
    print("=" * 105 + "\n")

    return {
        'fig_path': fig_path5,
        'results': {
            'ideal': res_base_ideal,
            'blockage_092': res_base_block,
            'faired_0015': res_faired_0015,
            'faired_0012': res_faired_0012,
            'cam_track': res_cam_track
        }
    }


if __name__ == '__main__':
    figures_out = ROOT / "figures" / "corrected"
    run_parametric_sweeps(save_dir=figures_out)
    run_airfoil_and_cam_study(save_dir=figures_out)
