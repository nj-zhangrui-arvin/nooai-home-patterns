# Evidence contract

```json
{
  "location": "zone-or-room",
  "confidence": "high|medium|low",
  "evidence": ["ordered-zone-event"],
  "observed_at": "RFC3339 timestamp",
  "stale": false
}
```

Direct sensor activity normally yields high confidence. Branch-gated signal classification normally yields medium confidence. Overlapping fingerprints resolved by an explicit prior yield low confidence and must identify the prior in `evidence`.
