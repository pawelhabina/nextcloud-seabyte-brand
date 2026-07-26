<!--
  SPDX-FileCopyrightText: 2026 SeaByte
  SPDX-License-Identifier: GPL-2.0-or-later
-->
# SeaByte asset map

Run `python3 tools/branding/generate_assets.py` after installing the pinned
packages from `tools/branding/requirements.txt`. The script only reads
`branding/source`.

| Source | Generated output | Use |
| --- | --- | --- |
| `seabyte-only-logo.svg` | `theme/colored/SeaByte-icon.svg` and `16-` through `1024-SeaByte-icon.png` | Application, executable, taskbar, Launchpad and notifications |
| `seabyte-only-logo.svg` | `branding/generated/SeaByteCloud.ico` | Multi-resolution Windows application icon/reference |
| `seabyte-only-logo.svg` | `admin/win/nsi/installer.ico` | Windows installer icon |
| `seabyte-only-logo.svg` | `branding/generated/SeaByteCloud.icns` | Multi-resolution macOS application icon/reference |
| `seabyte-only-logo.svg` | `theme/colored/SeaByte-w10startmenu.svg`, `70-` and `150-SeaByte-w10startmenu.png` | Windows Start tiles |
| `seabyte-only-logo.svg` | `theme/colored/icons/SeaByte-icon-win-folder.svg` | Windows virtual-files root folder icon |
| `seabyte-only-logo.svg` | `theme/colored/SeaByte-sidebar.svg` | Finder sidebar source |
| `seabyte-only-logo.svg` | `theme/{colored,black,white}/seabyte/state-*` | Branded tray/menu-bar sync states, including monochrome variants |
| `seabyte-only-logo.svg` | `branding/generated/macos-template/*` | macOS menu-bar template references |
| `seabyte-only-logo.svg` | `branding/generated/windows-overlays/*.ico`, `shell_integration/windows/NCOverlays/ico/*.ico` | Explorer overlay resources |
| `seabyte-only-logo.svg` | `branding/generated/macos-file-provider.png`, `macos-finder-extension.png` | File Provider and Finder extension artwork |
| `seabyte-full-logo.svg` | `theme/colored/wizard_logo.svg`, `.png`, `@2x.png` | Account wizard |
| `seabyte-full-logo.svg` | `admin/win/msi/gui/banner.bmp`, `dialog.bmp` | WiX MSI user interface |
| `seabyte-full-logo.svg` | `admin/win/nsi/page_header.bmp`, `welcome.bmp` | Legacy NSIS surfaces |
| `seabyte-full-logo.svg` | `admin/osx/DMGBackground.png` | DMG background |
| `seabyte-full-logo.svg` | `admin/osx/installer-background.png`, `_2x.png` | macOS package installer background |

The build still lets ECM create its native `.ico` and `.icns` files from the
same checked-in SVG/PNG set. The files under `branding/generated` are produced
as independently testable canonical references.
