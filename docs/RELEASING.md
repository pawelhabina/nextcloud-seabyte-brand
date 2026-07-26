<!--
  SPDX-FileCopyrightText: 2026 SeaByte
  SPDX-License-Identifier: GPL-2.0-or-later
-->
# Releasing SeaByte Cloud

## Release checklist

1. Update `SEABYTE_RELEASE_REVISION` default in
   `branding/version.cmake` and `CHANGELOG_SEABYTE.md`.
2. Regenerate assets and run `python3 tools/branding/check_branding.py`.
3. Confirm `git diff --check` and review every remaining Nextcloud literal
   against `tools/branding/nextcloud-allowlist.txt`.
4. Build and smoke-test Windows x64 and macOS arm64.
5. Sign, notarize where applicable, and verify every signature.
6. Verify `SHA256SUMS` from a clean machine.
7. Commit, then create a tag such as
   `seabyte-v33.0.7-seabyte.1`.
8. Push the branch and tag. GitHub Actions uploads build artifacts but does
   not create or publish a release.
9. Manually review the CI artifacts before attaching them to a release or
   update feed.
10. Publish corresponding source code, license and notice with distributed
    GPL binaries.

## Updating the upstream baseline

The official repository is kept as remote `upstream`. Use a new branch and
never rewrite the shared release branch without coordination:

```bash
git remote get-url upstream
git fetch upstream --tags --prune
git switch seabyte-branding
git switch -c update/vNEW
git rebase vNEW
```

Alternatively, replace the final command with `git merge --no-ff vNEW` if the
team's published-history policy forbids rebasing. Resolve conflicts by
preserving upstream protocol behavior first, then reapply the centralized
SeaByte overrides.

After the merge/rebase:

1. update the tag, commit, dates and rationale in `UPSTREAM.md`;
2. update `SEABYTE_UPSTREAM_VERSION` in `branding/version.cmake`;
3. audit upstream `NEXTCLOUD.cmake`, Theme, WiX, mac-crafter, Xcode extension
   IDs and workflows for changed OEM hooks;
4. regenerate all assets;
5. run the branding acceptance suite;
6. build and smoke-test both required platforms;
7. manually inspect the wizard, About UI, tray/menu bar, installer, Explorer
   and Finder;
8. update this documentation and the changelog.

Do not select beta, RC, nightly or development tags as a release baseline.

## Pushing a prepared local repository

If no writable `origin` exists, create a private/authorized destination first,
then run:

```bash
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin seabyte-branding
git push origin 'seabyte-v*'
```

If `origin` already exists, verify it with `git remote -v` and omit the
`git remote add` command. Publishing remains a deliberate manual action.
