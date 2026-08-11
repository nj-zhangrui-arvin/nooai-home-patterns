"""Freshness-aware, provider-neutral commute recommendation policy."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class CommuteSample:
    observed_at: datetime
    eta_minutes: int | None
    congestion: str | None
    provenance: str


@dataclass(frozen=True)
class CommuteDecision:
    status: str
    message: str
    manual_review: bool
    provenance: str


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def evaluate_commute(
    sample: CommuteSample,
    *,
    now: datetime,
    freshness_ttl: timedelta,
    warning_eta_minutes: int,
) -> CommuteDecision:
    if freshness_ttl <= timedelta(0) or warning_eta_minutes <= 0:
        return CommuteDecision("unknown", "policy configuration is invalid", True, sample.provenance)
    if not sample.provenance.strip():
        return CommuteDecision("unknown", "provenance is missing", True, sample.provenance)
    age = _as_utc(now) - _as_utc(sample.observed_at)
    if age < timedelta(0) or age > freshness_ttl:
        return CommuteDecision("unknown", "data is stale", True, sample.provenance)
    if sample.eta_minutes is None or sample.eta_minutes < 0 or sample.congestion is None:
        return CommuteDecision("unknown", "provider result is incomplete", True, sample.provenance)
    congestion = sample.congestion.strip().lower()
    if congestion not in {"clear", "light", "moderate", "heavy", "blocked"}:
        return CommuteDecision("unknown", "provider result is unsupported", True, sample.provenance)
    if sample.eta_minutes >= warning_eta_minutes or congestion in {"heavy", "blocked"}:
        return CommuteDecision("warning", "allow extra travel time", False, sample.provenance)
    return CommuteDecision("clear", "normal travel window", False, sample.provenance)
