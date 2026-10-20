"""Prepare or run reproducible, per-geometry, multi-Re steady OpenFOAM studies.

Default: write a study plan only. Source OpenFOAM v2412 before using --run.
Each run uses a fresh directory and exports only complete numerically accepted polars.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from project_config import BASELINE, ROOT
from cfd_quality import assess_history
from generate_mesh import generate_mesh
from log_iteration_data import parse_log_residuals

TEMPLATE = ROOT / "cfd_study" / "templates" / "steady"
COORDS = ROOT / "cfd_study" / "airfoil_coords"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_plan(airfoils=None, reynolds=None, angles=None):
    cfg = BASELINE["cfd"]
    airfoils = cfg["airfoils"] if airfoils is None else airfoils
    reynolds = cfg["reynolds"] if reynolds is None else reynolds
    angles = cfg["angles_deg"] if angles is None else angles
    if not airfoils or not reynolds or not angles:
        raise ValueError("The study needs airfoils, Reynolds numbers and angles")
    if any(f not in cfg["airfoils"] for f in airfoils):
        raise ValueError("Unsupported airfoil")
    if any(not math.isfinite(r) or r <= 0 for r in reynolds):
        raise ValueError("Reynolds numbers must be positive and finite")
    if any(not math.isfinite(a) or abs(a) > 40 for a in angles):
        raise ValueError("This mesh workflow is limited to angles in [-40, 40] degrees")
    if any(len(set(values)) != len(values) for values in (airfoils, reynolds, angles)):
        raise ValueError("Duplicate study coordinates")
    chord = BASELINE["geometry"]["chord"]
    fluid = BASELINE["fluid"]
    templates = {str(p.relative_to(TEMPLATE)).replace("\\", "/"): sha256(p)
                 for p in sorted(TEMPLATE.rglob("*")) if p.is_file()}
    cases = []
    for foil in airfoils:
        coordinate_file = COORDS / f"{foil}_normalized.dat"
        digest = sha256(coordinate_file)
        for re_value in sorted(reynolds):
            velocity = re_value * fluid["mu"] / (fluid["rho"] * chord)
            for alpha in sorted(angles):
                cases.append({
                    "airfoil": foil, "reynolds": re_value, "alpha_deg": alpha,
                    "chord_m": chord, "velocity_m_s": velocity, "fluid": fluid,
                    "coordinate_file": coordinate_file.name, "coordinate_sha256": digest,
                    "mesh": dict(cfg["mesh"]), "template_sha256": templates,
                    "mesh_generator_sha256": sha256(Path(__file__).with_name("generate_mesh.py")),
                    "runner_sha256": sha256(__file__),
                    "solver": "simpleFoam", "iterations": cfg["iterations"],
                    "acceptance": dict(cfg["acceptance"]),
                })
    return cases


def prepare_case(case, case_dir):
    case_dir = Path(case_dir)
    # Refuse to overwrite any previous fields or results, including partial runs.
    case_dir.mkdir(parents=True, exist_ok=False)
    coordinate_file = COORDS / case["coordinate_file"]
    if sha256(coordinate_file) != case["coordinate_sha256"]:
        raise ValueError("Airfoil geometry changed after planning")
    for relative, digest in case["template_sha256"].items():
        source = TEMPLATE / relative
        if sha256(source) != digest:
            raise ValueError("Template changed after planning")
        destination = case_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    generate_mesh(str(coordinate_file), str(case_dir), case["alpha_deg"],
                  chord=case["chord_m"], **case["mesh"])
    speed = case["velocity_m_s"]
    field_path = case_dir / "0" / "U"
    text = field_path.read_text()
    text = re.sub(r"uniform\s+\([^)]*\)", f"uniform ({speed:.12g} 0 0)", text)
    field_path.write_text(text)
    # Fixed 1% inlet turbulence intensity; length scale = 0.07 chord.
    kinetic = 1.5 * (0.01 * speed)**2
    omega = math.sqrt(kinetic) / (0.09**0.25 * 0.07 * case["chord_m"])
    for field, value in (("k", kinetic), ("omega", omega)):
        path = case_dir / "0" / field
        path.write_text(re.sub(r"uniform\s+[0-9.eE+-]+", f"uniform {value:.12g}", path.read_text()))
    nu = case["fluid"]["mu"] / case["fluid"]["rho"]
    path = case_dir / "constant" / "transportProperties"
    path.write_text(re.sub(r"(nu\s+\[[^]]+\]\s*)[0-9.eE+-]+", rf"\g<1>{nu:.12g}", path.read_text()))
    (case_dir / "system" / "fvSolution").write_text("""FoamFile
{ version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    p { solver GAMG; smoother GaussSeidel; tolerance 1e-7; relTol 0.05; }
    "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-7; relTol 0.1; }
}
SIMPLE { nNonOrthogonalCorrectors 1; pRefCell 0; pRefValue 0; }
relaxationFactors
{ fields { p 0.2; } equations { U 0.4; "(k|omega)" 0.4; } }
""")
    # Fixed iteration count allows sufficient final samples for the acceptance window.
    control = """FoamFile
{{ version 2.0; format ascii; class dictionary; object controlDict; }}
application simpleFoam;
startFrom startTime;
startTime 0;
stopAt endTime;
endTime {iterations};
deltaT 1;
writeControl timeStep;
writeInterval 100;
purgeWrite 2;
writeFormat ascii;
writePrecision 10;
writeCompression off;
timeFormat general;
timePrecision 8;
runTimeModifiable false;
functions
{{
    forceCoeffs
    {{
        type forceCoeffs;
        libs ("libforces.so");
        writeControl timeStep;
        writeInterval 10;
        patches (airfoil);
        rho rhoInf;
        rhoInf {rho};
        magUInf {velocity};
        lRef {chord};
        Aref {chord};
        liftDir (0 0 1);
        dragDir (1 0 0);
        pitchAxis (0 1 0);
        CofR (0 0 0);
    }}
}}
""".format(iterations=case["iterations"], rho=case["fluid"]["rho"], velocity=speed, chord=case["chord_m"])
    (case_dir / "system" / "controlDict").write_text(control)
    (case_dir / "case.json").write_text(json.dumps(case, indent=2), encoding="utf-8")
    return case_dir


def read_case_history(case_dir):
    case_dir = Path(case_dir)
    path = case_dir / "postProcessing" / "forceCoeffs" / "0" / "coefficient.dat"
    residuals = parse_log_residuals(str(case_dir / "log.simpleFoam"))
    columns = None
    rows = []
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            names = line.lstrip("#").split()
            if names and names[0] == "Time":
                columns = names
            continue
        if not line.strip():
            continue
        if columns is None:
            raise ValueError("Missing force coefficient header")
        data = dict(zip(columns, map(float, line.split())))
        iteration = int(data["Time"])
        rows.append({"iteration": iteration, "Cl": data["Cl"], "Cd": data["Cd"],
                     "Cm": data["CmPitch"], **residuals.get(iteration, {})})
    return pd.DataFrame(rows)


def run_case(case_dir):
    case_dir = Path(case_dir)
    if (case_dir / "log.simpleFoam").exists():
        raise ValueError("Refusing to overwrite a solved/partial case; use a fresh run directory")
    for program in ("blockMesh", "checkMesh", "simpleFoam"):
        executable = shutil.which(program)
        if executable is None:
            raise RuntimeError(f"{program} unavailable; source OpenFOAM v2412 first")
        with (case_dir / f"log.{program}").open("w") as log:
            subprocess.run([executable], cwd=case_dir, stdout=log, stderr=subprocess.STDOUT, check=True)
        if program == "checkMesh" and "Mesh OK." not in (case_dir / "log.checkMesh").read_text():
            raise RuntimeError("checkMesh did not report Mesh OK")
    history = read_case_history(case_dir)
    history.to_csv(case_dir / "history.csv", index=False)
    settings = json.loads((case_dir / "case.json").read_text())
    quality = assess_history(history, settings["acceptance"])
    (case_dir / "quality.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    return quality


def export_polars(plan, outcomes, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    exported = 0
    for foil, reynolds in sorted({(c["airfoil"], c["reynolds"]) for c in plan}):
        group = [c for c in plan if c["airfoil"] == foil and c["reynolds"] == reynolds]
        selected = [outcomes[(foil, reynolds, c["alpha_deg"])] for c in group]
        if not all(q["accepted"] for q in selected):
            continue
        path = output_dir / f"{foil}_openfoam_Re{reynolds:g}.csv"
        rows = [{"alpha_deg": c["alpha_deg"], **q["coefficient_mean"]}
                for c, q in zip(group, selected)]
        pd.DataFrame(rows).sort_values("alpha_deg").to_csv(path, index=False)
        metadata = {"numerically_accepted": True, "reynolds": reynolds,
                    "angles_deg": sorted(c["alpha_deg"] for c in group),
                    "csv_sha256": sha256(path), "cases": group,
                    "acceptance_results": selected,
                    "validation": "Steady numerical acceptance only; mesh independence and cyclic pitching unvalidated"}
        path.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        exported += 1
    return exported


def main(default_airfoil=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--airfoils", nargs="+", default=[default_airfoil] if default_airfoil else None)
    parser.add_argument("--reynolds", nargs="+", type=float)
    parser.add_argument("--angles", nargs="+", type=float)
    parser.add_argument("--run-dir", type=Path)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--run", action="store_true")
    args = parser.parse_args()
    try:
        plan = build_plan(args.airfoils, args.reynolds, args.angles)
        if not args.prepare and not args.run:
            target = ROOT / "reports" / "cfd_plan.json"
            target.parent.mkdir(exist_ok=True)
            target.write_text(json.dumps(plan, indent=2), encoding="utf-8")
            print(f"Planned {len(plan)} cases: {target}")
            return 0
        if args.run:
            for tool in ("blockMesh", "checkMesh", "simpleFoam"):
                if shutil.which(tool) is None:
                    raise RuntimeError(f"{tool} unavailable; source OpenFOAM v2412 first")
        run_dir = args.run_dir or ROOT / "cfd_study" / "runs" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        run_dir.mkdir(parents=True, exist_ok=False)
        (run_dir / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
        outcomes = {}
        for case in plan:
            directory = run_dir / case["airfoil"] / f"Re{case['reynolds']:g}" / f"alpha_{case['alpha_deg']:+g}"
            prepare_case(case, directory)
            if args.run:
                try:
                    quality = run_case(directory)
                except (RuntimeError, subprocess.CalledProcessError, OSError, ValueError, KeyError) as exc:
                    quality = {"accepted": False, "reasons": [str(exc)]}
                    (directory / "quality.json").write_text(json.dumps(quality, indent=2))
                outcomes[(case["airfoil"], case["reynolds"], case["alpha_deg"])] = quality
                print(f"{directory.name}: {'ACCEPTED' if quality['accepted'] else 'REJECTED'}")
        if args.run:
            count = export_polars(plan, outcomes, run_dir / "polars")
            rejected = sum(not q["accepted"] for q in outcomes.values())
            print(f"Exported {count} complete polars; {rejected} rejected cases. Results: {run_dir}")
            return 1 if rejected else 0
        print(f"Prepared {len(plan)} cases in {run_dir}; no solver was executed")
        return 0
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(1, f"Study unavailable: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
