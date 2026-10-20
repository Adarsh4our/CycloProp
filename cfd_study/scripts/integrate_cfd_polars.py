"""Bounded static CFD polars. Use --results with a new sweep's polars directory.

Numerical acceptance does not validate cyclic-pitch aerodynamics.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from cyclorotor_sizing import CyclorotorAeroModel, CyclorotorGeometry
from project_config import BASELINE, ROOT


def airfoil_key(name):
    return name.lower().replace(" ", "").replace("-", "")


def validate_polar(polar):
    arrays = [np.asarray(polar[key], dtype=float) for key in ("alpha", "Cl", "Cd", "Cm")]
    if any(a.ndim != 1 for a in arrays) or len(arrays[0]) < 2:
        raise ValueError("Polar arrays must be one-dimensional with at least two points")
    if any(a.shape != arrays[0].shape or not np.isfinite(a).all() for a in arrays):
        raise ValueError("Polar arrays must have equal lengths and finite coefficients")
    if not (np.diff(arrays[0]) > 0).all():
        raise ValueError("Polar angles must be strictly increasing and unique")
    if (arrays[2] < 0).any():
        raise ValueError("Drag coefficients must be nonnegative")
    if not np.isfinite(polar["reynolds"]) or polar["reynolds"] <= 0:
        raise ValueError("Polar Reynolds number must be finite and positive")


def load_polar(csv_path, *, require_accepted=True, reynolds=None):
    path = Path(csv_path)
    df = pd.read_csv(path, comment="#")
    df.columns = df.columns.str.strip()
    required = ["alpha_deg", "Cl", "Cd", "Cm"]
    if not set(required).issubset(df.columns):
        raise ValueError(f"{path.name}: required columns are {required}")
    df = df[required].apply(pd.to_numeric, errors="raise").sort_values("alpha_deg")
    match = re.search(r"_Re([0-9]+(?:[.][0-9]+)?)(k?)", path.stem)
    if reynolds is None:
        if match is None:
            raise ValueError(f"{path.name}: provide a Reynolds number")
        reynolds = float(match[1]) * (1000 if match[2] else 1)
    polar = {
        "alpha_deg": df.alpha_deg.to_numpy(),
        "alpha": np.radians(df.alpha_deg.to_numpy()),
        **{key: df[key].to_numpy() for key in ("Cl", "Cd", "Cm")},
        "source": str(path), "reynolds": float(reynolds), "accepted": False,
    }
    validate_polar(polar)
    metadata_path = path.with_suffix(".json")
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        polar["accepted"] = (
            metadata.get("numerically_accepted") is True
            and metadata.get("csv_sha256") == hashlib.sha256(path.read_bytes()).hexdigest()
            and metadata.get("reynolds") == polar["reynolds"]
            and metadata.get("angles_deg") == polar["alpha_deg"].tolist()
        )
    if require_accepted and not polar["accepted"]:
        raise ValueError(f"{path.name}: missing, stale or rejected numerical acceptance metadata")
    return polar


def cross_validate(polar_a, polar_b, name=""):
    validate_polar(polar_a)
    validate_polar(polar_b)
    if (polar_a["reynolds"] != polar_b["reynolds"]
            or not np.array_equal(polar_a["alpha"], polar_b["alpha"])):
        raise ValueError("Cross-validation requires matching Reynolds numbers and angle grids")
    ok = all(np.allclose(polar_a[key], polar_b[key], atol=0.002, rtol=tolerance)
             for key, tolerance in (("Cl", 0.05), ("Cd", 0.10), ("Cm", 0.10)))
    print(f"{name}: {'AGREE' if ok else 'DISAGREE'}; agreement is not physical validation")
    return bool(ok)


def average_polars(polar_a, polar_b):
    if not polar_a.get("accepted") or not polar_b.get("accepted"):
        raise ValueError("Only accepted polars may be combined")
    if not cross_validate(polar_a, polar_b):
        raise ValueError("Disagreeing polars must be investigated before averaging")
    return {**polar_a,
            **{key: 0.5 * (polar_a[key] + polar_b[key]) for key in ("Cl", "Cd", "Cm")},
            "source": f"average of {polar_a['source']} and {polar_b['source']}"}


class CFDPolarAeroModel(CyclorotorAeroModel):
    """Signed-angle and linear-Re interpolation; no silent fallback/extrapolation."""

    def __init__(self, polars, **kwargs):
        super().__init__(**kwargs)
        self.cfd_polars = {}
        for name, tables in polars.items():
            tables = [tables] if isinstance(tables, dict) else list(tables)
            if not tables:
                raise ValueError(f"No polar tables for {name}")
            for table in tables:
                validate_polar(table)
                if not table.get("accepted"):
                    raise ValueError(f"Unaccepted polar for {name}")
            tables.sort(key=lambda p: p["reynolds"])
            if len({p["reynolds"] for p in tables}) != len(tables):
                raise ValueError(f"Duplicate Reynolds datasets for {name}; select a source explicitly")
            self.cfd_polars[airfoil_key(name)] = tables

    def get_airfoil_polars(self, alpha_eff, Re, k_reduced, dalpha_dt,
                           aspect_ratio, airfoil="NACA 0012"):
        key = airfoil_key(airfoil)
        if key not in self.cfd_polars:
            raise ValueError(f"No accepted CFD polar for {airfoil}")
        angles, reynolds = np.broadcast_arrays(np.asarray(alpha_eff, float), np.asarray(Re, float))
        if angles.ndim != 1 or not angles.size or not np.isfinite(angles).all() or not np.isfinite(reynolds).all():
            raise ValueError("Angle and Reynolds queries must be finite, nonempty vectors")
        if not np.isfinite(aspect_ratio) or aspect_ratio <= 0:
            raise ValueError("Aspect ratio must be positive")
        tables = self.cfd_polars[key]
        re_grid = np.array([p["reynolds"] for p in tables])
        if np.any(reynolds < re_grid[0] - 1e-6) or np.any(reynolds > re_grid[-1] + 1e-6):
            raise ValueError(f"Reynolds range {reynolds.min():.0f}..{reynolds.max():.0f} "
                             f"outside {key} coverage {re_grid[0]:.0f}..{re_grid[-1]:.0f}")
        for table in tables:
            if np.any(angles < table["alpha"][0] - 1e-12) or np.any(angles > table["alpha"][-1] + 1e-12):
                raise ValueError(f"Angle query outside {key} polar coverage")
        values = []
        for coefficient in ("Cl", "Cd", "Cm"):
            samples = np.stack([np.interp(angles, p["alpha"], p[coefficient]) for p in tables])
            if len(tables) == 1:
                values.append(samples[0])
            else:
                lower = np.clip(np.searchsorted(re_grid, reynolds, side="right") - 1, 0, len(tables) - 2)
                weight = (reynolds - re_grid[lower]) / (re_grid[lower + 1] - re_grid[lower])
                indexes = np.arange(angles.size)
                values.append(samples[lower, indexes] * (1 - weight)
                              + samples[lower + 1, indexes] * weight)
        cl, cd, cm = values
        return cl, cd + cl**2 / (np.pi * aspect_ratio * self.e_oswald), cm

    def solve_hover_state(self, *args, **kwargs):
        result = super().solve_hover_state(*args, **kwargs)
        result["polar_model"] = "numerically accepted static CFD; cyclic-pitch validation pending"
        return result


def run_comparison(results_dir):
    available = {}
    for path in sorted(Path(results_dir).glob("*_Re*.csv")):
        name = path.name.split("_")[0]
        available.setdefault(name, []).append(load_polar(path))
    if not available:
        raise ValueError(f"No accepted polar files in {results_dir}; complete a CFD sweep first")
    aero = CFDPolarAeroModel(available)
    op = BASELINE["operating"]
    geometry = CyclorotorGeometry(**BASELINE["geometry"])
    result = aero.solve_hover_direction(
        geometry, op["rpm"], op["theta_0_deg"], thrust_direction_deg=op["thrust_direction_deg"],
        blockage_factor=op["blockage_factor"], pitch_schedule=op["pitch_schedule"],
    )
    print(json.dumps(result, indent=2, allow_nan=False))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "cfd_study" / "accepted")
    args = parser.parse_args()
    try:
        run_comparison(args.results)
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, f"CFD comparison unavailable: {exc}\n")


if __name__ == "__main__":
    main()
