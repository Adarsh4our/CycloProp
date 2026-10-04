"""Audit: Compare my generated NACA 63-012 vs real UIUC data, and verify all 4-digit airfoils."""
import numpy as np

# ── REAL NACA 63-012A from UIUC (upper surface, tabulated from NACA Report 824) ──
real_63012_x = [0.000, 0.005, 0.0075, 0.0125, 0.025, 0.050, 0.075, 0.100,
                0.150, 0.200, 0.250, 0.300, 0.350, 0.400, 0.450, 0.500,
                0.550, 0.600, 0.650, 0.700, 0.750, 0.800, 0.850, 0.900, 0.950, 1.000]
real_63012_y = [0.000000, 0.009730, 0.011730, 0.014920, 0.020780, 0.028950, 0.035040, 0.039940,
                0.047470, 0.052870, 0.056640, 0.059010, 0.059950, 0.059570, 0.057920, 0.055170,
                0.051480, 0.047000, 0.041860, 0.036210, 0.030260, 0.024260, 0.018260, 0.012250, 0.006250, 0.000250]

x = np.array(real_63012_x)
y_real = np.array(real_63012_y)

# ── MY FAKE 63-012 (from gen_airfoil_coords.py) ──
t = 0.12
y_fake = (t / 0.2) * (
    0.2969*np.sqrt(x) - 0.1260*x - 0.3516*x**2
    + 0.2843*x**3 - 0.1036*x**4
) + 0.006 * np.sin(np.pi * x)

# ── Standard NACA 0012 (4-digit) ──
y_0012 = (t / 0.2) * (
    0.2969*np.sqrt(x) - 0.1260*x - 0.3516*x**2
    + 0.2843*x**3 - 0.1015*x**4
)

print("=" * 90)
print("AUDIT: Real NACA 63-012A (UIUC) vs My Generated vs Standard NACA 0012")
print("=" * 90)
header = f"  {'x/c':>6} | {'REAL 63-012A':>12} | {'MY FAKE':>12} | {'Error%':>7} | {'NACA 0012':>10} | {'Real vs 0012':>12}"
print(header)
print("  " + "-" * 80)

errors = []
for i in range(len(x)):
    err = abs(y_fake[i] - y_real[i]) / (y_real[i] + 1e-8) * 100 if y_real[i] > 0.001 else 0
    errors.append(err)
    diff = y_real[i] - y_0012[i]
    flag = " *** BAD" if err > 5 else ""
    print(f"  {x[i]:>6.4f} | {y_real[i]:>12.6f} | {y_fake[i]:>12.6f} | {err:>6.1f}% | {y_0012[i]:>10.6f} | {diff:>+12.6f}{flag}")

print("=" * 90)
print()
print(f"  Max thickness REAL 63-012A: {max(y_real):.6f} at x/c = {x[np.argmax(y_real)]:.4f}")
print(f"  Max thickness MY FAKE:      {max(y_fake):.6f} at x/c = {x[np.argmax(y_fake)]:.4f}")
print(f"  Max thickness NACA 0012:    {max(y_0012):.6f} at x/c = {x[np.argmax(y_0012)]:.4f}")
print()
print(f"  Average error: {np.mean(errors):.1f}%")
print(f"  Max error:     {max(errors):.1f}%")
print()

if max(errors) > 5:
    print("  VERDICT: NACA 63-012 IS WRONG - my generated coords are a FAKE approximation")
    print("           Need to use the REAL tabulated UIUC data instead.")
else:
    print("  VERDICT: Acceptable tolerance.")

print()
print("=" * 90)
print("NACA 4-digit verification (these use the standard formula)")
print("=" * 90)
for name, tc in [("NACA 0009", 0.09), ("NACA 0012", 0.12), ("NACA 0015", 0.15), ("NACA 0018", 0.18)]:
    x_check = np.array([0.0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.70, 1.00])
    yt = (tc/0.2) * (0.2969*np.sqrt(x_check) - 0.1260*x_check - 0.3516*x_check**2
                     + 0.2843*x_check**3 - 0.1015*x_check**4)
    max_y = max(yt)
    x_max = x_check[np.argmax(yt)]
    expected_half_t = tc / 2.0
    err = abs(max_y - expected_half_t) / expected_half_t * 100
    status = "OK" if err < 2 else "WRONG"
    print(f"  {name}: max y/c = {max_y:.5f} (expected ~{expected_half_t:.4f}) | error = {err:.1f}% | {status}")

print()
print("  NACA 4-digit formula is STANDARD (from NACA Report 460).")
print("  These coordinates are CORRECT for NACA 0009, 0012, 0015, 0018.")
