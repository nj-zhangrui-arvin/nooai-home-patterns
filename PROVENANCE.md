# Provenance

This public candidate was rewritten from operational experience into provider-neutral examples, pure policy modules, and workflow Skills. It contains no production Home Assistant configuration or private Git history.

| Upstream | Reviewed ref (2026-08-11) | License | Reuse type | Scope in this project |
| --- | --- | --- | --- | --- |
| [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) | `2ed064090711` | MIT | methodology reference | Focused phase-output rules in `codex-phase-release`; no upstream text copied wholesale. |
| [obra/superpowers](https://github.com/obra/superpowers) | `44c9b2d6e889` | MIT | workflow reference | Requirement review before quality review and verification-before-completion boundaries. |
| [ExperienceLovelace/ha-floorplan](https://github.com/ExperienceLovelace/ha-floorplan) | `56b969418215` | Apache-2.0 | architecture reference | SVG delivery and Home Assistant mapping boundary; no code copied. |
| [Hollako/Home-Assistant-3D-Floorplan](https://github.com/Hollako/Home-Assistant-3D-Floorplan) | `ec73c9b179bd` | ISC | architecture reference | 3D floorplan delivery boundary; no assets or code copied. |
| [agittins/bermuda](https://github.com/agittins/bermuda) | `cd46d17e8469` | MIT | provider-boundary reference | BLE evidence adapter boundary; no code copied. |
| [ESPresense/ESPresense](https://github.com/ESPresense/ESPresense) | `b1fcfd53dbf9` | AGPL-3.0 | architecture reference only | Room-evidence interface concepts; no AGPL code, configuration, or protocol implementation included. |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | `b58d3f102cf3` | MIT | external tool and workflow reference | Optional secret scanner and staged/history gate design; no code copied. |
| [TruffleHog](https://github.com/trufflesecurity/trufflehog) | `bf17c561468b` | AGPL-3.0 | external tool and workflow reference | Optional offline scanner; no AGPL code included. |
| [Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) | `5e141933554a` | Apache-2.0 | external tool and workflow reference | Optional offline scanner and entropy/baseline concepts; no code copied. |
| [pre-commit/pre-commit](https://github.com/pre-commit/pre-commit) | `9767b6c8211a` | MIT | external tool | Local hook orchestration. |
| [awslabs/git-secrets](https://github.com/awslabs/git-secrets) | `7d6b970cbd3c` | Apache-2.0 | workflow reference | Secret scanning coverage concepts; no code copied. |

The MIT license in this repository applies only to original files in this repository. Third-party tools remain under their own licenses. Architectural reference to AGPL projects does not copy or relicense their implementations.
Home Assistant, Blender, and other product names are trademarks of their respective owners.

## Copied files
- `open-source/docs/architecture.md` sha256 `191661bec7e1c39158e45134d774e25f3fae7a4562da7a064a8f8707031903f5`
- `open-source/docs/module-catalog.md` sha256 `a1c51c5fcacb0b26470a0301671034b2840ebf73c5b4413daf7988e44ecb3e4d`
- `open-source/docs/privacy.md` sha256 `28b36937aaa63e127b2d376ae5d5429e2ddc47f8b1995e10237965ea9e6dc889`
- `open-source/docs/release-checklist.md` sha256 `b1a12b688ed13b10a396b731400455bc4e7368c1a579dc42183c1b8d37b7893a`
- `open-source/examples/compose/home-assistant-compose.example.yml` sha256 `be8c93ed44817c0b77e4855a883a0d26926ef3ef9621f47d5bb6c96688da7e5c`
- `open-source/examples/floorplan/manifest.example.json` sha256 `b7961c1b5c026b7c755e6ad40d8a57521d0fc23b95cadbef5370cd568dea2874`
- `open-source/examples/home-assistant/configuration.example.yaml` sha256 `1643520a5b89740d1ca4b39e0dd99ce18f679b197e4c253b1d9e5bf15900242f`
- `open-source/modules/README.md` sha256 `3f6adfa203a8b2514c7dab6c2a1a2cee5f7226404e00387f91b22f3d5b1d2ff4`
- `open-source/modules/__init__.py` sha256 `f3c403b558441909d96e0efecc3611567208dbb88f4b2572392591e3d07b7ae7`
- `open-source/modules/commute_alert.py` sha256 `d483ed1fff170b3e47fcdbc5a5cb84c5bc90d19828ed53dfdf71d9b260db5747`
- `open-source/modules/floorplan_manifest.py` sha256 `3bcc0b1640b37337a8e6f32da3110ad4f71524cc6c011f62b7dd4580eb70a706`
- `open-source/modules/presence_inference.py` sha256 `8ba23f00bcaa6b821cfc741c448d45d5c1487db07315c3ead6ae1ddaa0586c30`
- `open-source/modules/reliable_device_command.py` sha256 `2a08840d80236b4554c8e1e06950c8e2ad3337109b61376c9598578c19ef61d9`
- `open-source/skills/codex-phase-release/SKILL.md` sha256 `f7d46a19c1fbd8e9990106d1457e66a4f8b48d8ea96c5883404d41fea674b8a5`
- `open-source/skills/codex-phase-release/agents/openai.yaml` sha256 `1e5986d9e2d9f66d846efb98c0702ce257cb0a345d9f532321164b2b3dbfffd1`
- `open-source/skills/codex-phase-release/references/evidence-matrix.md` sha256 `b511f7d21b1bce658efdb1eb4745201b101648063ced5e213b8a8135d25d1f22`
- `open-source/skills/codex-phase-release/references/prior-art.md` sha256 `10de9b6c4df159c1ed74a007e9361545f1c037159d9e28c851f98af25699c643`
- `open-source/skills/ha-floorplan-3d-public/SKILL.md` sha256 `10a5c6578e02627d9359e2b8cc6c50cd26a92ce8c7e8cb688f1b1320c7475586`
- `open-source/skills/ha-floorplan-3d-public/agents/openai.yaml` sha256 `043d44470fcc3fe22b8cf61c6e10176ae767be21ef5ad55ab870fe8847b8f415`
- `open-source/skills/ha-floorplan-3d-public/references/prior-art.md` sha256 `33aed6dacb17b765231538460438dec94809630cb3666fb57602e67ba8970eff`
- `open-source/skills/ha-floorplan-3d-public/references/quality-gates.md` sha256 `d9a6052f41f1f3716b70b99598657089958ea05d8be4e4fa26cd7a463a1a7618`
- `open-source/skills/ha-presence-inference/SKILL.md` sha256 `f1539b273a1e2f55323d9b2f8c7c536e1ebeb08ce59a679d79addd4a3084f6bc`
- `open-source/skills/ha-presence-inference/agents/openai.yaml` sha256 `179e7ad7f170166d783316b2b6823a444067574a56a6a6cd2a5761fa5ae4037b`
- `open-source/skills/ha-presence-inference/references/evidence-contract.md` sha256 `eee311b11aefe9c18fc575b45e615d928479379642505d2a4c128fc8298f0afb`
- `open-source/skills/ha-presence-inference/references/prior-art.md` sha256 `1376552a46a7ace3f8887da546b606602a18f262f6965be742b97cf9aab5159b`
- `open-source/skills/public-release-audit/SKILL.md` sha256 `f0eeca41ab2dc469142e3c68e9fd745a38e8d7ab3633b341b6a7baba2172ad38`
- `open-source/skills/public-release-audit/agents/openai.yaml` sha256 `2df3f065945973f65315dc6e05a7faa3c158413e1f3c151bf9d70c135eb059cc`
- `open-source/skills/public-release-audit/references/gate-matrix.md` sha256 `ad1487e2bd3d3edf0125cfc0aa23b83ead62ab1e4ee08e3d33fa534bd66e6703`
- `open-source/skills/public-release-audit/references/prior-art.md` sha256 `f2df8c4942167ec68c765ebb1ed27910c9897bfaeac5249f78b450efd1fdc49e`
- `open-source/skills/public-release-audit/scripts/audit_public_release.py` sha256 `cf2ffccc2f442ea956c17642caa976ae42630c21845cced52ba51dc4d9e0529f`
- `open-source/skills/public-release-audit/scripts/check_optional_scanners.py` sha256 `3e0c92039b0eceb47fe26300a030b263802b795611de883bfcca19a41247dff1`
- `open-source/tests/test_modules.py` sha256 `f407c4feca0d854eef421ea2a8f0281eb545deac19a83509d4b4d20bc2e37838`
- `open-source/tests/test_public_export.py` sha256 `bb0170dff249a5e3283c44d3430c66953566167fdadeb76ebdefb0dbc82eab93`
- `open-source/tests/test_public_release_audit.py` sha256 `22d96abf869e75b0916db1128133ad05e3f4be546e999caab35edbe8e8f46317`
- `open-source/tools/check_public_export.py` sha256 `e9639b04de18876fc21823ae9dd6af94e8242435b6042ece317d469359279e46`

## Generated files
- `PROVENANCE.md` generated from `open-source/PROVENANCE.md` and per-file digests at build time.
- `README.md` sha256 `b630dd8cf4ef6730eba82475328a690aa0fe81adcf7e9cde823b00a9471297f0` sources template-only
- `LICENSE` sha256 `a051f09943f9908709b881a77ddcd13085e2e6be6d07a39e6f84c54fc637224d` sources template-only
- `SECURITY.md` sha256 `7a49c09139fd6068d2523e2a22f041151d42f1ed66ce1a32f55a5c9f3eac9564` sources template-only
- `CONTRIBUTING.md` sha256 `ac6be3dfdc06124848ce195ffd6a72bd4f98c7cca7aabcea8b08865268582b87` sources template-only
- `THIRD_PARTY_NOTICES.md` sha256 `7f75f5640266e638d25b8139e1226278287461cade81235f0cf5586b075647d5` sources `open-source/PROVENANCE.md`
- `.github/workflows/ci.yml` sha256 `866c6ffff932915fb8c5a687edce1a668c2d9d06c2f30ab50ce7580b4da96f16` sources template-only
- `.gitignore` sha256 `47fd8e76c097d23b7c27335af6ee225e19f451e55e7a288b37edd5d17c6b43d6` sources `open-source/.gitignore`
- `.pre-commit-config.yaml` sha256 `1c245ecf03390010dc2f447d7ae175544d987853cad767174bcbc142e07e02ae` sources `open-source/.pre-commit-config.yaml`
- `assets/README.md` sha256 `9f73a368272139c4be63321d93c246157ce8c0969378a495ada743fe9818c545` sources template-only
- `media-manifest.json` sha256 `d069aa09baf312753eeb74630fda038ec517f328a7239fd17a35380bb8d08b7d` sources template-only
