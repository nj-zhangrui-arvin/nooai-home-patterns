from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

PUBLIC_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PUBLIC_ROOT))

from modules.commute_alert import CommuteSample, evaluate_commute
from modules.presence_inference import InferenceResult, ZoneEvent, infer_location
from modules.reliable_device_command import CommandIntent, CommandState, evaluate_command
from modules.floorplan_manifest import validate_manifest


class FloorplanManifestTests(unittest.TestCase):
    def test_synthetic_manifest_is_valid(self) -> None:
        result = validate_manifest(
            {
                "version": 1,
                "units": "meters",
                "source": {"kind": "synthetic", "license": "MIT"},
                "cameras": [{"name": "top"}, {"name": "isometric"}],
                "objects": [{"name": "room_alpha"}, {"name": "light_alpha"}],
            }
        )
        self.assertTrue(result.valid)

    def test_entity_binding_is_rejected_from_asset_manifest(self) -> None:
        result = validate_manifest(
            {
                "version": 1,
                "units": "meters",
                "source": {"kind": "synthetic", "license": "MIT"},
                "cameras": [{"name": "top"}],
                "objects": [{"name": "light_alpha", "entity_id": "light.example"}],
            }
        )
        self.assertIn("entity-binding-must-be-separate", result.errors)


class PresenceInferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2030, 1, 1, 8, 0, tzinfo=timezone.utc)
        self.adjacency = {
            "living": {"branch_entry", "dining"},
            "dining": {"living", "entry"},
            "entry": {"dining"},
            "branch_entry": {"living"},
        }

    def test_phone_signal_only_classifies_after_branch_entry(self) -> None:
        result = infer_location(
            events=[ZoneEvent("branch_entry", self.now)],
            adjacency=self.adjacency,
            now=self.now,
            event_ttl=timedelta(seconds=30),
            branch_entry="branch_entry",
            phone_rssi_samples=[-77, -76],
            room_fingerprints={"room_a": (-80, -72), "room_b": (-60, -50)},
        )
        self.assertEqual(result.location, "room_a")
        self.assertEqual(result.confidence, "medium")

    def test_phone_signal_cannot_jump_from_entry_to_room(self) -> None:
        result = infer_location(
            events=[ZoneEvent("entry", self.now)],
            adjacency=self.adjacency,
            now=self.now,
            event_ttl=timedelta(seconds=30),
            branch_entry="branch_entry",
            phone_rssi_samples=[-56, -55],
            room_fingerprints={"room_b": (-60, -50)},
        )
        self.assertEqual(result.location, "entry")
        self.assertEqual(result.confidence, "high")

    def test_overlap_uses_explicit_prior_with_low_confidence(self) -> None:
        result = infer_location(
            events=[ZoneEvent("branch_entry", self.now)],
            adjacency=self.adjacency,
            now=self.now,
            event_ttl=timedelta(seconds=30),
            branch_entry="branch_entry",
            phone_rssi_samples=[-55, -54],
            room_fingerprints={"room_a": (-60, -50), "room_b": (-58, -52)},
            overlap_default="room_a",
        )
        self.assertEqual((result.location, result.confidence), ("room_a", "low"))
        self.assertIn("user-prior-fallback", result.evidence)

    def test_expired_evidence_keeps_previous_but_marks_stale(self) -> None:
        previous = InferenceResult("living", "high", ("sensor",), self.now - timedelta(minutes=2))
        result = infer_location(
            events=[], adjacency=self.adjacency, now=self.now, event_ttl=timedelta(seconds=30), previous=previous
        )
        self.assertEqual(result.location, "living")
        self.assertTrue(result.stale)

    def test_naive_event_and_aware_now_are_normalized_to_utc(self) -> None:
        result = infer_location(
            events=[ZoneEvent("living", datetime(2030, 1, 1, 8, 0))],
            adjacency=self.adjacency,
            now=self.now,
            event_ttl=timedelta(seconds=30),
        )
        self.assertEqual(result.location, "living")
        self.assertEqual(result.observed_at.tzinfo, timezone.utc)

    def test_single_signal_sample_does_not_resolve_branch(self) -> None:
        result = infer_location(
            events=[ZoneEvent("branch_entry", self.now)],
            adjacency=self.adjacency,
            now=self.now,
            event_ttl=timedelta(seconds=30),
            branch_entry="branch_entry",
            phone_rssi=-76,
            room_fingerprints={"room_a": (-80, -72)},
        )
        self.assertEqual(result.location, "branch_entry")
        self.assertIn("phone-signal-insufficient-samples", result.evidence)


class ReliableCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2030, 1, 1, tzinfo=timezone.utc)
        self.intent = CommandIntent("cycle-1:raise", self.now, timedelta(minutes=2))

    def test_sent_without_ack_is_not_confirmed(self) -> None:
        result = evaluate_command(
            intent=self.intent, now=self.now, channel_available=True, safety_ok=True, sent=True
        )
        self.assertEqual(result.state, CommandState.SENT_UNCONFIRMED)

    def test_manual_or_automatic_duplicate_is_consumed_once(self) -> None:
        result = evaluate_command(
            intent=self.intent,
            now=self.now,
            channel_available=True,
            safety_ok=True,
            already_consumed=True,
        )
        self.assertEqual(result.state, CommandState.IDLE)

    def test_expired_intent_is_blocked(self) -> None:
        result = evaluate_command(
            intent=self.intent,
            now=self.now + timedelta(minutes=3),
            channel_available=True,
            safety_ok=True,
        )
        self.assertEqual(result.state, CommandState.BLOCKED)

    def test_naive_timestamps_are_normalized_to_utc(self) -> None:
        intent = CommandIntent("cycle-2:raise", datetime(2030, 1, 1, 8, 0), timedelta(minutes=2))
        result = evaluate_command(
            intent=intent,
            now=datetime(2030, 1, 1, 8, 1, tzinfo=timezone.utc),
            channel_available=True,
            safety_ok=True,
        )
        self.assertEqual(result.state, CommandState.REQUESTED)

    def test_future_intent_is_blocked(self) -> None:
        intent = CommandIntent("cycle-3:raise", self.now + timedelta(seconds=1), timedelta(minutes=2))
        result = evaluate_command(
            intent=intent,
            now=self.now,
            channel_available=True,
            safety_ok=True,
        )
        self.assertEqual(result.state, CommandState.BLOCKED)

    def test_missing_idempotency_key_is_blocked(self) -> None:
        result = evaluate_command(
            intent=CommandIntent(" ", self.now, timedelta(minutes=1)),
            now=self.now,
            channel_available=True,
            safety_ok=True,
        )
        self.assertEqual(result.reason, "idempotency-key-missing")

    def test_failed_signal_wins_over_acknowledgement(self) -> None:
        result = evaluate_command(
            intent=self.intent,
            now=self.now,
            channel_available=True,
            safety_ok=True,
            failed=True,
            acknowledged=True,
        )
        self.assertEqual(result.state, CommandState.FAILED)


class CommuteTests(unittest.TestCase):
    def test_stale_sample_requires_manual_review(self) -> None:
        now = datetime(2030, 1, 1, 8, 0, tzinfo=timezone.utc)
        decision = evaluate_commute(
            CommuteSample(now - timedelta(minutes=20), 25, "clear", "provider-a"),
            now=now,
            freshness_ttl=timedelta(minutes=5),
            warning_eta_minutes=30,
        )
        self.assertTrue(decision.manual_review)
        self.assertEqual(decision.status, "unknown")

    def test_fresh_congestion_warns(self) -> None:
        now = datetime(2030, 1, 1, 8, 0, tzinfo=timezone.utc)
        decision = evaluate_commute(
            CommuteSample(now, 24, "heavy", "provider-a"),
            now=now,
            freshness_ttl=timedelta(minutes=5),
            warning_eta_minutes=30,
        )
        self.assertEqual(decision.status, "warning")
        self.assertFalse(decision.manual_review)

    def test_naive_sample_and_aware_now_are_normalized_to_utc(self) -> None:
        now = datetime(2030, 1, 1, 8, 0, tzinfo=timezone.utc)
        decision = evaluate_commute(
            CommuteSample(datetime(2030, 1, 1, 8, 0), 18, "clear", "provider-a"),
            now=now,
            freshness_ttl=timedelta(minutes=5),
            warning_eta_minutes=30,
        )
        self.assertEqual(decision.status, "clear")

    def test_unknown_provider_congestion_requires_review(self) -> None:
        now = datetime(2030, 1, 1, 8, 0, tzinfo=timezone.utc)
        decision = evaluate_commute(
            CommuteSample(now, 18, "jam", "provider-a"),
            now=now,
            freshness_ttl=timedelta(minutes=5),
            warning_eta_minutes=30,
        )
        self.assertEqual(decision.status, "unknown")
        self.assertTrue(decision.manual_review)


if __name__ == "__main__":
    unittest.main()
