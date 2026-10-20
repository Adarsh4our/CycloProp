"""Compatibility entry point for the shared, per-geometry CFD runner."""
from run_openfoam_sweep import main

if __name__ == "__main__":
    raise SystemExit(main(default_airfoil="naca0018"))
