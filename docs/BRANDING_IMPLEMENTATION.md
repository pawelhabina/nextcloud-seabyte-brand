<!--
  SPDX-FileCopyrightText: 2026 SeaByte
  SPDX-License-Identifier: GPL-2.0-or-later
-->
# SeaByte branding implementation plan

## Upstream mechanisms selected

The fork uses the upstream OEM configuration in `NEXTCLOUD.cmake` instead of
global string replacement. A SeaByte CMake module will override only public
application identity, server defaults, updater policy, package identifiers,
installer metadata, extension identifiers and asset paths.

Windows packaging uses the existing WiX MSI implementation in
`admin/win/msi`, built through KDE Craft. The existing NSIS directory is
translation and legacy support material, not the primary installer path for
this release.

macOS packaging uses the existing `admin/osx/mac-crafter` Swift tool, KDE
Craft, the main CMake app bundle, and the Xcode extension project under
`shell_integration/MacOSX`.

## Planned files and responsibilities

| Area | Files |
| --- | --- |
| Central identity | `branding/seabyte-branding.cmake`, `branding/version.cmake`, `NEXTCLOUD.cmake`, `config.h.in` |
| Asset pipeline | `branding/source/*`, `tools/branding/generate_assets.py`, `branding/ASSET_MAP.md`, generated files under `theme/colored`, `admin/win`, and `admin/osx` |
| Shared UI | `src/libsync/theme.*`, account wizard defaults and About UI sources selected after source inspection |
| Windows | `admin/win/msi/*`, `shell_integration/windows/*`, `scripts/build-windows.ps1` |
| macOS | `admin/osx/*`, `shell_integration/MacOSX/*`, `scripts/build-macos.sh` |
| Updater | CMake `BUILD_UPDATER` policy plus `docs/UPDATES.md` |
| Verification | `tools/branding/check_branding.py`, asset tests, CMake configure smoke test |
| CI | `.github/workflows/build-seabyte.yml` |
| Operations | `README_SEABYTE.md`, `docs/BUILD_*.md`, `docs/SIGNING.md`, `docs/RELEASING.md`, `docs/KNOWN_LIMITATIONS.md`, `NOTICE_SEABYTE.md`, `CHANGELOG_SEABYTE.md` |

## Data-safety decisions

- SeaByte uses its own executable and configuration name so it does not import
  or overwrite Nextcloud Desktop settings.
- Account migration and the legacy import dialog are disabled.
- Server protocol names, WebDAV paths, capabilities, login flow and the
  compatible `nc` local-edit URL scheme are retained.
- The SeaByte callback/bundle identity remains unique where controlled by the
  application, but no server-facing protocol tokens are renamed.
- The official updater is compiled out until a SeaByte update endpoint is
  deliberately configured.

