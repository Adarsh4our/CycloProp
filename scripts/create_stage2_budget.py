import sys
sys.stdout.reconfigure(encoding='utf-8')
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def build_budget_proposal():
    # Load original template
    wb = openpyxl.load_workbook('budget_template_downloaded.xlsx')
    ws = wb.active

    # Set Header Info
    ws['B1'] = "Grand Challenge 2: CycloProp - Advanced UAV Propulsion Challenge"
    ws['B2'] = "CycloProp (Team Leader: Adarsh Singh)"
    
    # 16 Detailed Line Items
    items = [
        # Testing / Validation
        (
            1,
            "Testing / Validation",
            "Multi-Axis Static/Dynamic Force & Torque Load Cell (5 kg capacity, S-Beam strain gauge transducer for measuring vertical lift Fz and horizontal vector force Fx)",
            "Robu.in / Phidgets India",
            16500,
            "Direct instrumentation for Deliverable D6 (Build-and-Test Plan, Test T2) to calibrate test-bench geometry and validate BEMT/CFD 10N-12N thrust predictions."
        ),
        (
            2,
            "Testing / Validation",
            "High-Speed Multi-Channel USB DAQ Interface & Signal Conditioning Module (16-bit high-sampling rate ADC interface)",
            "Robu.in / Amazon India",
            8500,
            "High-frequency data acquisition required to capture instantaneous load cell voltages and dynamic thrust ripple without aliasing under 44 Hz blade pass frequencies."
        ),
        (
            3,
            "Testing / Validation",
            "Non-Contact Precision Optical Laser Tachometer (2–99,999 RPM with digital optical reflective pick-up)",
            "Amazon India / Robu.in",
            3200,
            "Direct measurement of rotating endplate speed to verify the 2640 RPM operating point against ESC telemetry (Test T4)."
        ),
        (
            4,
            "Testing / Validation",
            "High-Accuracy Digital Analytical Balance (0.01 g resolution, 500 g range)",
            "Wensar India / Amazon India",
            2800,
            "Precision mass verification of manufactured CFRP coupons, fasteners, and mockups to validate the 301.4 g CAD mass budget (Deliverables D1, D5, D6)."
        ),
        (
            5,
            "Testing / Validation",
            "High-Current / High-Voltage Shunt Power Telemetry Module (Dual INA226 / 100A bidirectional I2C power sensor)",
            "Robu.in",
            3000,
            "Electrical telemetry sensor setup to measure 14.2A continuous current draw and verify hover electrical power consumption (P_elec <= 209.8 W) for Test T3."
        ),

        # Mechanical / Structural / Fabrication
        (
            6,
            "Mechanical / Structural / Fabrication",
            "1:1 Scale SLS PA12 3D Printed Kinematic Swashplate & Carriage Assembly (Selective Laser Sintering of 2-DOF inner carriage plate, outer ring, guide brackets, and blade pitch horns)",
            "Imaginarium India / Indiaprot",
            14500,
            "Highest-impact physical validation: Full-scale physical kinematic mockup to verify 2-DOF eccentric travel (e <= 6.88 mm), non-binding pushrod kinematics, and zero mechanical collisions (Deliverable D2, D8)."
        ),
        (
            7,
            "Mechanical / Structural / Fabrication",
            "Precision CNC Workshop Machining of Hub Adapters & Ground Shaft Coupling Journals (7075-T6 aluminum hubs, roll-pin reaming, and shaft test couplers)",
            "Prototype Fabricators / Indiaprot",
            8500,
            "Precision turning and reaming to verify shaft slide fits (h7/H7), DIN 1481 roll-pin engagement, and endplate perpendicularity under high torque (Deliverable D1, D8)."
        ),
        (
            8,
            "Mechanical / Structural / Fabrication",
            "Precision FDM PETG 3D Printed Chassis Fairings & Motor Cooling Duct Scoop (NACA 0025 teardrop fairing sleeves and downwash cooling duct)",
            "Robu.in / Local 3D Bureau",
            4000,
            "Physical verification of snap-on standoff fairing geometry and aerodynamic motor duct fit to validate wake blockage mitigation and thermal dissipation claims (Deliverables D1, D3, D5)."
        ),

        # Components / Electronics
        (
            9,
            "Components / Electronics",
            "BLDC Drivetrain Propulsion Motor (T-Motor MN3508 380KV with verified cross-pattern mount & telemetry ESC)",
            "Robu.in / QuadKopter India",
            8500,
            "Physical procurement of the master baseline propulsion unit to verify dimensional mounting fit in CAD cradle, motor base boss clearances, and bench test calibration (Deliverable D5, D6)."
        ),
        (
            10,
            "Components / Electronics",
            "High-Speed Micro Pitch Actuation Servos (KST X08 V5 Ultra-Slim 8mm Steel Gear Micro Servos x 2 pcs)",
            "Robu.in / DroneEdge India",
            5800,
            "Baseline pitch actuation hardware procured to physically measure transit slew latency (14.5 ms), gear backlash, and mounting pocket fit on Pillar 2 (Deliverables D2, D5, D6)."
        ),
        (
            11,
            "Components / Electronics",
            "Self-Lubricating Polymer Flanged Bushings (Igus Iglide J JFM-0306-04 x 8 pcs)",
            "Igus India Pvt. Ltd. (Pune)",
            2200,
            "Direct procurement of critical trunnion polymer bushings to measure press-fit tolerances in G10 endplates, photograph for Material Selection (Deliverable D5), and verify zero false-brinelling."
        ),
        (
            12,
            "Components / Electronics",
            "Aerospace Composite Material Coupons & Tubes (UD Carbon Prepreg Sheet, G10 FR4 1.5mm plate, Ø4 mm Carbon Spar Tubes)",
            "Carbon Craft India / PCB Unlimited",
            3500,
            "Material specimen procurement for physical coupon weighing, laminate thickness verification, and photographic evidence for Deliverable D5 (Material Selection)."
        ),

        # Software / Computing / CAE / Subscription
        (
            13,
            "Software / Computing / Computer-Aided Engineering (CAE) / Subscription",
            "High-Speed External NVMe/USB 3.2 Gen 2 Archival SSD (1 TB, 1050 MB/s transfer rate)",
            "Amazon India / Crucial India",
            6500,
            "Explicitly approved in Stage 2 FAQ. Required for high-speed local archival and backup of massive OpenFOAM 3D transient meshes, SolidWorks assemblies, and transient FEA stress field databases across the 2-month simulation campaign."
        ),
        (
            14,
            "Software / Computing / Computer-Aided Engineering (CAE) / Subscription",
            "Cloud High-Performance Computing (HPC) Simulation Credits (Cloud compute instances for large multi-grid CFD & FEA solutions)",
            "AWS India / DigitalOcean India / Microsoft India",
            5000,
            "High-core compute resources for solving high-resolution Navier-Stokes 2D/3D aerodynamic sweeps and multi-body dynamic transient solvers beyond local workstation capacity (Deliverable D3, D4)."
        ),

        # Other Direct Technical Expenses
        (
            15,
            "Other Direct Technical Expenses",
            "Professional Large-Format A3 Plotting, Engineering GA Dossiers & Archival Binding (Color plots of engineering drawings, exploded BOM callouts, and FEA contour plots x 3 sets)",
            "Print Solutions / Campus Print Centre",
            4500,
            "High-resolution large-format A3 technical documentation and official formal design dossiers for faculty review, lab archival, and evaluation readiness."
        ),
        (
            16,
            "Other Direct Technical Expenses",
            "High-Speed Technical Data Connectivity & Archival Submission Media (Encrypted USB 3.2 64GB flash drives x 3 + dedicated broadband data top-up)",
            "SanDisk India / Amazon India",
            2000,
            "Physical offline submission media archive for faculty mentor and high-bandwidth transfer of multi-gigabyte CAE datasets."
        )
    ]

    # Delete template default 7 empty rows (rows 6 to 12)
    # ws.delete_rows(idx, amount)
    ws.delete_rows(6, 7)

    # Insert 16 rows at row 6
    ws.insert_rows(6, len(items))

    # Styling definitions
    font_regular = Font(name="Calibri", size=11)
    font_bold = Font(name="Calibri", size=11, bold=True)
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center")
    
    thin_border_side = Side(border_style="thin", color="D3D3D3")
    table_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

    # Write items
    for idx, item in enumerate(items, start=6):
        sr, cat, part, vend, amt, just = item
        ws.cell(row=idx, column=1, value=sr).alignment = align_center
        ws.cell(row=idx, column=2, value=cat).alignment = align_left
        ws.cell(row=idx, column=3, value=part).alignment = align_left
        ws.cell(row=idx, column=4, value=vend).alignment = align_left
        ws.cell(row=idx, column=5, value=amt).alignment = align_right
        ws.cell(row=idx, column=5).number_format = '₹#,##0'
        ws.cell(row=idx, column=6, value=just).alignment = align_left

        for col in range(1, 7):
            cell = ws.cell(row=idx, column=col)
            cell.font = font_regular
            cell.border = table_border
        
        ws.row_dimensions[idx].height = 42

    # Total Row (now at row 6 + 16 = 22)
    total_row = 6 + len(items)
    ws.cell(row=total_row, column=1, value="Total Stage 2 Requirement").font = font_bold
    ws.cell(row=total_row, column=1).alignment = align_left
    ws.cell(row=total_row, column=5, value=f"=SUM(E6:E{total_row-1})").font = font_bold
    ws.cell(row=total_row, column=5).alignment = align_right
    ws.cell(row=total_row, column=5).number_format = '₹#,##0'
    ws.row_dimensions[total_row].height = 25

    # Re-apply Data Validation to Category column (B6:B21)
    dv = DataValidation(
        type="list", 
        formula1='"Components / Electronics,Mechanical / Structural / Fabrication,Software / Computing / Computer-Aided Engineering (CAE) / Subscription,Testing / Validation,Other Direct Technical Expenses"',
        allow_blank=True
    )
    ws.add_data_validation(dv)
    dv.add(f"B6:B{total_row-1}")

    # Financial declarations rows shifted by +9 (16 - 7 = 9)
    # Search for "We hereby certify that:"
    for r in range(total_row + 1, ws.max_row + 1):
        c1 = ws.cell(row=r, column=1)
        c2 = ws.cell(row=r, column=2)
        if c1.value is False:
            c1.value = True  # Check all certification boxes
            c1.font = font_bold
            c1.alignment = align_center
        if c1.value == "Date:":
            ws.cell(row=r, column=2, value="18 October 2026").font = font_bold

    # Column Widths
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 28
    ws.column_dimensions['C'].width = 46
    ws.column_dimensions['D'].width = 24
    ws.column_dimensions['E'].width = 16
    ws.column_dimensions['F'].width = 50

    output_path = 'PUSHPAK_Stage2_Budget_Proposal_CycloProp.xlsx'
    wb.save(output_path)
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    build_budget_proposal()
