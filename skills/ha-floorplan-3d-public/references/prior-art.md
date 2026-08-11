# Prior art and delivery choices

Select a rendering path from the required interaction, not from visual novelty.

| Need | Preferred public pattern |
| --- | --- |
| Fast overview with state styling | Static image plus lightweight overlay |
| Clickable named regions and simple state styles | SVG object mapping, as demonstrated by [ha-floorplan](https://github.com/ExperienceLovelace/ha-floorplan) |
| Camera movement, named mesh interaction, or model animation | Browser-optimized GLB with an explicit object manifest, as demonstrated by [Home-Assistant-3D-Floorplan](https://github.com/Hollako/Home-Assistant-3D-Floorplan) |

Absorbed boundaries:

- Record the axis convention and default camera in the manifest.
- Name interactive and animated objects deterministically; validate exact case and object origin before export.
- Keep state styling, tap/hold actions, and entity mapping outside the model generator.
- Prefer a single browser-oriented GLB and simple polygons; measure mobile load and steady-state rendering cost.
- Bundle runtime dependencies locally when offline or Companion App use matters.
- Continuous animation must be state-driven and must stop when inactive or hidden.

No upstream card code or example entity configuration is included in this Skill.
