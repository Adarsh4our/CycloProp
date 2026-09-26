import numpy as np

rho = 1.225
configs = [
    {'name': 'Config A (Compact): R=85mm, b=200mm, c=35mm', 'R': 0.085, 'b': 0.200, 'c': 0.035, 'th0': 35.0},
    {'name': 'Config B (Baseline Recommended): R=95mm, b=220mm, c=38mm', 'R': 0.095, 'b': 0.220, 'c': 0.038, 'th0': 35.0},
    {'name': 'Config C (High-Thrust/Robust): R=100mm, b=230mm, c=40mm', 'R': 0.100, 'b': 0.230, 'c': 0.040, 'th0': 35.0},
    {'name': 'Config D (Wide Span): R=90mm, b=240mm, c=36mm', 'R': 0.090, 'b': 0.240, 'c': 0.036, 'th0': 35.0},
]

for cfg in configs:
    R = cfg['R']
    b = cfg['b']
    c = cfg['c']
    th0 = cfg['th0']
    sigma = (4 * c) / (np.pi * R)
    AR = b / c
    print(f"\n{'='*75}")
    print(f"{cfg['name']} | Solidity={sigma:.3f}, AR={AR:.2f}")
    print(f"{'='*75}")
    print(f"{'RPM':<6} | {'Thrust (N)':<10} | {'Torque (Nm)':<11} | {'P_aero (W)':<10} | {'P_elec (W)':<10} | {'FM':<6} | {'PL (g/W)':<8}")
    print("-" * 75)
    
    for rpm in [2000, 2200, 2400, 2600, 2800]:
        omega = rpm * 2 * np.pi / 60
        psi = np.linspace(0, 2*np.pi, 360, endpoint=False)
        theta_0 = np.radians(th0)
        theta = theta_0 * np.sin(psi)
        v_i = 4.0
        
        # Self consistent inflow solver
        for _ in range(40):
            V_flow_T = omega * R + v_i * np.cos(psi)
            V_flow_N = v_i * np.sin(psi)
            U_rel = np.sqrt(V_flow_T**2 + V_flow_N**2)
            phi_inf = np.arctan2(V_flow_N, V_flow_T)
            
            # Virtual camber and pitch rate corrections
            dtheta_dt = omega * theta_0 * np.cos(psi)
            alpha_geom = theta - phi_inf
            delta_alpha_camber = c / (4.0 * R)
            delta_alpha_rate = (c / (2.0 * np.maximum(U_rel, 1.0))) * dtheta_dt
            alpha_eff = alpha_geom + delta_alpha_camber + delta_alpha_rate
            
            # Aerodynamic polars with low-Re stall
            cl = 2.0 * np.pi * 0.88 * np.sin(alpha_eff)
            cd = 0.018 + 1.15 * (alpha_eff**2)
            
            q = 0.5 * rho * (U_rel**2) * (c * b)
            dL = q * cl
            dD = q * cd
            
            # Normal and Tangential force on blade
            Ft = - dL * np.sin(phi_inf) - dD * np.cos(phi_inf)
            Fn = dL * np.cos(phi_inf) - dD * np.sin(phi_inf)
            
            # Global coordinates
            FX = -Ft * np.sin(psi) + Fn * np.cos(psi)
            FZ = Ft * np.cos(psi) + Fn * np.sin(psi)
            
            FZ_4 = 4 * np.mean(FZ)
            FX_4 = 4 * np.mean(FX)
            F_net = np.sqrt(FZ_4**2 + FX_4**2)
            
            # Momentum induced downwash
            v_i_new = np.sqrt(F_net / (4 * rho * R * b))
            v_i = 0.7 * v_i + 0.3 * v_i_new
            
        Q = - Ft * R
        Q_4 = 4 * np.mean(Q)
        P_aero = Q_4 * omega
        P_elec = P_aero / (0.82 * 0.95 * 0.96)
        PL = (F_net * 1000 / 9.81) / P_elec
        P_ideal = (F_net**1.5) / np.sqrt(4 * rho * R * b)
        FM = P_ideal / P_aero
        
        print(f"{rpm:<6d} | {F_net:<10.2f} | {Q_4:<11.4f} | {P_aero:<10.1f} | {P_elec:<10.1f} | {FM:<6.3f} | {PL:<8.2f}")
