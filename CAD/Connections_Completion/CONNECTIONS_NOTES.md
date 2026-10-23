# Connections 1-4: provisional CAD implementation - 21 October 2026

This step implements the requested Y drive-tab attachment, positive linkage-pivot retention, a custom spline-drive servo horn, and guide/bearing/hub/frame mounting interfaces. The geometry is not a fabrication release. See the final validation JSON for the parts actually present, saved file hashes and checks performed. A file or label alone does not establish a check passed.

## Y drive tab

The two mounting centres are tab-local (-27,-23) and (-27,-17) mm. They were moved away from the existing carriage holes. The tab has D2.9 clearance holes with D5.2 x90 degree countersinks. Nuts above the carriage would enter the rotating control-ring path, so those provisional through-bolt sets are suppressed. Two M2.5x4 countersunk screws now enter from below the 2mm tab into blind M2.5x0.45 carriage threads. Their head planes sit0.1mm inside the tab underside, giving2.1mm nominal engagement in the3mm carriage.

The native carriage solid shows D2.5 thread-major envelopes depth2.6. Manufacturing callout: tap-drill D2.05 depth2.7 from underside; full usable thread2.3. Do not manufacture the major-envelope diameter as a tap-drill hole. Stripping strength, tolerances, screw length, actual tap point and residual roof thickness require release. No hardware stands above the plate. Suppressed earlier through-bolts, washers and nuts are retained as history, not included in the intended active hardware.

## Four servo-link pivots

The existing pin now has a D2 smooth shoulder5.2mm long, followed by M1.6x0.35 thread-envelope2.3mm long. The D4x1 head remains. Each pin has an ID1.7 OD4 H0.3 washer at the shoulder and an AF3.2 H1.3 M1.6 nut. The nut clamps the washer to the positive shoulder; it does not clamp the link stack. The nominal occupied stack ends5.0mm above the pin shoulder origin, leaving0.2mm axial freedom and0.7mm nominal thread protrusion past the nut.

The pins are custom machined shoulder fasteners, not ordinary fully threaded screws. Bearing finish, hardness, material, diametral fit, fatigue, thread relief and an anti-loosening method remain unverified. Nut and thread solids are envelopes. Both servo-link joints remain free to pivot through their existing mates.

## Servo torque connection

The R12 horn part has been revised from a circular clearance-bore layout to a custom spline-drive design. Its arm remains2mm thick and its linkage pivot remains12mm from the output axis. A hub OD8 extends3.2mm below the arm. The final female cavity uses the output extracted from Savox's official SH-0257MG+ STEP, dated7May2025; the earlier project-derived cavity is suppressed. Inspection found21 crown faces at17.142857-degree spacing. The tool is scaled1.01 (approximately25micrometres radial allowance at a2.5mm radius). The nominal shaft-tip position is0.5mm below the arm underside. An entry reliefD5.2 x0.5 and centre-tip reliefD2.8 remove base/tip contacts, leaving approximately2.2mm nominal tooth engagement. Those allowances are prototype choices requiring manufacturing and load validation.

The retaining-screw clearance isD2.2. A D4.4 head pocket leaves a screw seating plane0.5mm above the arm underside. The M2x3 screw envelope has a D3.8 H2 head, giving nominal2mm threaded engagement below the shaft tip. The actual internal thread depth and head form are unverified.

This is a custom horn based on the official supplier STEP spline. It is not a measured commercial SH11M horn and is not certified interchangeable with delivered hardware. The supplier STEP has5.0mm crown diameter, while its product page specifies21T nominalD4.8. This is a supplier-source conflict; it is not silently resolved. Obtain a toleranced output/horn drawing or a compatible physical sample before manufacturing this cavity. Tooth-root finish, production method, fit, proof load and supplied retaining screw remain unverified. The official archive, STEP, source URL/hash and inspected face records are retained inManufacturer_References.

The output body is instanced as `Savox_Output_Spline_NATIVE_REFERENCE` rotating with each horn. Its legacy filename remains, but the earlier body has been replaced by the official21T output extraction. The copied stationary servo case retains its independent output-axis reference. The original `Savox_SH-0257MG.SLDPRT` remains unchanged. The old clearance-bore concentric mates are suppressed; new axis mates locate the horn. Datum mates index each output body to its horn; no electrical motion or servo torque capability is established. The stationary case remains the project's earlier envelope, rather than a wholesale replacement by the newer supplier case.

## Linear guides

The supplier-native rail and block shapes are retained. Rails have three holes at localY5,20,35mm, D2.4 through and D3.6 x0.8 head pockets. Two M2x1.5-deep block threads are8mm apart, at localX+/-4 andY8.001mm. HIWIN's MGN5C catalogue supports that nominal pattern. Matching holes have been added to the mating base, intermediate and carriage plates.

The rail connections use custom M2x9 low-head reference screws (D3.4 x0.7 head), washers2.2x5x0.3 and AF4 H1.6 nuts. Nominal protrusion is1.3mm. These are not ordinary ISO4762 heads; a real drive form, grade and procurement/manufacturing specification must be established. The supplier's catalogue M2x6 rail bolt recommendation assumes a tapped base, whereas this layout uses through-bolts and nuts in the3mm plates.

The lower block uses M2x2 reference cap screws with D3.8 H2 heads in D4.2 depth2.05 counterbores, leaving0.95mm plate webs and nominal1.05mm thread engagement. The upper block was revised to custom M2x2.5 low-head screws D3.4 H0.7, seated1.5mm above the plate underside, giving1mm nominal engagement. Their head tops are2.2mm above the underside and clear the rotating-retainer head recess. Earlier upper cap screws are suppressed. Short engagement and remaining webs need load and tolerance checks.

The MGN5C part shows thread-pilot geometry, so intentional screw/thread envelope overlap is not evidence of an interference defect. Actual thread pitch/depth must follow the supplier drawing and be checked on delivered guides. Existing supplier rail/block end-region overlaps remain separate, unresolved imported geometry; no metal was trimmed to hide them.

## 6806 bearing retainers

Each retainer has three D2.2 holes. Inner-retainer centres lie onPCD25; outer-retainer centres onPCD45. Matching blind M2x0.4 thread envelopes are in the carriage seat and rotating ring. Callout: D1.6 pilot depth4.8, full thread4mm; native solid shows major-envelopeD2 depth4.3.

Three OD4 ID2.2 H1 spacers bridge the existing1mm gap below the inner retainer. With0.3mm washers and M2x6 screws, nominal threaded engagement is3.7mm. The spacers avoid pulling the cap down across that gap and do not contact the bearing outer ring.

The outer retainer uses0.3mm washers and custom low-head M2x4 screws, headD3.4 H0.7, for3.2mm nominal thread engagement. Their heads sweep over a new carriage-top annular recess fromR20 toR25.5, depth0.7 in the3mm plate. This is a necessary local geometry change for clearance. Screw-head clearance to the upper-block heads is nominally0.3mm. Cap stiffness, outer-race contact lands, residual plate sections, tightening sequence and tolerances require release. Angular indexing between each retainer and its mating tapped pattern must remain fixed when rebuilding the bearing subassembly.

## Revised frame, main shaft and hubs

The intended revised frame is a separate native copy `Frame_Mounting_RevA`; the older `6-Mounting_Chassis_Frame` is preserved. The fixed base receives routed integral support ears ending at X+/-24,Y+/-52mm to place the standoffs outside the eccentric control-ring sweep and moving stop arm. The revised frame origin is46mm above the fixed-base underside. Two support lengths35mm and two29mm account for the existing6mm step in the lower frame mounting feet. Four M3x55 cap-screw reference envelopes, washers3.2x7x0.5 and AF5.5 H2.4 nuts define the attachment. Supplier M3x55 screws have18mm threaded ends, covering the proposed nut positions; exact tolerance and material remain unverified. Left support routes pass outboard at X-42..-36mm; right routes start at X17..23mm beyond Y+/-28mm to avoid existing countersinks. The cantilevered ears require stiffness and strength checks.

The selected main-bearing envelope is686ZZ,6x13x5mm (the unshielded686 is only3.5mm wide, so the suffix matters). Revised frame bearing centres are localZ-2 and251.2mm,253.2mm apart, matching the actual shaft's two5.15mm journal spans. The upper housing extends inward3.8mm; positive outer-race shoulders, a lower spacer and separate caps provide outer-race retention. Cap contact diameters must be checked against the selected bearing's detailed ring faces. The bearing model is a solid annular envelope, not internal geometry or a reliable mass model.

The6x275mm shaft length remains unchanged. Its four groove roots are corrected from the inspected5.0mm to5.7mm for nominal6mm DIN471/DSH6 rings; the existing0.8mm widths remain. Installed ring references reserve a conservative exterior envelope and are not spring-ring manufacturing models. Shaft root is33.575mm above the fixed-base underside, aligning bearing journals. The shaft nose clears the saved control-ring top by3.075mm nominally. The change to groove roots and added hub crossholes changes shaft CAD mass; the260mm calculation baseline is not silently revised.

Separate hub copies have OD28 x3 flanges,13.9 x1.5 pilots,6mm bores and added OD14 x11 collars. Four D2.8 holes onPCD22 use M2.5x8 cap screws, two washers per screw and plain nuts. The revised endplate copies correct the original's inspected15mm centre hole to the documented14mm to match those pilots; originals remain unchanged. This discrepancy is recorded rather than treated as proof the old part was14mm.

The two blade-facing endplate planes are at shaft-localZ32.5 and252.5mm, preserving220mm between them. Their axial stations are2.5mm inward from the old assembly placement to clear main-bearing-cap screw heads. Positive D2 hub/shaft crosspins are at shaft-localZ41.5 and243.5mm. DIN1481 installed2x14 references define the pin envelopes. This selects a positive pinned hub connection; it is not a set-screw torque assumption. Pin fit, fatigue, shaft strength, balance and detailed production drawings remain unreleased.

The new endplate/hub/frame stack is a provisional mounting layout. Blades, blade pitch arms, pushrods, motor coupling and cable routing are not integrated by this step. The legacy rotor assembly and current calculation baseline are preserved. Full motion and complete-module clearance are outside these focused checks.

## Validation and remaining release work

Latest clearance corrections: frame origin46mm above the base underside, shaft origin33.575mm, and support lengths35mm/29mm supersede the earlier44mm,31.575mm and33mm/27mm figures above. The frame hardware washers and nuts move upward2mm accordingly. Routed base ears avoid the drive tab, servo mount and existing countersinks; their stiffness remains unverified. One rail nut was corrected to the underside. Native assembly mates rebuild without errors after these corrections.

Each linkage pin additionally has two ID2.1 OD4 H0.5 thrust spacers, preserving0.2mm nominal axial play. Loctite222 is provisionally selected for steel pin/nut retention; preparation, cure, compatibility and torque remain unverified. The inner and outer6806 retainers now use indexed native lock mates to their supporting parts in Assem3, replacing their earlier free concentric/coincident mate pairs.

Checks are limited to native rebuild and interface dimensions, plus focused static intersections involving changed/new connections. No25-position campaign is repeated. Final results, failures, intentional thread-envelope contacts and exclusions must be read from the validation JSON. No physical tests, measured mass, strength approval or fabrication readiness is claimed.

Final focused static result:451 native solid-boolean comparisons at the saved pose, zero unexpected intersections and six classified screw/thread-envelope contacts. Same-component imported bodies, unchanged-existing pairs and supplier rail/block internal geometry were excluded. This passes only the stated static scope; a complete rotor/actuator motion sweep was not performed. Earlier assembly validation files refer to earlier source hashes and do not certify this revision.

Before fabrication: approve actual servo/spline and special fastener supply; release materials, dimensions, fits and tolerances; verify all short tapped engagements, thin sections, preload and anti-loosening; check main-bearing ring-face contacts and floating/locating strategy; complete rotor/motor integration and full travel; reconcile CAD mass and issue manufacturing drawings. Suppressed previous proposals are history, not intended BOM items.

A low-memory warning occurred during editing. The operation was declined; completed edits were saved and undo lists were cleared only for saved task documents. Pre-change CAD copies are retained at the path recorded in validation data. This removes session undo history for those saved task documents; recovery uses the saved files and backups.

## Sources

- [Savox SH-0257MG+ specification](https://www.teamsavox.com/product/sh-0257mgp/): current family nominal21T output identity; not delivered-part inspection.
- [Official Savox SH-0257MG+ 3D archive](https://web.teamsavox.com/wp-content/uploads/2025/05/SH-0257MGP_3D.zip): inspected STEP output has21 teeth and5.0mm crown diameter; retained locally with source/hash records.
- [Loctite222 manufacturer technical data](https://dm.henkel-dam.com/is/content/henkel/tds-471660-au-loctite-222-threadlocker-carded-10ml): provisional small steel pivot-thread retention; no applied/cured hardware is claimed.
- [Savox SH11M](https://www.savoxusa.com/products/savsh11m-sh11m-micro-servo-horn-set): retaining screw2x3mm. It does not establish this custom horn's fit or radius.
- [HIWIN miniature-guide catalogue](https://www.hiwin.com/wp-content/uploads/Linear_Guideway-E-2.pdf): MGN5C pattern, M2x1.5 block holes and rail geometry.
- [SMB miniature-bearing catalogue](https://www.smbbearings.com/products/miniature-bearings.html):686ZZ6x13x5 versus open6866x13x3.5.
- [Rotor Clip retaining-ring catalogue](https://www.rotorclip.com/wp-content/uploads/2023/03/spanish_catalog.pdf): DSH6 grooveD5.7,width0.8, ring thickness0.7.
- [M1.6 washer dimensions](https://shop.schaefer-peters.com/sp/ro/din-125-a2-1-7-p493474/):1.7x4x0.3.
- [M2.5x8 cap screw](https://shop.schaefer-peters.com/sp/ro/iso-4762-a2-m-2-5x8-p512859/):head4.5x2.5.
- [M3x55 cap screw](https://shop.schaefer-peters.com/sp/en/iso-4762-a2-m-3x55-p301593/):head5.5x3, threaded length18.
- [M3 nut](https://shop.schaefer-peters.com/sp/ro/din-934-a2-m-3-p500632/):AF5.5,H2.4.
- [Previously selected M2 and M2.5 hardware](../Servo_Mounting_Prototype/MOUNTING_NOTES.md), [stop hardware sources](../Travel_Stop_Prototype/MOUNTING_NOTES.md).

Exact materials and grades are not inferred from dimensional catalogue references. Custom low-head screws and the derived horn require independent manufacturing definitions.
