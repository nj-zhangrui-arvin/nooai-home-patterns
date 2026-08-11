---
name: ha-floorplan-3d-public
description: "Build, revise, render, validate, and export privacy-safe 3D floorplan assets for Home Assistant. Use for synthetic or licensed CAD-to-Blender work, floorplan overlays, coordinate registration, staged dashboard assets, or reproducible GLB/image export without exposing a real home."
---

# HA Floorplan 3D Public

Build reproducible floorplan assets from synthetic or explicitly licensed inputs.

## Input gate

1. Confirm the input does not reveal a real residence, address, exterior view, device identifier, or person location.
2. Record source, license, units, orientation, crop, and intended output.
3. Back up every model and generator before writes; verify the backup checksum.
4. Work on a staged copy, never the accepted source model.

## Build loop

1. Choose the least expensive delivery mode that meets the interaction need: static image, SVG object map, or GLB scene.
2. Generate geometry from a script or documented import process.
3. Preserve metric units, axis orientation, object origins, and stable semantic object names.
4. Register camera, crop, anchors, lights, interactions, and animations in one manifest.
5. Render fixed top and perspective baselines.
6. Change one geometric or visual concern at a time.
7. Compare the same cameras and reject regressions.
8. Export only after geometry, manifest, visual, performance, offline-loading, and privacy gates pass.

## Home Assistant boundary

- Keep model generation independent from entity IDs.
- Map example entities to SVG IDs or named GLB objects in a separate adapter.
- Bind animation to explicit entity states and stop it when the state is inactive or the layer is hidden.
- Prefer locally bundled frontend dependencies; document any remote fallback.
- Deploy assets to staged UI first.
- Do not call real device services during asset validation.
- Keep hidden layers and unchanged state from repainting continuously.

Read `references/quality-gates.md` before accepting an asset set.
Read `references/prior-art.md` before selecting SVG or GLB delivery.
