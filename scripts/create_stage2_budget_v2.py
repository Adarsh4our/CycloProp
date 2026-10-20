import sys
sys.stdout.reconfigure(encoding='utf-8')
import openpyxl, csv
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Font, Alignment, Border, Side

def build_revised_budget():
    wb = openpyxl.load_workbook('budget_template_downloaded.xlsx')
    ws = wb.active

    # Header info
    ws['B1'] = 'Grand Challenge 2: CycloProp - Advanced UAV Propulsion Challenge'
    ws['B2'] = 'CycloProp (Team Leader: Adarsh Singh)'

    CAE_CAT = 'Software / Computing / Computer-Aided Engineering (CAE) / Subscription'
    MECH_CAT = 'Mechanical / Structural / Fabrication'
    COMP_CAT = 'Components / Electronics'
    OTHER_CAT = 'Other Direct Technical Expenses'

    items = [
        (1, CAE_CAT,
         'SanDisk Extreme 1TB Portable External SSD (USB 3.2 Gen 2 Type-C, Up to 1050MB/s Read, IP65 Water/Dust Resistant) — FAQ-approved for simulation logs & dedicated external Linux OS environment',
         'Amazon India / SanDisk India', 17999,
         'PUSHPAK Stage 2 FAQ explicitly approves external SSDs for simulation storage. High-speed NVMe 1050MB/s rugged external drive required to host a dedicated bootable Linux OS (Ubuntu 24.04 LTS), execute OpenFOAM 2D CFD solvers, and archive massive unsteady VTK simulation flow-field logs (D3, D4). Live verified Amazon India retail rate.'),
        (2, CAE_CAT,
         '512GB M.2 NVMe PCIe Gen4 x4 Internal SSD (Pack of 2 pcs: Crucial P3 Plus / WD Blue SN580 500GB @ ₹3,500 each) — high-speed simulation workspace expansion for team workstations',
         'Amazon India / Crucial India / Western Digital', 7000,
         'High-speed Gen4 NVMe internal solid-state drives (2 units @ ₹3,500 each) to upgrade team workstations with dedicated high-IOPS Linux/OpenFOAM computational partitions, preventing disk bottlenecks during parallel grid generation and transient FEA stress runs (D3, D4).'),
        (3, CAE_CAT,
         'Cloud HPC On-Demand Compute Credits — parallel 2D OpenFOAM AoA parameter sweeps & Richardson mesh convergence study',
         'AWS India / DigitalOcean India', 9000,
         'Running 200+ parallel 2D CFD cases (17 AoA x pitch amplitudes x 3 grid densities) simultaneously on cloud for overnight convergence vs. 6 days of sequential laptop runs. Required for D3 aerodynamic thrust validation (11.76N target, FM=0.768).'),
        (4, CAE_CAT,
         'Google One AI Premium (Gemini Advanced / Ultra) Subscription — 2 Months (₹1,950/mo incl. Indian GST)',
         'Google India Pvt. Ltd.', 3900,
         'AI-assisted computational engineering subscription (Google India Pvt. Ltd., GST-compliant tax invoice) across the 2-month Stage 2 development period. Accelerates OpenFOAM mesh automation scripting, Python BEMT solver optimization, SolidWorks macro automation, and complex mathematical deliverable verification (D1–D6).'),
        (5, COMP_CAT,
         'Raw ASTM Material Coupon Stock: UD CFRP prepreg sample (50x200mm x3), G10 FR4 sheet (150x150mm x2), 4130 Chromoly rod section, 7075-T6 Al bar slug, Igus JFM-0306-04 polymer bushing x4',
         'Carbon Craft India / PCB Unlimited / Igus India', 8000,
         'D5 explicitly requires photographic evidence of physical material samples. Raw coupon specimens enable dimensional verification, mass-density confirmation, and macro photography for the material selection dossier. NOT functional assemblies — raw specimen stock only.'),
        (6, MECH_CAT,
         'FDM Desktop 3D Printed Kinematic Clearance Verification Set — eccentric carriage ring, 4-bar linkage, pitch horn, pushrod assembly (non-structural, non-flight PETG/PLA; visual interference check only)',
         'IIT Ropar Mechatronics Lab / Local 3D Bureau', 4500,
         'D1/D2 kinematic design verification consumable. Physical eccentric linkage model allows manual verification of gimbal-lock absence, pushrod toggle clearance, and eccentric carriage travel (e<=6.88mm), correlating SolidWorks Motion simulation with physical reality before design freeze.'),
        (7, OTHER_CAT,
         'Professional A3 Large-Format Engineering Drawings, Technical Report Dossier Printing & Archival Binding x3 sets (GA drawings, FEA contour plots, kinematic trace diagrams, 2D manufacturing drawings)',
         'Print Solutions / Campus Print Centre', 5500,
         'Three formal A3 dossier sets for faculty mentor (Dr. Shashi Shekhar Jha), IIT Ropar CoDRAS archive, and master review copy. Supports all D1-D6 deliverable documentation and evaluation readiness.'),
        (8, OTHER_CAT,
         'High-Speed Archival Flash Drives x3 (SanDisk Ultra USB 3.0 64GB @ ₹1,000 each) + Dedicated Broadband Data Top-Up for multi-GB CAD and CFD file transfers',
         'SanDisk India / Amazon India', 3200,
         'Physical offline submission media archive for faculty mentor and broadband for multi-GB OpenFOAM and SolidWorks dataset synchronisation across the Stage 2 simulation campaign.'),
        (9, OTHER_CAT,
         'Miscellaneous Design Verification Consumables (Themisto TH-M61 150mm digital vernier caliper, engineering graph paper, adhesive labels for material specimen cataloguing)',
         'Amazon India / Local Stationery', 1000,
         'Lab consumables for material coupon cataloguing, precision digital dimensional spot-checks (coupon thickness, bushing OD verification), and physical design verification activities directly tied to D5 deliverable photography.'),
    ]

    ws.delete_rows(6, 7)
    ws.insert_rows(6, len(items))

    font_regular = Font(name='Calibri', size=11)
    font_bold = Font(name='Calibri', size=11, bold=True)
    align_center = Alignment(horizontal='center', vertical='center', wrap_text=True)
    align_left = Alignment(horizontal='left', vertical='center', wrap_text=True)
    align_right = Alignment(horizontal='right', vertical='center')
    thin = Side(border_style='thin', color='D3D3D3')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for idx, item in enumerate(items, start=6):
        sr, cat, part, vend, amt, just = item
        ws.cell(idx, 1, sr).alignment = align_center
        ws.cell(idx, 2, cat).alignment = align_left
        ws.cell(idx, 3, part).alignment = align_left
        ws.cell(idx, 4, vend).alignment = align_left
        ws.cell(idx, 5, amt).alignment = align_right
        ws.cell(idx, 5).number_format = u'\u20b9#,##0'
        ws.cell(idx, 6, just).alignment = align_left
        for col in range(1, 7):
            ws.cell(idx, col).font = font_regular
            ws.cell(idx, col).border = border
        ws.row_dimensions[idx].height = 50

    total_row = 6 + len(items)
    ws.cell(total_row, 1, 'Total Stage 2 Requirement').font = font_bold
    ws.cell(total_row, 1).alignment = align_left
    formula = '=SUM(E6:E' + str(total_row - 1) + ')'
    ws.cell(total_row, 5, formula).font = font_bold
    ws.cell(total_row, 5).alignment = align_right
    ws.cell(total_row, 5).number_format = u'\u20b9#,##0'
    ws.row_dimensions[total_row].height = 25

    dv_formula = ('"Components / Electronics,Mechanical / Structural / Fabrication,'
                  'Software / Computing / Computer-Aided Engineering (CAE) / Subscription,'
                  'Testing / Validation,Other Direct Technical Expenses"')
    dv = DataValidation(type='list', formula1=dv_formula, allow_blank=True)
    ws.add_data_validation(dv)
    dv.add('B6:B' + str(total_row - 1))

    for r in range(total_row + 1, ws.max_row + 1):
        c1 = ws.cell(r, 1)
        if c1.value is False:
            c1.value = True
        if c1.value == 'Date:':
            ws.cell(r, 2, '18 October 2026').font = font_bold

    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 28
    ws.column_dimensions['C'].width = 48
    ws.column_dimensions['D'].width = 24
    ws.column_dimensions['E'].width = 16
    ws.column_dimensions['F'].width = 52

    path_xlsx = 'PUSHPAK_Stage2_Budget_Proposal_CycloProp_v2.xlsx'
    wb.save(path_xlsx)
    
    # Also export CSV
    path_csv = 'PUSHPAK_Stage2_Budget_Proposal_CycloProp_v2.csv'
    with open(path_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        for row in ws.iter_rows(values_only=True):
            writer.writerow(row)

    total = sum(i[4] for i in items)
    print('Saved XLSX:', path_xlsx)
    print('Saved CSV:', path_csv)
    print('Items count:', len(items))
    print('Total: Rs.' + str(total))
    print('Forfeit: Rs.' + str(100000 - total))

if __name__ == '__main__':
    build_revised_budget()
