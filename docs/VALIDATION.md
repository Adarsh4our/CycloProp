# Remaining engineering validation

The software changes correct data handling and internal numerical consistency. They do not certify the aerodynamic model or hardware.

## CFD

1. Execute the generated multi-Re study in OpenFOAM v2412. Retain case manifests, checkMesh logs, solver logs and numerical quality reports.
2. Compare at least three mesh resolutions while holding geometry, fluid, discretization and boundary conditions fixed. Record coefficient changes, wall resolution and force stability; select acceptance tolerances before comparing results.
3. Investigate persistent oscillation using a transient solver. Record physical timestep, Courant limit, startup exclusion, sampling interval and averaging duration. Repeat with a smaller timestep and longer averaging window. Quantify mean and variation; do not treat steady SIMPLE iterations as physical time samples.
4. Validate static polars against independent reference data at matching Reynolds number, surface condition and turbulence assumptions. Then assess cyclic pitching at the rotor's amplitude and frequency. A static airfoil comparison alone does not validate rotor hover.
5. Import only complete numerically accepted tables within the rotor operating envelope. The current integration path accepts steady numerical exports; transient data requires a separately reviewed time-averaging and acceptance record before import.

## CAD and mass

Export component volume, assigned material/density, quantity and calculated mass from SolidWorks. Compare every line with config/baseline.json. The specified solid 6 mm diameter, 260 mm long steel shaft is 57.708 g before machining. The previous 28 g allocation is superseded. Other component masses remain estimates.

Reconcile shaft length, endplate dimensions, blade profile and material assignments across the assembly, specification and drawings. Check trunnion-to-spar fits, full-motion clearances and actual material masses. No binary CAD change or clearance certification was performed in this software update.

## Design decision

The corrected preliminary baseline predicts about 8.40 N vertical thrust at 2640 RPM, 189.41 W electrical demand and 331.11 g estimated mass. It falls below the 10 N thrust target. Higher RPM, geometry changes and mass reduction require motor/ESC thermal assessment, strength/stiffness checks and updated CFD. The analytical estimate is not a flight or fabrication sign-off.

## Evidence status

- 23 regression checks passed before the final continuous-stall correction.
- No further tests were run after the user requested they be skipped.
- The baseline report, BOM and CFD plan were generated after the stall correction.
- Existing CFD histories were audited: 1 accepted case, 84 rejected cases.
- New OpenFOAM solves, transient/mesh studies, SolidWorks mass exports and hardware measurements remain pending. OpenFOAM was unavailable in the local Windows environment; WSL listed only Docker Desktop.
