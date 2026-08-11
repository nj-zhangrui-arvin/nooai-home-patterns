---
name: public-release-audit
description: Audit a repository, public export, staged Git change, commit message, or release candidate for secrets, private infrastructure, personal identifiers, unsafe history, and generated artifacts. Use before creating a public repository, staging or committing public code, publishing a release, reviewing an allowlist, or claiming that an export is privacy-safe.
---

# Public Release Audit

Treat privacy as a fail-closed release property. Run deterministic checks before
model review; a reviewer cannot override a failed hard gate.

## Workflow

1. Define the exact public root. Never treat a private production repository as
   the public source merely because its current files look clean.
2. Run the bundled scanner on the public tree and, when applicable, the staged
   index, commit message, full reachable history, and unreachable objects.
3. Run optional external scanners only after the deterministic gate passes.
   Keep their output redacted and do not perform network verification of a
   candidate credential without explicit authorization.
4. Ask independent reviewers to inspect semantic leaks that regex cannot prove:
   household topology, names, addresses, device mappings, screenshots, routes,
   operational endpoints, and third-party licensing.
5. Resolve every finding by removing or replacing the source. Use an exception
   only when it is exact, content-bound, documented, expiring, and reviewed.
6. Re-run all gates from a clean checkout. Report skipped tools and unreviewed
   media as gaps, never as passes.

## Commands

Scan a candidate directory without writing bytecode:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 \
  skills/public-release-audit/scripts/audit_public_release.py .
```

Before a public commit, scan the tree, staged blobs, and commit message:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 \
  skills/public-release-audit/scripts/audit_public_release.py . \
  --staged --commit-message /path/to/commit-message.txt
```

Before first publication, run the full repository gate from the new public
repository. Explicitly approve the public author email; do not reuse the private
repository history.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 \
  skills/public-release-audit/scripts/audit_public_release.py . \
  --staged --history --unreachable \
  --allow-name "Public Release Bot" \
  --allow-email public@example.com --allow-remote-host github.com
```

Provide household-specific literals through a denylist stored outside the
public tree. The scanner never prints denylist values or matching content.

```bash
python3 skills/public-release-audit/scripts/audit_public_release.py . \
  --deny-pattern-file /private/path/release-denylist.txt
```

Media remains blocked unless an exact manifest binds the relative path to its
current SHA-256 and records source, license, privacy review, and metadata
removal. A changed byte invalidates the grant.

```bash
python3 skills/public-release-audit/scripts/audit_public_release.py . \
  --media-manifest media-manifest.json
```

## Hard gates

- Block credentials, private keys, authenticated URLs, secret assignments,
  private network identifiers, user paths, device identifiers, `.storage`,
  databases, backups, logs, caches, symlinks, binaries, and oversized files.
- Block staged secrets even when the working-tree copy is clean.
- Block secrets and sensitive paths deleted from the tip but retained in
  reachable history, including annotated tag messages and Git ref names.
- Block unreachable Git objects before initial publication; create a fresh
  repository instead of trying to bless unknown residue.
- Block unapproved author and committer names, emails, and signing identities. A public identity is an explicit
  release decision.
- Reject screenshots, CAD, audio, video, and other binary media by default.
  The only media exception is an exact reviewed manifest entry; broad suffix or
  directory allowlists are not supported.

## Review contract

Use separate deterministic and human/model verdicts:

- `PASS`: every required hard gate passed and no review finding remains.
- `REVIEW`: deterministic checks passed, but an external tool, media review,
  license decision, or semantic privacy review is incomplete.
- `FAIL`: any hard-gate finding, unapproved exception, or ambiguous public root.

Never reproduce a discovered credential in output. Report only scope, rule,
path, line when safe, object prefix, and remediation status.

Inventory optional open-source scanners without running them:

```bash
python3 skills/public-release-audit/scripts/check_optional_scanners.py .
```

Run installed scanners locally with candidate values redacted and network
verification disabled. `--strict` makes missing tools an incomplete gate rather
than a silent pass.

```bash
python3 skills/public-release-audit/scripts/check_optional_scanners.py . \
  --run --strict
```

Read [gate-matrix.md](references/gate-matrix.md) before configuring a release
pipeline. Read [prior-art.md](references/prior-art.md) when selecting external
scanners or hooks.
