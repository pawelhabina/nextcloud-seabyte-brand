<!--
  SPDX-FileCopyrightText: 2026 SeaByte
  SPDX-License-Identifier: GPL-2.0-or-later
-->
# Building SeaByte Cloud for Windows

## Supported release target

The release target is Windows 10/11 x64 using Visual Studio 2022, Qt 6 and KDE
Craft's `windows-msvc2022_64-cl` target. WiX v3 creates the MSI. The script
uses the upstream `stable-33.0` KDE and desktop-client blueprint branches.

Required host software:

- Windows 10 or 11 x64;
- Visual Studio 2022 with Desktop development with C++;
- Git, Python 3.12, CMake and PowerShell 7 or Windows PowerShell 5.1;
- Chocolatey, unless WiX v3 is already installed.

The first run downloads and builds a substantial KDE Craft dependency tree.

## One-command build

Open a developer PowerShell in the repository root:

```powershell
./scripts/build-windows.ps1
```

The script validates branding, configures KDE Craft, builds Release, runs
CTest, creates the WiX MSI, and writes:

```text
dist/windows/SeaByte-Cloud-Setup-x64-33.0.7-seabyte.1-unsigned.msi
dist/windows/build-metadata.json
dist/windows/SHA256SUMS
```

Use `-SkipDependencyInstall` only after Craft and WiX have been prepared, or
`-SkipTests` only for a diagnostic iteration. Neither option is suitable for
a release build.

To build a new brand revision:

```powershell
$env:SEABYTE_RELEASE_REVISION = "2"; ./scripts/build-windows.ps1
```

## Signed local build

Import the Authenticode certificate into the current user's certificate
store, then expose only its SHA-1 thumbprint:

```powershell
$env:SEABYTE_WINDOWS_CERT_SHA1 = "CERTIFICATE_THUMBPRINT"; ./scripts/build-windows.ps1
```

The script signs the image binaries before harvesting and signs the final MSI
with SHA-256 and an RFC 3161 timestamp. See [SIGNING.md](SIGNING.md).

## Manual verification

On a disposable Windows test account:

1. Verify the checksum and Authenticode status, if signed.
2. Install the MSI and confirm `SeaByte Cloud` in Apps & features.
3. Start `SeaByteCloud.exe`; confirm the SeaByte icon and default server.
4. Add a test account, synchronize a small file in both directions, and
   inspect tray notifications.
5. Enable autostart and confirm its entry launches SeaByte Cloud.
6. Confirm Explorer navigation, context menu, overlays and virtual-files
   provider behavior.
7. Install the official Nextcloud client side by side and verify separate
   configuration and credentials.
8. Uninstall SeaByte Cloud and confirm the user's sync data remains.

Platform smoke tests must be recorded as unrun unless these actions were
actually performed.
