# Rotor integration: blade pattern release

21 October 2026. This step changes only Assem20 assembly structure/mates and inserts one existing pushrod. Part geometry and calculation inputs are unchanged.

The user identifies Part1.SLDPRT as the intended NACA0012 blade. Native inspection confirms220mm aerodynamic span,38mm approximate chord envelope, andD3 end journals on the axis9.5mm from the leading-edge origin. This step does not independently certify the airfoil coordinates.

Both LocalCirPattern1 (blades) and LocalCirPattern2 (arms) have been dissolved. The seed blade retains Concentric4 (rotation unlocked) and centred Width1. The three former blade copies each receive an unlocked concentric mate to the corresponding endplate hole and a centred width mate between the endplates. Thus no pattern ties their pitch angles together.

The user's seed pitch-arm connection remains: arm1 to blade3, with Concentric5 and the two existing coincident flat/axial mates. The other arms retain their current positions and use rigid relative attachments: arm2 to blade4, arm3 to blade1, arm4 to blade2. These rigid attachments represent the intended arm-to-blade connection; they do not establish physical clamp strength or retention.

One5-Pushrod_Linkage-1 component is inserted nearby and deliberately unmated. Pushrod mating and hardware design are the next step. No complete rotor-motion claim is made.

See PATTERN_RELEASE_VALIDATION.json for affected-mate checks, pose preservation, source hashes and the pre-change backup. Earlier connection validation remains tied to its earlier assembly hash.

Outstanding physical interfaces: blade span and endplate inner-face separation are both220mm, so there is no nominal axial running allowance; theD3 journals require bushings in theD6 endplate holes; blade axial retention and actual pitch-arm fastening still need definition. This step neither changes those dimensions nor establishes fabrication readiness.

Subsequent step: one separate-ball articulated linkage is now fitted between arm4/blade2 and the control ring. See [ball-link prototype notes](Ball_Link_Prototype/README.md) and [current focused evidence](Ball_Link_Prototype/BALL_LINK_VALIDATION.json). The earlier pattern-release report remains evidence for its earlier assembly hash. The other three articulated linkages, known frame-clearance conflict and physical socket-retention details remain unresolved.

Latest revision: all four stations now use planar offset-arm articulated links in Assem20. See [four-link notes](Ball_Link_Prototype/FOUR_LINKS_NOTES.md) and [four-link check results](Ball_Link_Prototype/FOUR_LINKS_VALIDATION.json). Those records supersede the single-link scope above and describe the revised frame/support clearance. Full rotor motion, physical ring timing, strength and socket retention remain unresolved.
