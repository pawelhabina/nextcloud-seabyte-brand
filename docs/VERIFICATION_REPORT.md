<!--
  SPDX-FileCopyrightText: 2026 SeaByte
  SPDX-License-Identifier: GPL-2.0-or-later
-->
# Verification report — 2026-07-26

## Environment

Verification ran on Apple Silicon (`arm64`), macOS 26.5.2, with CMake 4.4.0,
Python 3.14.0 and Swift 6.0.3. Only Apple Command Line Tools are installed at
`/Library/Developer/CommandLineTools`; full Xcode, Qt 6 and PowerShell are not
available.

## Completed checks

| Check | Result | Evidence |
| --- | --- | --- |
| Upstream baseline | Passed | `v33.0.7` resolves to `497d6610b3b954b35307ee665429fd4ba9ae68d4` |
| Source-artwork preservation | Passed | all three copied SVGs are byte-identical to the read-only originals |
| Asset generation | Passed | pinned generator completed; subsequent `git diff --exit-code` was clean |
| Branding acceptance | Passed | 244 assertions |
| ICO/ICNS contents | Passed | verified by the branding suite using binary parsers |
| Visible upstream-name scan | Passed | no finding outside the documented regex allowlist |
| Python syntax | Passed | generator and acceptance script compiled |
| Bash syntax | Passed | `bash -n scripts/build-macos.sh` |
| XML and translations | Passed | `xmllint` on WiX, Visual Elements manifest and both SeaByte TS files |
| macOS plist syntax | Passed | four Xcode plists passed `plutil`; the rendered main template passed `plistlib` |
| Workflow syntax | Passed | YAML parsed successfully |
| Central CMake configuration | Passed | default and overridden server configurations executed with `cmake -P` |
| Custom updater safety | Passed | valid URL/key configuration succeeded; missing Sparkle key failed as intended |
| Whitespace | Passed | `git diff --check` |
| Visual asset review | Passed | 16 px app icon remains recognizable; DMG wordmark is proportional and uncut |

## Builds and platform smoke tests

| Target/test | Result | Reason |
| --- | --- | --- |
| Full CMake configure | Blocked by environment | Qt 6 `qtpaths` is not installed |
| C++ build and CTest | Not run | requires the Qt/KDE Craft build produced after configuration |
| macOS `desktopclient` Xcode scheme | Blocked by environment | full Xcode is not installed |
| macOS `NextcloudDev` Xcode target | Blocked by environment | full Xcode is not installed |
| Swift source parse | Blocked by environment | installed Command Line Tools expose duplicate `SwiftBridging` module maps |
| macOS release script | Blocked at preflight | correctly reports that full Xcode is required |
| Windows x64 Release/MSI | Not run | current host is macOS and PowerShell is unavailable |
| Windows application/account/sync/autostart/Explorer/uninstall smoke | Not run | requires the Windows artifact and a Windows test host |
| macOS app/account/sync/menu bar/Finder/File Provider smoke | Not run | requires a signed app built with full Xcode |
| macOS universal2 | Not run | optional path is implemented but requires both architecture builds |
| Signing/notarization | Not run | real Authenticode and Apple Developer credentials were not provided |

No installer was produced locally, so there are no artifact SHA-256 values from
this host. The platform scripts and GitHub workflow generate `SHA256SUMS` when
they successfully create packages. A release must not promote the static checks
above as a substitute for the explicitly unrun platform smoke tests.
