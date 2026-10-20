"""Numerical acceptance of steady CFD histories, separate from physical validation."""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from project_config import BASELINE, ROOT

RESIDUALS = ("res_p", "res_Ux", "res_Uz", "res_k", "res_omega")
COEFFICIENTS = ("Cl", "Cd", "Cm")


def assess_history(history, criteria=None):
    criteria = BASELINE["cfd"]["acceptance"] if criteria is None else criteria
    window = criteria["window_samples"]
    if not isinstance(window, int) or window < 2:
        raise ValueError("Acceptance window must contain at least two samples")
    for key in ("residual_limit", "coefficient_atol", "coefficient_rtol"):
        if not np.isfinite(criteria[key]) or criteria[key] <= 0:
            raise ValueError(f"{key} must be finite and positive")
    reasons = []
    required = ("iteration", *COEFFICIENTS, *RESIDUALS)
    missing = sorted(set(required) - set(history.columns))
    if missing:
        return {"accepted": False, "reasons": [f"Missing columns: {', '.join(missing)}"]}
    if len(history) < window:
        return {"accepted": False, "reasons": [f"Need {window} samples; have {len(history)}"]}
    tail = history.loc[:, list(required)].tail(window).apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(tail.to_numpy()).all():
        return {"accepted": False, "reasons": ["Nonfinite or missing history values"]}
    if not (np.diff(tail["iteration"]) > 0).all():
        reasons.append("History samples are not strictly increasing")
    residual_max = {key: float(tail[key].max()) for key in RESIDUALS}
    for key in RESIDUALS:
        if (tail[key] < 0).any() or residual_max[key] > criteria["residual_limit"]:
            reasons.append(f"{key} fails residual limit")
    means = {key: float(tail[key].mean()) for key in COEFFICIENTS}
    spreads = {key: float(np.ptp(tail[key])) for key in COEFFICIENTS}
    for key in COEFFICIENTS:
        limit = criteria["coefficient_atol"] + criteria["coefficient_rtol"] * abs(means[key])
        if spreads[key] > limit:
            reasons.append(f"{key} is not stable across the final {window} samples")
    if (tail["Cd"] < 0).any():
        reasons.append("Negative drag coefficient")
    return {
        "accepted": not reasons, "reasons": reasons, "sample_count": len(history),
        "last_iteration": float(tail["iteration"].iloc[-1]),
        "residual_max": residual_max, "coefficient_mean": means,
        "coefficient_range": spreads, "criteria": dict(criteria),
        "status": "numerical acceptance only; mesh and physical validation pending",
    }


def audit_saved_histories(results_dir):
    rows = []
    for path in sorted((Path(results_dir) / "iteration_logs").glob("*_iterations.csv")):
        result = assess_history(pd.read_csv(path))
        rows.append({"history": path.name, "accepted": result["accepted"],
                     "reasons": "; ".join(result["reasons"])})
    return pd.DataFrame(rows, columns=["history", "accepted", "reasons"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "cfd_study" / "results")
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "cfd_quality.csv")
    args = parser.parse_args()
    table = audit_saved_histories(args.results)
    if table.empty:
        parser.error("No iteration histories found")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output, index=False)
    accepted = int(table["accepted"].sum())
    print(json.dumps({"accepted": accepted, "rejected": len(table) - accepted,
                      "report": str(args.output)}))
    return 0 if accepted == len(table) else 1


if __name__ == "__main__":
    raise SystemExit(main())
