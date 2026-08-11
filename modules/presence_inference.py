"""Topology-first room inference using synthetic, provider-neutral evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Mapping, Sequence


@dataclass(frozen=True)
class ZoneEvent:
    zone: str
    observed_at: datetime


@dataclass(frozen=True)
class InferenceResult:
    location: str
    confidence: str
    evidence: tuple[str, ...]
    observed_at: datetime
    stale: bool = False


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _fresh(events: Sequence[ZoneEvent], now: datetime, ttl: timedelta) -> list[ZoneEvent]:
    normalized_now = _as_utc(now)
    return sorted(
        (
            ZoneEvent(event.zone, _as_utc(event.observed_at))
            for event in events
            if timedelta(0) <= normalized_now - _as_utc(event.observed_at) <= ttl
        ),
        key=lambda event: event.observed_at,
    )


def _validated_path(
    events: Sequence[ZoneEvent], adjacency: Mapping[str, set[str]]
) -> tuple[list[ZoneEvent], int]:
    if not events:
        return [], 0
    accepted = [events[0]]
    rejected = 0
    for event in events[1:]:
        previous = accepted[-1].zone
        if event.zone == previous or event.zone in adjacency.get(previous, set()):
            accepted.append(event)
        else:
            rejected += 1
    return accepted, rejected


def infer_location(
    *,
    events: Sequence[ZoneEvent],
    adjacency: Mapping[str, set[str]],
    now: datetime,
    event_ttl: timedelta,
    branch_entry: str | None = None,
    phone_rssi: float | None = None,
    phone_rssi_samples: Sequence[float] | None = None,
    minimum_signal_samples: int = 2,
    room_fingerprints: Mapping[str, tuple[float, float]] | None = None,
    overlap_default: str | None = None,
    previous: InferenceResult | None = None,
) -> InferenceResult:
    """Infer a location without allowing phone signal to create a topology jump."""

    now = _as_utc(now)
    fresh, rejected = _validated_path(_fresh(events, now, event_ttl), adjacency)
    if not fresh:
        if previous is None:
            return InferenceResult("unknown", "low", ("no-fresh-evidence",), now, True)
        return InferenceResult(
            previous.location,
            "low",
            ("previous-location", "evidence-expired"),
            previous.observed_at,
            True,
        )

    latest = fresh[-1]
    evidence = ["ordered-zone-event"]
    if rejected:
        evidence.append("ignored-impossible-jump")

    if latest.zone != branch_entry:
        return InferenceResult(latest.zone, "high", tuple(evidence), latest.observed_at)

    samples = list(phone_rssi_samples or ())
    if not samples and phone_rssi is not None:
        samples = [phone_rssi]
    if not samples or not room_fingerprints:
        return InferenceResult(latest.zone, "low", tuple(evidence + ["branch-unresolved"]), latest.observed_at)

    required = max(1, minimum_signal_samples)
    if len(samples) < required:
        return InferenceResult(
            latest.zone,
            "low",
            tuple(evidence + ["phone-signal-insufficient-samples"]),
            latest.observed_at,
        )
    stable_samples = samples[-required:]

    candidates = [
        room
        for room, (lower, upper) in room_fingerprints.items()
        if all(lower <= value <= upper for value in stable_samples)
    ]
    if len(candidates) == 1:
        return InferenceResult(
            candidates[0],
            "medium",
            tuple(evidence + ["phone-signal-consecutive-within-confirmed-branch"]),
            latest.observed_at,
        )
    if candidates and overlap_default in candidates:
        return InferenceResult(
            overlap_default,
            "low",
            tuple(evidence + ["phone-signal-overlap", "user-prior-fallback"]),
            latest.observed_at,
        )
    return InferenceResult(
        latest.zone,
        "low",
        tuple(evidence + ["phone-signal-no-unique-match"]),
        latest.observed_at,
    )
