with open('CYCLOPROP_MASTER_KNOWLEDGE_BASE.md', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()
print('Total lines in updated master:', len(lines))
print('Total characters:', len(text))

checks = [
    '6.5.9 Rev 3.0 Master Skeleton',
    '6.5.10 Part 01',
    '6.5.11 Part 02',
    '6.5.12 Part 03',
    '6.5.13 Part 04',
    '6.5.14 Part 05',
    '6.5.15 Part 06',
    '6.5.16 Part 07',
    '38. **SolidWorks COM API Automation',
    '39. **Analytical NACA 0012 Profile Equation',
    '40. **Inner Cavity Wall Thickness',
    '41. **Endplate Hub Disc Ø206 mm',
    '42. **Running Air Gap & Full Envelope Clearance',
    '43. **Sizing Solver Cosmetic Default Label',
    'scripts\\generate_naca0012.py',
    'scripts\\audit_blade_dims.py'
]

all_found = True
for c in checks:
    found = c in text
    if not found:
        all_found = False
    print(f'Check \"{c}\": {"FOUND" if found else "NOT FOUND"}')

print("All checks passed:", all_found)
