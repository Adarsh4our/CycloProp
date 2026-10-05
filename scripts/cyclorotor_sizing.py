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
  1. Complete Blade Element Momentum Theory (BEMT) / Double-pass Inflow Solver.
  2. Curvilinear flow virtual camber correction: kappa = c / (2R) -> delta_alpha = c / (4R).
  3. Dynamic pitch-rate damping & virtual pitching effect.
  4. Low-Reynolds unsteady dynamic stall delay (Leishman-Beddoes / Gormont cyclorotor adaptation).
  5. 3D finite aspect ratio tip-loss & induced drag polar correction (C_Di = C_L^2 / (pi * AR * e)).
  6. Endplate parasitic friction & shaft bearing tare torque modeling.
  7. Multi-variable parametric sweeps (Radius, Span, Chord, RPM, Pitch Amplitude).
  8. Dynamic blade hinge moment & cyclic pitch servo torque analysis.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

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
    airfoil: str = "NACA 0015"
    pivot_ratio: float = 0.25 # Pivot axis location from leading edge (x/c)
    blade_mass_each: float = 0.0125 # Mass of single blade [kg] (12.5 g)
    total_module_mass: float = 0.3014 # Total module mass [kg] (301.4 g, Rev 3.0)

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
    def __init__(self, rho: float = 1.225, mu: float = 1.81e-5):
        self.rho = rho          # Air density [kg/m^3]
        self.mu = mu            # Dynamic viscosity [Pa*s]
        self.eta_motor = 0.84   # High-efficiency Brushless Outrunner motor efficiency
        self.eta_mech = 0.96    # Precision ceramic/steel hybrid bearing & linkage efficiency
        self.eta_esc = 0.97     # High-frequency 32-bit ESC switching efficiency
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
        else:  # Default NACA 0015
            alpha_ss_deg = 13.5  # Static stall angle [deg]
            cl_alpha_2d = 2.0 * np.pi * 0.88  # 2D lift curve slope with low-Re viscous boundary layer deficit
            cd0 = 0.020  # Base zero-lift profile drag coefficient at Re ~ 100,000
            cd_profile_quad = 1.25

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
                # Post-stall regime (Viterna-Corrigan / flat plate dynamic stall shedding)
                cl_max_dyn = self.tip_loss_factor * cl_alpha_2d * a_ds
                cd_max = 1.60
                cl[i] = sgn * (cl_max_dyn * np.cos(abs_a - a_ds) * np.exp(-1.4 * (abs_a - a_ds)) + 
                                0.5 * cd_max * np.sin(2.0 * abs_a))
                cd_profile = cd0 + (cd_max - cd0) * (np.sin(abs_a) ** 2)
                cd_induced = (cl[i] ** 2) / (np.pi * aspect_ratio * self.e_oswald)
                cd[i] = cd_profile + cd_induced
                cm[i] = -0.22 * sgn * (np.sin(abs_a - a_ds))

        return cl, cd, cm

    def evaluate_azimuth(self, geom: CyclorotorGeometry, rpm: float, 
                          theta_0_deg: float, phi_0_deg: float = 0.0,
                          v_i: float = 0.0, num_azimuth: int = 360,
                          pitch_schedule: str = "sinusoidal") -> Dict[str, np.ndarray]:
        """
        Evaluate full revolution kinematics and blade forces across azimuth psi in [0, 2*pi].
        Supports 'sinusoidal' (standard eccentric ring) and 'asymmetric_cam' (higher-harmonic dwell).
        """
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
            dtheta_dpsi = np.gradient(theta, dpsi)
            dtheta_dt = omega * dtheta_dpsi
            d2theta_dt2 = np.gradient(dtheta_dt, dt)
        else:
            # Pure sinusoidal eccentric ring
            theta = theta_0 * np.sin(psi - phi_0)
            dtheta_dpsi = theta_0 * np.cos(psi - phi_0)
            dtheta_dt = omega * dtheta_dpsi
            d2theta_dt2 = - (omega ** 2) * theta

        # Tangential and radial velocity components of oncoming flow relative to blade:
        # Rotation is CCW; at psi=0 (3 o'clock), blade moves along +Z.
        # Flow blows against motion (+V_flow_T along tangent) and downward (+Z thrust -> -Z induced downwash).
        V_flow_T = omega * geom.radius + v_i * np.cos(psi)
        V_flow_N = v_i * np.sin(psi)
        
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
        dalpha_dt = np.gradient(alpha_eff, dt)

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
            'v_i': v_i
        }

    def solve_hover_state(self, geom: CyclorotorGeometry, rpm: float, 
                          theta_0_deg: float, phi_0_deg: float = 0.0,
                          pitch_schedule: str = "sinusoidal",
                          blockage_factor: float = 1.0,
                          max_iter: int = 50, tol: float = 1e-4) -> Dict[str, float]:
        """
        Solve self-consistent hover induced velocity v_i and rotor performance metrics.
        Includes aerodynamic blockage factor from frame structure and supports non-sinusoidal cam scheduling.
        """
        v_i = 3.5  # Initial guess [m/s]
        relaxation = 0.35

        for _ in range(max_iter):
            res = self.evaluate_azimuth(geom, rpm, theta_0_deg, phi_0_deg, v_i=v_i, pitch_schedule=pitch_schedule)
            F_X_mean = np.mean(res['F_X_multi'])
            F_Z_mean = np.mean(res['F_Z_multi'])
            F_net = np.sqrt(F_X_mean**2 + F_Z_mean**2)

            # Momentum theory induced velocity: v_i_new = sqrt(F_net / (4 * rho * R * b))
            v_i_new = np.sqrt(F_net / (2.0 * self.rho * geom.swept_area))

            if np.abs(v_i_new - v_i) < tol:
                v_i = v_i_new
                break
            v_i = (1.0 - relaxation) * v_i + relaxation * v_i_new

        # Final evaluation with converged v_i
        res = self.evaluate_azimuth(geom, rpm, theta_0_deg, phi_0_deg, v_i=v_i, pitch_schedule=pitch_schedule)
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
        P_profile = max(P_aero - P_induced, 0.0)  # Profile drag + tare power [W]
        
        # Ideal momentum power
        P_ideal = (F_net ** 1.5) / np.sqrt(2.0 * self.rho * geom.swept_area)
        figure_of_merit = P_ideal / np.maximum(P_aero, 1e-3)
        figure_of_merit = float(np.clip(figure_of_merit, 0.0, 1.0))

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
            'pitch_schedule': pitch_schedule,
            'airfoil': geom.airfoil
        }


def run_parametric_sweeps(save_dir: str = "figures") -> Dict[str, any]:
    """
    Execute comprehensive multi-variable sweeps and export publication figures.
    """
    os.makedirs(save_dir, exist_ok=True)
    aero = CyclorotorAeroModel()

    # Recommended Baseline Geometry (Rev 3.0)
    baseline_geom = CyclorotorGeometry(
        radius=0.095,       # R = 95 mm (Diameter D = 190 mm)
        span=0.220,         # b = 220 mm
        chord=0.038,        # c = 38 mm
        num_blades=4,
        airfoil="NACA 0015",
        blade_mass_each=0.0125,
        total_module_mass=0.3014  # Rev 3.0 baseline: 301.4 g
    )

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
            res = aero.solve_hover_state(baseline_geom, rpm, theta_0_deg=th0)
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
    op_rpm = 2730.0
    op_theta0 = 35.0
    op_state = aero.solve_hover_state(baseline_geom, op_rpm, theta_0_deg=op_theta0)
    azimuth_data = aero.evaluate_azimuth(baseline_geom, op_rpm, theta_0_deg=op_theta0, v_i=op_state['v_i'])

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
    axs[1, 0].plot(azimuth_data['psi_deg'], azimuth_data['F_Z_single'], 'b:', alpha=0.7, label='Single Blade $F_Z(\\psi)$')
    axs[1, 0].plot(azimuth_data['psi_deg'], azimuth_data['F_Z_multi'], 'navy', linewidth=2.5, label='Total 4-Blade Net Lift $F_Z(\\psi)$')
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
    r_results = [aero.solve_hover_state(CyclorotorGeometry(radius=r, span=0.220, chord=0.038, num_blades=4), rpm=2500.0, theta_0_deg=35.0) for r in r_sweep]

    b_sweep = np.linspace(0.150, 0.250, 15)
    b_results = [aero.solve_hover_state(CyclorotorGeometry(radius=0.095, span=b, chord=0.038, num_blades=4), rpm=2500.0, theta_0_deg=35.0) for b in b_sweep]

    c_sweep = np.linspace(0.025, 0.045, 15)
    c_results = [aero.solve_hover_state(CyclorotorGeometry(radius=0.095, span=0.220, chord=c, num_blades=4), rpm=2500.0, theta_0_deg=35.0) for c in c_sweep]

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
        t_list = [aero.solve_hover_state(baseline_geom, r, 35.0)['thrust_N'] for r in rpms]
        req_rpm = float(np.interp(ft_target, t_list, rpms))
        perf = aero.solve_hover_state(baseline_geom, req_rpm, 35.0)
        
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
    geom_0015 = CyclorotorGeometry(radius=0.095, span=0.220, chord=0.038, num_blades=4, airfoil="NACA 0015", total_module_mass=0.303)
    geom_0012 = CyclorotorGeometry(radius=0.095, span=0.220, chord=0.038, num_blades=4, airfoil="NACA 0012", total_module_mass=0.303)
    geom_e374 = CyclorotorGeometry(radius=0.095, span=0.220, chord=0.038, num_blades=4, airfoil="Eppler E374", total_module_mass=0.303)

    rpm_eval = 2640.0
    theta0_eval = 35.0

    # 1. Evaluate baseline and variants at 2640 RPM
    res_base_ideal = aero.solve_hover_state(geom_0015, rpm_eval, theta0_eval, pitch_schedule="sinusoidal", blockage_factor=1.0)
    res_base_block = aero.solve_hover_state(geom_0015, rpm_eval, theta0_eval, pitch_schedule="sinusoidal", blockage_factor=0.92)
    res_faired_0015 = aero.solve_hover_state(geom_0015, rpm_eval, theta0_eval, pitch_schedule="sinusoidal", blockage_factor=0.96)
    res_faired_0012 = aero.solve_hover_state(geom_0012, rpm_eval, theta0_eval, pitch_schedule="sinusoidal", blockage_factor=0.96)
    res_faired_e374 = aero.solve_hover_state(geom_e374, rpm_eval, theta0_eval, pitch_schedule="sinusoidal", blockage_factor=0.96)
    res_cam_track = aero.solve_hover_state(geom_0012, rpm_eval, theta0_eval, pitch_schedule="asymmetric_cam", blockage_factor=0.96)

    # Azimuthal detailed data for plotting
    az_sin = aero.evaluate_azimuth(geom_0015, rpm_eval, theta0_eval, v_i=res_base_ideal['v_i'], pitch_schedule="sinusoidal")
    az_cam = aero.evaluate_azimuth(geom_0012, rpm_eval, theta0_eval, v_i=res_cam_track['v_i'], pitch_schedule="asymmetric_cam")

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
    axs[1, 0].plot(az_cam['psi_deg'], az_cam['F_Z_multi'], 'r-', linewidth=2.2, label=f'Cam-Track 4-Blade Lift ($F_Z = {res_cam_track["thrust_Z_N"]:.2f}$ N)')
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
    figures_out = "c:/Users/Adarsh Singh/CycloProp/figures"
    run_parametric_sweeps(save_dir=figures_out)
    run_airfoil_and_cam_study(save_dir=figures_out)
