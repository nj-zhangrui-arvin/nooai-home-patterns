"""Validate a privacy-safe, provider-neutral floorplan asset manifest."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class ManifestResult:
    valid: bool
    errors: tuple[str, ...]


def validate_manifest(payload: Mapping[str, Any]) -> ManifestResult:
    """Validate the public contract without opening or rendering private assets."""

    errors: list[str] = []
    if payload.get("version") != 1:
        errors.append("unsupported-version")
    if payload.get("units") != "meters":
        errors.append("units-must-be-meters")
    source = payload.get("source")
    if not isinstance(source, Mapping):
        errors.append("source-missing")
    else:
        if source.get("kind") not in {"synthetic", "licensed"}:
            errors.append("source-kind-not-public")
        if not str(source.get("license", "")).strip():
            errors.append("source-license-missing")
    cameras = payload.get("cameras")
    if not isinstance(cameras, list) or not cameras:
        errors.append("camera-baseline-missing")
    else:
        names = [str(item.get("name", "")) for item in cameras if isinstance(item, Mapping)]
        if len(names) != len(cameras) or any(not name for name in names):
            errors.append("camera-name-missing")
        elif len(set(names)) != len(names):
            errors.append("camera-name-duplicate")
    objects = payload.get("objects")
    if not isinstance(objects, list) or not objects:
        errors.append("semantic-objects-missing")
    else:
        object_names = [str(item.get("name", "")) for item in objects if isinstance(item, Mapping)]
        if len(object_names) != len(objects) or any(not name for name in object_names):
            errors.append("semantic-object-name-missing")
        elif len(set(object_names)) != len(object_names):
            errors.append("semantic-object-name-duplicate")
        if any("entity_id" in item for item in objects if isinstance(item, Mapping)):
            errors.append("entity-binding-must-be-separate")
    return ManifestResult(not errors, tuple(errors))
