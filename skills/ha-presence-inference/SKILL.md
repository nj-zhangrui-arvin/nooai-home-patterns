---
name: ha-presence-inference
description: "Design and validate topology-first Home Assistant room presence inference. Use when combining zone sensors, ordered paths, Wi-Fi or Bluetooth signal, TTL, confidence, and user priors while preventing impossible room jumps and protecting location privacy."
---

# HA Presence Inference

Treat room location as an evidence graph, not a signal-strength lookup table.

## Workflow

1. Draw the zone adjacency graph and mark sensor blind spots.
2. Classify each input as direct observation, path evidence, weak signal, prior, or unavailable.
3. Normalize timestamps and define TTL, debounce, cluster, and restart behavior.
4. Accept direct zone events before signal evidence.
5. Use phone signal only inside an already confirmed branch.
6. Reject impossible non-adjacent jumps and record the rejected evidence.
7. Return location, confidence, evidence, observed time, and stale state separately.
8. Calibrate each receiver independently and require a handoff margin or consecutive samples before changing between signal-derived candidates.
9. Test forward/reverse paths, short pulses, missing data, signal overlap, restart, stale evidence, and rotating device identifiers.

## Provider adapters

- Convert radar/PIR/zone events into direct or path evidence.
- Convert BLE providers into area and distance observations; keep receiver calibration, attenuation, and maximum radius in provider configuration.
- Convert MQTT room providers into timestamped room candidates, never directly into a final person location.
- Keep anonymous occupancy separate from identity-bearing device presence.
- Treat USB or non-timestamped observations as lower-quality evidence.

## Safety rules

- Do not treat phone offline as proof that a person left home.
- Do not treat sensor `off` as absence outside that sensor's coverage.
- Do not add uncertainty words to the room name; use confidence.
- Do not persist personal trajectories unless the user explicitly requests it.
- Do not expose raw MAC addresses, IRKs, beacon UUIDs, or receiver dumps in logs or public fixtures; use pseudonymous IDs.
- Do not call device services during location tests.

Use the provider-neutral contract in `references/evidence-contract.md`. A minimal pure-Python example is available in `modules/presence_inference.py`.
Read `references/prior-art.md` before adding BLE or MQTT hardware adapters.
