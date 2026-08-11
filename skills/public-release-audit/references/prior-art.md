# Prior art and adopted boundaries

No upstream code is copied into this Skill.

- **Gitleaks**: adopt separate directory, staged/commit, and Git-history scans;
  redact output; pin hook versions; use exact fingerprints for reviewed noise.
- **TruffleHog**: adopt broad secret classification and signed-release
  verification. Run filesystem scans with `--no-verification --no-update`; its
  normal validation can contact a provider with candidate material.
- **detect-secrets**: adopt baseline review, entropy as supplementary evidence,
  `--no-verify`, and explicit human auditing of probable false positives.
- **pre-commit**: adopt a local developer feedback hook, while keeping CI and
  release-time scans independent because local hooks can be skipped.
- **git-secrets**: adopt staged, untracked, commit-message, and history coverage,
  while retaining the warning that regex is insurance rather than proof.

The built-in scanner remains dependency-free and privacy-specific. External
tools increase coverage but do not replace checks for household topology,
device identifiers, media, Git identity, or private operational history.
