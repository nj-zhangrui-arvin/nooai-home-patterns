"""A small state machine for commands whose physical result is not always readable."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


class CommandState(str, Enum):
    IDLE = "idle"
    REQUESTED = "requested"
    BLOCKED = "blocked"
    SENT_UNCONFIRMED = "sent_unconfirmed"
    CONFIRMED = "confirmed"
    FAILED = "failed"


@dataclass(frozen=True)
class CommandIntent:
    key: str
    created_at: datetime
    ttl: timedelta


@dataclass(frozen=True)
class CommandResult:
    state: CommandState
    reason: str


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def evaluate_command(
    *,
    intent: CommandIntent,
    now: datetime,
    channel_available: bool,
    safety_ok: bool,
    already_consumed: bool = False,
    sent: bool = False,
    acknowledged: bool = False,
    failed: bool = False,
) -> CommandResult:
    """Evaluate one idempotent command without claiming unobserved physical success."""

    if not intent.key.strip():
        return CommandResult(CommandState.BLOCKED, "idempotency-key-missing")
    if intent.ttl <= timedelta(0):
        return CommandResult(CommandState.BLOCKED, "intent-ttl-invalid")
    if already_consumed:
        return CommandResult(CommandState.IDLE, "idempotency-key-consumed")

    normalized_now = _as_utc(now)
    created_at = _as_utc(intent.created_at)
    age = normalized_now - created_at
    if age < timedelta(0):
        return CommandResult(CommandState.BLOCKED, "intent-from-future")
    if age > intent.ttl:
        return CommandResult(CommandState.BLOCKED, "intent-expired")
    if not channel_available:
        return CommandResult(CommandState.BLOCKED, "channel-unavailable")
    if not safety_ok:
        return CommandResult(CommandState.BLOCKED, "safety-gate")
    if failed:
        return CommandResult(CommandState.FAILED, "execution-failed")
    if acknowledged:
        return CommandResult(CommandState.CONFIRMED, "independent-ack")
    if sent:
        return CommandResult(CommandState.SENT_UNCONFIRMED, "awaiting-independent-ack")
    return CommandResult(CommandState.REQUESTED, "ready-to-send")
