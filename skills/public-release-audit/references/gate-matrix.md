# Gate matrix

| Surface | Deterministic gate | Semantic review |
|---|---|---|
| Public tree | paths, suffixes, content patterns, symlinks, binary, size | names, topology, addresses, screenshots, licensing |
| Git index | staged blob content and mode | whether the staged concern belongs in public scope |
| Commit message | secret and identity patterns | unnecessary operational detail |
| Reachable history | every path, unique blob, commit/tag message, ref, remote and author metadata | whether any private history was inherited |
| Unreachable objects | fail if residue exists | create a fresh repository; do not waive blindly |
| Media | reject by default; exact path + SHA-256 manifest only | visible content, EXIF/GPS, copyright, source license |
| External tools | redacted local scan | investigate false positives without exposing values |

## Required finding classes

- credentials: API keys, tokens, cookies, JWTs, private keys, authenticated URLs;
- infrastructure: private IP ranges, private DNS, user paths, SSH material;
- smart-home privacy: entity IDs, device IDs, MAC/BLE identifiers, MQTT topics,
  household routes, room topology, coordinates, automation logs;
- repository residue: backups, databases, `.storage`, logs, caches, generated
  output, ignored runtime files, old Git objects, private author identity;
- legal/media: screenshots, CAD/3D source, fonts, icons, photos, audio/video,
  embedded metadata, incompatible licenses.

## Exception rules

Prefer removal or synthetic replacement. If an exception is unavoidable, bind
it to an exact path, exact rule, current file digest, source, license, reviewer,
reason, and expiry.
Never allow a broad directory, wildcard token pattern, or permanent exception.
Re-review an exception after any content change.

## Four-review merge

Use multiple reviewers only for independent semantic review. Give each reviewer
the public root and the gate contract, not another reviewer's conclusions.
Merge findings by severity and evidence. One credible P0/P1 privacy finding is
enough to block release even if other reviewers report no issue.
