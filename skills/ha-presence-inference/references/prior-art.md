# Prior art and adapter boundary

This inference layer complements, rather than replaces, sensor integrations.

- [Bermuda](https://github.com/agittins/bermuda) provides Home Assistant Area and Distance observations from Bluetooth proxies, supports configurable reference RSSI, environmental attenuation and tracking radius, and handles privacy-preserving BLE identities.
- [ESPresense](https://github.com/ESPresense/ESPresense) provides ESP32 room observations over MQTT for Home Assistant indoor positioning.

Absorbed design boundary:

1. Provider integrations own packet collection, identity resolution, receiver calibration, and distance estimation.
2. This Skill normalizes their outputs into timestamped evidence and combines them with physical topology and room sensors.
3. A provider's area result remains one observation; it cannot bypass adjacency, freshness, blind-spot, or confidence rules.
4. Identity-bearing presence and anonymous occupancy remain separate evidence classes.
5. Raw receiver dumps and stable device identifiers remain private diagnostic data.

No Bermuda or ESPresense code is copied into this package. In particular, ESPresense's AGPL-licensed implementation is only referenced as architectural prior art.
