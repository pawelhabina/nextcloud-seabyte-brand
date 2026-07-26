<!--
  SPDX-FileCopyrightText: 2026 SeaByte
  SPDX-License-Identifier: GPL-2.0-or-later
-->
# SeaByte Cloud Desktop

SeaByte Cloud is SeaByte's branded desktop synchronization client, based on
the official Nextcloud Desktop Client. It connects by default to
`https://cloud.seabyte.pl`, creates a local folder named `seabyte.pl`, and
still lets the user choose another compatible server.

This branch is based on Nextcloud Desktop `v33.0.7`, commit
`497d6610b3b954b35307ee665429fd4ba9ae68d4`. The product version is
`33.0.7-seabyte.1`; the last component is the independently incremented
SeaByte packaging revision. See [UPSTREAM.md](UPSTREAM.md) and
[NOTICE_SEABYTE.md](NOTICE_SEABYTE.md).

## What is branded

- application, executable, installer, shortcuts, notifications and About UI;
- Windows AppUserModelID, MSI identity, registry roots and Explorer overlays;
- macOS app, Finder Sync and File Provider bundle IDs, app group and artwork;
- configuration, logs, autostart and keychain service namespace;
- default server and local sync-folder name;
- updater policy: the official Nextcloud feed is not used.

The compatible `nc://` local-edit scheme and Nextcloud server/WebDAV protocol
tokens deliberately remain unchanged. A unique `seabytecloud://` alias is
registered as well.

## Brand configuration

All public defaults live in
[`branding/seabyte-branding.cmake`](branding/seabyte-branding.cmake), and the
release revision lives in [`branding/version.cmake`](branding/version.cmake).
Each public value can be overridden either as a CMake cache option or by an
environment variable of the same name.

For example:

```bash
DEFAULT_SERVER_URL=https://staging.example \
SEABYTE_RELEASE_REVISION=2 \
cmake -S . -B build
```

Set `ALLOW_CUSTOM_SERVER=OFF` to make the preconfigured server mandatory.

## Generate artwork

From the repository root, the following one-liner creates an isolated Python
environment, installs pinned dependencies and regenerates every asset:

```bash
python3 -m venv .venv-branding && .venv-branding/bin/pip install -r tools/branding/requirements.txt && .venv-branding/bin/python tools/branding/generate_assets.py
```

The generator reads only the copied SVGs in `branding/source`. It does not
modify the designer's original directory. Outputs and their consumers are
listed in [branding/ASSET_MAP.md](branding/ASSET_MAP.md).

Run the static acceptance suite with:

```bash
python3 tools/branding/check_branding.py
```

## Build

Windows x64, from PowerShell on Windows:

```powershell
./scripts/build-windows.ps1
```

macOS Apple Silicon, from a macOS host with full Xcode:

```bash
./scripts/build-macos.sh --arch arm64
```

The scripts run tests and place versioned, explicitly `signed` or `unsigned`
artifacts plus `SHA256SUMS` under `dist/windows` and `dist/macos`. Detailed
requirements and troubleshooting are in
[docs/BUILD_WINDOWS.md](docs/BUILD_WINDOWS.md) and
[docs/BUILD_MACOS.md](docs/BUILD_MACOS.md).

## Releases and maintenance

- Signing and GitHub secret names: [docs/SIGNING.md](docs/SIGNING.md)
- Private updater protocol: [docs/UPDATES.md](docs/UPDATES.md)
- Release checklist: [docs/RELEASING.md](docs/RELEASING.md)
- Known platform limits: [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md)
- Latest local verification: [docs/VERIFICATION_REPORT.md](docs/VERIFICATION_REPORT.md)
- SeaByte changes: [CHANGELOG_SEABYTE.md](CHANGELOG_SEABYTE.md)

To update the fork, fetch a new stable tag from the `upstream` remote, create
an update branch from `seabyte-branding`, rebase or merge the tag, resolve the
small OEM surface, regenerate assets, run the branding suite, and rebuild both
platforms. The exact commands and review gates are in
[docs/RELEASING.md](docs/RELEASING.md#updating-the-upstream-baseline).
