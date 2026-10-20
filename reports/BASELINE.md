# Current preliminary calculation

Analytical estimate; CFD, CAD mass and hardware validation pending.

| Quantity | Estimate |
| --- | ---: |
| Vertical thrust | 8.400 N |
| Horizontal thrust | 0.000002 N |
| Electrical power | 189.41 W |
| Figure of merit | 0.5134 |
| Estimated mass | 331.108 g |
| Thrust / module weight | 2.587 |
| Pitch phase for vertical thrust | 19.675 deg |
| Reynolds range | 43774 to 91317 |

- Empirical Re-independent analytical coefficients and continuous stall approximation
- Uniform inflow and empirical blockage; cyclic pitching not CFD validated
- Shaft mass from gross solid geometry; other BOM masses remain estimates
- CAD mass, structural, thermal and hardware verification pending

Regenerate with `python scripts/generate_baseline_report.py`. Full inputs and hashes: [baseline.json](baseline.json).
