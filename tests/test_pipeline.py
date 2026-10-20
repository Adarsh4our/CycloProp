"""Regression checks for numerical consistency and CFD data acceptance."""

import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "cfd_study" / "scripts")]

from cyclorotor_sizing import (
    ConvergenceError, CyclorotorAeroModel, CyclorotorGeometry, InvalidPerformanceError,
)
from project_config import BASELINE, bom_rows, load_config, shaft_mass_g
from cfd_quality import assess_history, RESIDUALS
from integrate_cfd_polars import CFDPolarAeroModel, cross_validate, load_polar
from run_openfoam_sweep import build_plan, export_polars, prepare_case, read_case_history


def polar(reynolds=50000, drag=0.02):
    return {
        "alpha": np.radians([-40., 0., 40.]),
        "alpha_deg": np.array([-40., 0., 40.]),
        "Cl": np.array([-1., 0., 1.]),
        "Cd": np.array([0.9, drag, 0.8]),
        "Cm": np.zeros(3), "reynolds": reynolds,
        "accepted": True, "source": "synthetic regression fixture",
    }


def stable_history():
    return pd.DataFrame({
        "iteration": np.arange(10, 410, 10),
        "Cl": np.full(40, 0.5), "Cd": np.full(40, 0.02), "Cm": np.zeros(40),
        **{name: np.full(40, 1e-6) for name in RESIDUALS},
    })


class RotorTests(unittest.TestCase):
    def setUp(self):
        self.model = CyclorotorAeroModel()
        self.geometry = CyclorotorGeometry(**BASELINE["geometry"])

    def test_phase_rotation_preserves_thrust_power_and_rotates_force(self):
        base = self.model.solve_hover_state(self.geometry, 2640, 35, blockage_factor=0.96)
        for phase in (45, 90, 180, 270):
            with self.subTest(phase=phase):
                result = self.model.solve_hover_state(
                    self.geometry, 2640, 35, phi_0_deg=phase, blockage_factor=0.96
                )
                angle = np.radians(phase)
                rotation = np.array([[np.cos(angle), -np.sin(angle)],
                                     [np.sin(angle), np.cos(angle)]])
                expected = rotation @ [base["thrust_X_N"], base["thrust_Z_N"]]
                np.testing.assert_allclose(
                    [result["thrust_X_N"], result["thrust_Z_N"]], expected, atol=1e-8
                )
                self.assertAlmostEqual(result["P_elec_W"], base["P_elec_W"], places=8)

    def test_vertical_target_and_inflow_closure(self):
        result = self.model.solve_hover_direction(self.geometry, 2640, 35, blockage_factor=0.96)
        self.assertLess(abs(result["thrust_X_N"]), 1e-3)
        self.assertGreater(result["thrust_Z_N"], 0)
        self.assertLess(result["inflow_residual_m_s"], 1e-6)
        raw = self.model.evaluate_azimuth(
            self.geometry, 2640, 35, phi_0_deg=result["phi_0_deg"], v_i=result["inflow_XZ"]
        )
        force = np.array([raw["F_X_multi"].mean(), raw["F_Z_multi"].mean()])
        expected = force / np.sqrt(2 * self.model.rho * self.geometry.swept_area * np.linalg.norm(force))
        np.testing.assert_allclose(result["inflow_XZ"], expected, atol=1e-6)

    def test_direction_targeting_all_quadrants(self):
        for direction in (90, 180, 270):
            result = self.model.solve_hover_direction(self.geometry, 2640, 35, thrust_direction_deg=direction)
            error = (result["thrust_direction_deg"] - direction + 180) % 360 - 180
            self.assertLess(abs(error), 1e-3)

    def test_iteration_exhaustion_is_an_error(self):
        with self.assertRaises(ConvergenceError):
            self.model.solve_hover_state(self.geometry, 2640, 35, max_iter=1)

    def test_invalid_efficiency_is_not_clipped(self):
        class UnderpoweredModel(CyclorotorAeroModel):
            def evaluate_azimuth(self, *args, **kwargs):
                result = super().evaluate_azimuth(*args, **kwargs)
                result["Q_multi"] *= 0.01
                return result
        model = UnderpoweredModel()
        result = model.solve_hover_state(self.geometry, 2640, 35, strict=False)
        self.assertGreater(result["figure_of_merit"], 1)
        self.assertFalse(result["physical_consistent"])
        with self.assertRaises(InvalidPerformanceError):
            model.solve_hover_state(self.geometry, 2640, 35)

    def test_invalid_operating_inputs(self):
        for kwargs in ({"rpm": 0}, {"rpm": -1}, {"rpm": float("nan")},
                       {"theta_0_deg": 90}, {"blockage_factor": 1.5}, {"max_iter": 0}):
            inputs = {"rpm": 2640, "theta_0_deg": 35, **kwargs}
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.model.solve_hover_state(self.geometry, **inputs)

    def test_unknown_airfoil_and_pitch_schedule(self):
        g = CyclorotorGeometry(.095, .22, .038, airfoil="NACA 0018")
        with self.assertRaisesRegex(ValueError, "No analytical polar"):
            self.model.solve_hover_state(g, 2640, 35)
        with self.assertRaises(ValueError):
            self.model.evaluate_azimuth(self.geometry, 2640, 35, pitch_schedule="typo")

    def test_geometry_and_azimuth_validation(self):
        with self.assertRaises(ValueError):
            CyclorotorGeometry(0, .22, .038)
        with self.assertRaises(ValueError):
            self.model.evaluate_azimuth(self.geometry, 2640, 35, num_azimuth=359)

    def test_cam_periodic_rotation(self):
        first = self.model.evaluate_azimuth(self.geometry, 2640, 35, pitch_schedule="asymmetric_cam")
        rotated = self.model.evaluate_azimuth(
            self.geometry, 2640, 35, phi_0_deg=90, pitch_schedule="asymmetric_cam"
        )
        np.testing.assert_allclose(rotated["alpha_eff_deg"], np.roll(first["alpha_eff_deg"], 90), atol=1e-10)


class PolarTests(unittest.TestCase):
    def test_signed_drag_reproduces_positive_negative_and_zero_points(self):
        p = polar()
        model = CFDPolarAeroModel({"NACA 0012": p})
        cl, cd, _ = model.get_airfoil_polars(p["alpha"], np.full(3, 50000), None, None, 6)
        profile_drag = cd - cl**2 / (np.pi * 6 * model.e_oswald)
        np.testing.assert_allclose(profile_drag, [0.9, 0.02, 0.8])

    def test_reynolds_interpolation(self):
        model = CFDPolarAeroModel({"naca0012": [polar(50000, .02), polar(100000, .04)]})
        _, cd, _ = model.get_airfoil_polars(np.zeros(3), np.array([50000, 75000, 100000]), None, None, 6)
        np.testing.assert_allclose(cd, [.02, .03, .04])

    def test_coverage_and_missing_airfoil_errors(self):
        model = CFDPolarAeroModel({"naca0012": polar()})
        for angle, reynolds in ((45, 50000), (0, 30000), (float("nan"), 50000)):
            with self.subTest(angle=angle, reynolds=reynolds), self.assertRaises(ValueError):
                model.get_airfoil_polars(np.radians([angle]), np.array([reynolds]), None, None, 6)
        with self.assertRaises(ValueError):
            model.get_airfoil_polars(np.zeros(1), np.array([50000]), None, None, 6, airfoil="NACA 0018")

    def test_invalid_polar_data(self):
        for field, value in (("alpha", np.array([0., 0., 1.])),
                             ("Cd", np.array([.1, -1., .1])),
                             ("Cl", np.array([0., float("nan"), 1.])),
                             ("accepted", False)):
            p = polar()
            p[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                CFDPolarAeroModel({"naca0012": p})
        with self.assertRaises(ValueError):
            CFDPolarAeroModel({"naca0012": [polar(), polar()]})

    def test_loader_sorts_rows_and_requires_current_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "naca0012_openfoam_Re50k.csv"
            path.write_text("alpha_deg,Cl,Cd,Cm\n40,1,.8,0\n-40,-1,.9,0\n0,0,.02,0\n")
            with self.assertRaises(ValueError):
                load_polar(path)
            p = load_polar(path, require_accepted=False)
            np.testing.assert_array_equal(p["alpha_deg"], [-40, 0, 40])
            metadata = {"numerically_accepted": True, "reynolds": 50000,
                        "angles_deg": [-40, 0, 40], "csv_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            path.with_suffix(".json").write_text(json.dumps(metadata))
            self.assertTrue(load_polar(path)["accepted"])
            path.write_text(path.read_text().replace(".02", ".03"))
            with self.assertRaises(ValueError):
                load_polar(path)

    def test_cross_validation_requires_matching_conditions(self):
        with self.assertRaises(ValueError):
            cross_validate(polar(50000), polar(100000))
        second = polar()
        second["alpha"] += .01
        with self.assertRaises(ValueError):
            cross_validate(polar(), second)


class CFDWorkflowTests(unittest.TestCase):
    def test_stable_history_passes(self):
        self.assertTrue(assess_history(stable_history())["accepted"])

    def test_rejects_residuals_oscillation_missing_and_short_history(self):
        variants = []
        residual = stable_history()
        residual.loc[39, "res_p"] = .02
        variants.append(residual)
        unstable = stable_history()
        unstable.loc[39, "Cl"] = 1.5
        variants.append(unstable)
        variants.append(stable_history().drop(columns="res_omega"))
        variants.append(stable_history().head(5))
        missing = stable_history()
        missing.loc[39, "res_k"] = np.nan
        variants.append(missing)
        for history in variants:
            self.assertFalse(assess_history(history)["accepted"])

    def test_airfoil_meshes_differ_and_inputs_match_reynolds(self):
        plan = build_plan(["naca0012", "naca0015"], [50000], [0])
        self.assertNotEqual(plan[0]["coordinate_sha256"], plan[1]["coordinate_sha256"])
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            paths = [prepare_case(c, Path(directory) / c["airfoil"]) for c in plan]
            self.assertNotEqual((paths[0] / "system/blockMeshDict").read_bytes(),
                                (paths[1] / "system/blockMeshDict").read_bytes())
            case = plan[0]
            re_actual = case["velocity_m_s"] * case["chord_m"] * case["fluid"]["rho"] / case["fluid"]["mu"]
            self.assertAlmostEqual(re_actual, 50000)
            self.assertIn(f"uniform ({case['velocity_m_s']:.12g} 0 0)", (paths[0] / "0/U").read_text())
            with self.assertRaises(FileExistsError):
                prepare_case(case, paths[0])

    def test_plan_has_all_requested_geometry_angle_and_re_combinations(self):
        plan = build_plan(["naca0012", "naca0009"], [50000, 100000], [-5, 0, 5])
        self.assertEqual(len(plan), 12)
        for args in ((["missing"], [50000], [0]), (["naca0012"], [-1], [0]),
                     (["naca0012"], [50000], [0, 0])):
            with self.assertRaises(ValueError):
                build_plan(*args)

    def test_header_based_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            case = Path(directory)
            coeff = case / "postProcessing/forceCoeffs/0/coefficient.dat"
            coeff.parent.mkdir(parents=True)
            coeff.write_text("# Time CmPitch Cd Cl\n10 -0.01 0.02 0.5\n")
            (case / "log.simpleFoam").write_text("Time = 10\nGAMG: Solving for p, Initial residual = 1e-6, Final residual = 0, No Iterations 1\n")
            history = read_case_history(case)
            self.assertEqual(history.iloc[0].Cl, .5)
            self.assertEqual(history.iloc[0].Cm, -.01)
            self.assertEqual(history.iloc[0].res_p, 1e-6)

    def test_rejected_angle_blocks_whole_polar_and_export_binds_metadata(self):
        plan = build_plan(["naca0012"], [50000], [-5, 0, 5])
        quality = assess_history(stable_history())
        outcomes = {(c["airfoil"], c["reynolds"], c["alpha_deg"]): copy.deepcopy(quality) for c in plan}
        with tempfile.TemporaryDirectory() as directory:
            outcomes[("naca0012", 50000, 5)]["accepted"] = False
            self.assertEqual(export_polars(plan, outcomes, directory), 0)
            self.assertFalse(list(Path(directory).glob("*.csv")))
            outcomes[("naca0012", 50000, 5)]["accepted"] = True
            self.assertEqual(export_polars(plan, outcomes, directory), 1)
            path = next(Path(directory).glob("*.csv"))
            self.assertTrue(load_polar(path)["accepted"])


class MassTests(unittest.TestCase):
    def test_solid_and_hollow_shaft_mass(self):
        shaft = dict(BASELINE["shaft"])
        self.assertAlmostEqual(shaft_mass_g(shaft), 57.70791545, places=7)
        shaft["inner_diameter_m"] = shaft["outer_diameter_m"] / 2
        self.assertAlmostEqual(shaft_mass_g(shaft), 57.70791545 * .75, places=7)
        shaft["inner_diameter_m"] = shaft["outer_diameter_m"]
        with self.assertRaises(ValueError):
            shaft_mass_g(shaft)

    def test_bom_and_geometry_share_total(self):
        config = load_config()
        total = sum(r["total_mass_g"] for r in bom_rows(config))
        self.assertAlmostEqual(total, 331.10791545, places=7)
        self.assertAlmostEqual(config["geometry"]["total_module_mass"] * 1000, total)


if __name__ == "__main__":
    unittest.main()
