"""Shared inputs for current analyses. Historical submissions remain snapshots."""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "baseline.json"


def shaft_mass_g(shaft):
    outer = shaft["outer_diameter_m"]
    inner = shaft["inner_diameter_m"]
    length = shaft["length_m"]
    density = shaft["density_kg_m3"]
    if not all(math.isfinite(v) for v in (outer, inner, length, density)):
        raise ValueError("Shaft dimensions and density must be finite")
    if not 0 <= inner < outer or length <= 0 or density <= 0:
        raise ValueError("Invalid shaft dimensions or density")
    return math.pi / 4 * (outer**2 - inner**2) * length * density * 1000


def bom_rows(config):
    rows = []
    for item in config["bom"]:
        quantity = item["quantity"]
        unit_mass = (shaft_mass_g(config["shaft"]) if item.get("mass_from") == "shaft"
                     else item["unit_mass_g"])
        if not isinstance(quantity, int) or quantity <= 0 or not math.isfinite(unit_mass) or unit_mass <= 0:
            raise ValueError(f"Invalid BOM item: {item['component']}")
        rows.append({**item, "unit_mass_g": unit_mass, "total_mass_g": quantity * unit_mass})
    return rows


def load_config(path=CONFIG_PATH):
    with Path(path).open(encoding="utf-8") as stream:
        config = json.load(stream)
    config["geometry"]["total_module_mass"] = sum(
        row["total_mass_g"] for row in bom_rows(config)
    ) / 1000
    return config


BASELINE = load_config()
