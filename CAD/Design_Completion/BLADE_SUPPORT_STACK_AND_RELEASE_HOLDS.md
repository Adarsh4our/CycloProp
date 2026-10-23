# Blade support cartridge: implemented stack and release holds

This is a prototype design record, not a fabrication or operating release. Read the native integration and check JSON files for the actual implemented revision and checks.

The previous D3 journal in a D6 plate hole did not define a working bearing or retention. The specification's JFM-0306-04 identity was not reconciled with supplier geometry. The preliminary reaction/speed screen also warrants a rolling-bearing alternative. The revised candidate uses F693ZZ external bearing envelopes, 3×8×4 mm with a 9.5×0.9 mm flange, per the retained supplier drawing. Its catalogue ratings do not establish suitability for 44 Hz oscillatory pitch.

## Geometry and assembly

Eight cartridge subassemblies are installed, one at each blade end. Each machined housing has a D10 pilot through a D10.02 endplate hole, an inboard flange and an M10×0.5 outer retaining nut. The cartridge flange and nut capture the 1.5 mm G10 sheet. A separate M14×0.5 cap retains the bearing's outer flange against the housing shoulder. The cap's ID8.2 contact annulus clears the nominal OD8 bearing body. Actual supplier ring-face contact lands require confirmation.

Cartridge coordinates run inward from the endplate outside face:

| Feature | Nominal axial station, mm |
| --- | --- |
| Endplate | 0 to 1.5 |
| Housing inboard retaining flange | 1.5 to 1.8 |
| M10 retaining nut | −1 to 0 |
| Bearing external envelope | −2.5 to 1.5 |
| Bearing flange | −2.5 to −1.6 |
| Bearing cap | −3 to −1.3 |
| Inner-race spacer, OD4 / ID3.05 | 1.5 to 1.8 |
| PTFE thrust film, OD4 / ID3.05 | 1.8 to 1.95 |
| Blade shoulder, centred position | 2.15 |

The two 0.65 mm hub/endplate shims increase the plate inner-face separation from 220 to 221.3 mm. The blade aerodynamic span remains 220 mm. Each end has 0.45 mm of spacer/film inward of the plate, leaving 0.2 mm nominal clearance at each blade shoulder, or 0.4 mm total endfloat. The width mates represent the centred construction position; they do not simulate physical endfloat.

Both endplates moved symmetrically. The shaft, blade, hub and pitch-arm stations were preserved by native transform checks. The remaining hub pilot engagement is 0.85 mm. M2.5×10 screw references replace the earlier M2.5×8 references; nominal protrusion beyond the nuts is 1.85 mm. The upper main-bearing cap's screws were changed to M2×4 button-head envelopes seated directly on the cap to resolve a detected clash. The correction and its recheck are recorded separately.

Both proposed bearing spans were intersected with the native blade journal solid: the full D3 round journal volumes were present, clear of the D-flat. This verifies nominal geometry only. It does not identify the journal's actual material, hardness, surface finish, tolerance or connection to a composite blade.

Assemble the cartridges into the plates before closing the two-plate rotor around the blades. The flange enters from the blade side; the nut and bearing cap are accessible from outside. Insert the blade journals while assembling the endplates, then install the hub fasteners and pitch arms. The opposing blade shoulders provide axial capture through the inner-ring spacer/film stacks. Do not clamp the blade shoulders between the plates or tighten a bearing cap against an inner ring.

## Fits and inspections still required

- Release the steel journal/bearing-bore fit using the supplier's delivered bore tolerance and actual rotating-load condition. Nominal D3/D3 is not a fit specification.
- Release the cartridge D8 bearing seat and D10/D10.02 plate pilot tolerances, concentricity and coaxiality. A nominal 0.02 mm clearance is not a controlled assembled runout.
- Confirm the bearing shoulder and inner-ring spacer contact only their intended rings. The solid annular bearing model does not resolve shields, race lands or internal axial play.
- Release M10×0.5 and M14×0.5 thread classes, full usable engagement, runouts, lead-ins, torque and anti-loosening. CAD shows major envelopes, not helical threads or manufacturing tap sizes.
- Determine allowable G10 clamp pressure, edge strength and fatigue from the supplied sheet/laminate. The enlarged D10.02 holes leave 2.99 mm nominal material to the OD206 edge; the nearby cutouts and net sections also require assessment. No G10 strength approval is implied.
- Measure actual blade span, hub stations, plate thickness, cartridge lands, bearing ring offsets, spacers and film. Set and inspect endfloat on the assembled rotor using selected shims. A provisional inspection window of 0.15–0.45 mm total is proposed; it requires engineering approval and thermal/loaded justification. Do not substitute this proposal for an approved tolerance stack.
- Establish oscillatory bearing life, grease condition, fretting/false-brinelling risk, misalignment limits and proof-load requirements with the supplier and test programme.
- The bearing's steel annulus is an external envelope with a steel density proxy. It is not a bearing manufacturing model or reliable purchased bearing mass.

## Evidence

- BLADE_CARTRIDGE_INTEGRATION_STATE.json: installed component mapping, backups, changed mates and preserved transforms.
- BLADE_JOURNAL_GEOMETRY_CHECK.json: round journal volume checks.
- BLADE_SUPPORT_STATIC_CHECK.json: measured axial gaps and scoped native solid intersections. Read the result; installation alone is not a pass.
- UPPER_CAP_HEAD_CORRECTION.json: hardware correction following the first static failure.
- Manufacturer_References/F693ZZ_supplier.pdf: supplier external dimensions and catalogue data.
- BLADE_SUPPORT_SELECTION_SCREEN.json: assumed reaction/speed comparison and exclusions.
