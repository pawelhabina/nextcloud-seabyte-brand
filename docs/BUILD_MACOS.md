<!--
  SPDX-FileCopyrightText: 2026 SeaByte
  SPDX-License-Identifier: GPL-2.0-or-later
-->
# Building SeaByte Cloud for macOS

## Requirements

- macOS 13 or newer;
- full Xcode selected with `xcode-select` (Command Line Tools alone are not
  enough);
- Swift, Git, Python 3, CMake/CTest and Homebrew;
- sufficient disk space for Qt 6 and KDE Craft.

The build uses upstream `admin/osx/mac-crafter`, KDE Craft and the
`NextcloudIntegration.xcodeproj` extensions.

## One-command Apple Silicon build

```bash
./scripts/build-macos.sh --arch arm64
```

The script validates branding, performs a Release build with File Provider,
runs CTest, creates `SeaByte Cloud.app`, then produces:

```text
dist/macos/SeaByte-Cloud-33.0.7-seabyte.1-arm64-unsigned.dmg
dist/macos/SeaByte-Cloud-33.0.7-seabyte.1-arm64-unsigned.zip
dist/macos/build-metadata.json
dist/macos/SHA256SUMS
```

Full dependencies are cached below `.build/macos`. Set
`SEABYTE_MAC_BUILD_ROOT` to move that cache.

## Universal 2 option

```bash
./scripts/build-macos.sh --arch universal2
```

This independently builds x86_64 and arm64, merges Mach-O files with the
upstream `make_universal.py`, and re-signs the merged bundle. The option is
implemented but is not considered verified until it completes on CI or a
proper macOS build host and the resulting application is tested on both CPU
families.

## Signing and notarization

Set `SEABYTE_MAC_CODE_SIGN_IDENTITY` to a Developer ID Application identity.
If all three notarization values are also present, the DMG is submitted and
stapled:

```bash
SEABYTE_MAC_CODE_SIGN_IDENTITY="Developer ID Application: SeaByte (...)" \
SEABYTE_APPLE_ID="release@example.com" \
SEABYTE_APPLE_PASSWORD="@keychain:AC_PASSWORD" \
SEABYTE_APPLE_TEAM_ID="TEAMID" \
./scripts/build-macos.sh --arch arm64
```

Use a keychain reference or CI secret for the app-specific password. Never
commit it. See [SIGNING.md](SIGNING.md).

## Manual verification

1. Inspect bundle IDs with `codesign -d --entitlements :-` and
   `mdls`/`plutil`.
2. Launch the app and confirm name, icon, menu bar and default server.
3. Add a test account and synchronize a small file in both directions.
4. Confirm the provider appears as `seabyte.pl` in Finder.
5. Exercise download/evict, Finder actions and Finder Sync as applicable.
6. Confirm the app and all `.appex` bundles share
   `group.pl.seabyte.cloud`.
7. Confirm Login Item behavior.
8. Install official Nextcloud side by side and verify separate preferences and
   keychain services.

macOS may cache provider names/icons; sign out or remove/re-add the File
Provider domain before judging a changed asset.
