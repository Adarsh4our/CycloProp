# CycloProp provisional density database

Use CycloProp_Prototype_Densities.sldmat. DATABASE_INSTALLATION.json records its retained source, installed copy and SHA256. It supplies G10 density1850kg/m3 and tube CFRP density1550kg/m3 for provisional CAD mass only. Elastic, yield, laminate and fatigue properties are deliberately absent.

This computer uses the copied database in the existing SolidWorks2026 custom-materials folder; no preferences or existing databases were modified. On another computer, copy this file to a configured Material Databases folder, or configure the project Materials folder, then verify native material/density readback. Merely naming the material does not verify density.

Unregistered_Draft preserves the earlier minimal database attempt. That attempt did not read back through the native API; it is not the assigned production source. Do not use it as completed material evidence.
