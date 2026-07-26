#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 SeaByte
# SPDX-License-Identifier: GPL-2.0-or-later

"""Static acceptance checks for the SeaByte Cloud OEM fork."""

from __future__ import annotations

import argparse
import hashlib
import plistlib
import re
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = ROOT / "tools/branding/nextcloud-allowlist.txt"
SOURCE_SUFFIXES = {".cpp", ".h", ".mm", ".qml", ".ui"}


class Checks:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.passed = 0

    def require(self, condition: bool, description: str) -> None:
        if condition:
            self.passed += 1
        else:
            self.failures.append(description)

    def contains(self, relative: str, *needles: str) -> None:
        path = ROOT / relative
        self.require(path.is_file(), f"missing file: {relative}")
        if not path.is_file():
            return
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            self.require(needle in text, f"{relative} does not contain {needle!r}")


def cmake_default(text: str, key: str) -> str | None:
    match = re.search(
        rf"seabyte_cache_(?:string|bool)\(\s*{re.escape(key)}\s+(?:\"([^\"]*)\"|([^\s\)]+))",
        text,
    )
    return (match.group(1) or match.group(2)) if match else None


def check_identity(checks: Checks) -> None:
    central = (ROOT / "branding/seabyte-branding.cmake").read_text(encoding="utf-8")
    expected = {
        "BRAND_DISPLAY_NAME": "SeaByte Cloud",
        "BRAND_SHORT_NAME": "SeaByte",
        "BRAND_FOLDER_NAME": "seabyte.pl",
        "BRAND_COMPANY": "SeaByte",
        "BRAND_DOMAIN": "seabyte.pl",
        "BRAND_WEBSITE": "https://seabyte.pl",
        "DEFAULT_SERVER_URL": "https://cloud.seabyte.pl",
        "BRAND_CONFIG_NAME": "seabytecloud",
        "WINDOWS_EXECUTABLE_NAME": "SeaByteCloud",
        "WINDOWS_APP_ID": "pl.seabyte.cloud",
        "WINDOWS_INSTALLER_BASENAME": "SeaByte-Cloud-Setup",
        "MACOS_BUNDLE_ID": "pl.seabyte.cloud",
        "MACOS_FILE_PROVIDER_BUNDLE_ID": "pl.seabyte.cloud.fileprovider",
        "MACOS_FILE_PROVIDER_UI_BUNDLE_ID": "pl.seabyte.cloud.fileproviderui",
        "MACOS_FINDER_EXTENSION_BUNDLE_ID": "pl.seabyte.cloud.findersync",
        "MACOS_APP_GROUP": "group.pl.seabyte.cloud",
        "ENABLE_CUSTOM_UPDATER": "OFF",
        "ALLOW_CUSTOM_SERVER": "ON",
    }
    for key, value in expected.items():
        checks.require(cmake_default(central, key) == value, f"{key} must default to {value!r}")

    checks.contains(
        "branding/seabyte-branding.cmake",
        'set(APPLICATION_NAME "${BRAND_DISPLAY_NAME}")',
        'set(APPLICATION_CONFIG_NAME "${BRAND_CONFIG_NAME}")',
        'set(APPLICATION_SERVER_URL "${DEFAULT_SERVER_URL}"',
        'set(APPLICATION_UPDATE_URL "${CUSTOM_UPDATE_URL}"',
        'set(BUILD_UPDATER "${ENABLE_CUSTOM_UPDATER}"',
        "set(DISABLE_ACCOUNT_MIGRATION ON",
    )
    checks.contains(
        "admin/win/msi/CMakeLists.txt",
        '"${WINDOWS_INSTALLER_BASENAME}-${MSI_BUILD_ARCH}-${MIRALL_VERSION}${MIRALL_VERSION_SUFFIX}.msi"',
    )
    checks.contains("admin/win/msi/Nextcloud.wxs", '<Property Id="SKIPAUTOUPDATE" Value="1" />')
    checks.contains(
        "src/libsync/theme.cpp",
        'tr("Based on Nextcloud Desktop")',
        'tr("Upstream version %1")',
        'tr("<p>Application updates are provided by SeaByte.</p>")',
    )
    checks.contains(
        "src/gui/wizard/owncloudsetuppage.cpp",
        "_ui.leUrl->setPlaceholderText(theme->overrideServerUrl())",
    )


def check_version(checks: Checks) -> None:
    upstream = (ROOT / "VERSION.cmake").read_text(encoding="utf-8")
    version = (ROOT / "branding/version.cmake").read_text(encoding="utf-8")

    def value(name: str) -> str:
        match = re.search(rf"set\(\s*{name}\s+\"?([^\"\s\)]+)", upstream)
        return match.group(1) if match else ""

    calculated = ".".join(
        value(name)
        for name in ("MIRALL_VERSION_MAJOR", "MIRALL_VERSION_MINOR", "MIRALL_VERSION_PATCH")
    )
    declared_match = re.search(r'set\(SEABYTE_UPSTREAM_VERSION "([^"]+)"\)', version)
    declared = declared_match.group(1) if declared_match else ""
    checks.require(calculated == declared == "33.0.7", "SeaByte and upstream versions must both be 33.0.7")
    checks.require("-seabyte.${SEABYTE_RELEASE_REVISION}" in version, "brand release suffix is missing")


def ico_sizes(path: Path) -> set[int]:
    data = path.read_bytes()
    if len(data) < 6:
        return set()
    reserved, kind, count = struct.unpack_from("<HHH", data)
    if (reserved, kind) != (0, 1) or len(data) < 6 + (16 * count):
        return set()
    return {
        256 if data[6 + (index * 16)] == 0 else data[6 + (index * 16)]
        for index in range(count)
    }


def icns_chunks(path: Path) -> set[bytes]:
    data = path.read_bytes()
    if len(data) < 8 or data[:4] != b"icns":
        return set()
    declared_size = struct.unpack_from(">I", data, 4)[0]
    if declared_size != len(data):
        return set()
    chunks: set[bytes] = set()
    offset = 8
    while offset + 8 <= len(data):
        kind = data[offset : offset + 4]
        size = struct.unpack_from(">I", data, offset + 4)[0]
        if size < 8 or offset + size > len(data):
            return set()
        chunks.add(kind)
        offset += size
    return chunks if offset == len(data) else set()


def check_assets(checks: Checks) -> None:
    required = [
        "branding/generated/SeaByteCloud.ico",
        "branding/generated/SeaByteCloud.icns",
        "branding/generated/macos-file-provider.png",
        "branding/generated/macos-finder-extension.png",
        "theme/colored/SeaByte-icon.svg",
        "theme/colored/wizard_logo.svg",
        "theme/colored/wizard_logo.png",
        "theme/colored/wizard_logo@2x.png",
        "theme/colored/icons/SeaByte-icon-win-folder.svg",
        "theme/SeaByteCloud.VisualElementsManifest.xml",
        "admin/win/nsi/installer.ico",
        "admin/win/nsi/page_header.bmp",
        "admin/win/nsi/welcome.bmp",
        "admin/win/msi/gui/banner.bmp",
        "admin/win/msi/gui/dialog.bmp",
        "admin/osx/DMGBackground.png",
        "admin/osx/installer-background.png",
        "admin/osx/installer-background_2x.png",
    ]
    required.extend(f"theme/colored/{size}-SeaByte-icon.png" for size in (16, 20, 24, 32, 40, 48, 64, 128, 256, 512, 1024))
    required.extend(
        f"theme/{variant}/seabyte/state-{state}-{size}.png"
        for variant in ("colored", "black", "white")
        for state in ("error", "info", "offline", "ok", "pause", "sync", "warning")
        for size in (16, 32, 64, 128, 256)
    )
    for relative in required:
        path = ROOT / relative
        checks.require(path.is_file() and path.stat().st_size > 0, f"asset missing or empty: {relative}")

    expected_ico_sizes = {16, 20, 24, 32, 40, 48, 64, 128, 256}
    checks.require(
        ico_sizes(ROOT / "branding/generated/SeaByteCloud.ico") == expected_ico_sizes,
        "SeaByteCloud.ico does not contain the expected resolution set",
    )
    checks.require(
        ico_sizes(ROOT / "admin/win/nsi/installer.ico") == expected_ico_sizes,
        "installer.ico does not contain the expected resolution set",
    )
    expected_icns_chunks = {b"icp4", b"icp5", b"icp6", b"ic07", b"ic08", b"ic09", b"ic10"}
    checks.require(
        expected_icns_chunks <= icns_chunks(ROOT / "branding/generated/SeaByteCloud.icns"),
        "SeaByteCloud.icns is missing one or more modern icon chunks",
    )

    for source in ("seabyte-back-logo.svg", "seabyte-full-logo.svg", "seabyte-only-logo.svg"):
        checks.require((ROOT / "branding/source" / source).is_file(), f"brand source missing: {source}")
        checks.require((ROOT / "branding/source" / f"{source}.license").is_file(), f"license sidecar missing: {source}")


def check_platform_ids(checks: Checks) -> None:
    checks.contains(
        "shell_integration/MacOSX/CMakeLists.txt",
        '"PRODUCT_BUNDLE_IDENTIFIER=${MACOS_FINDER_EXTENSION_BUNDLE_ID}"',
        '"PRODUCT_BUNDLE_IDENTIFIER=${MACOS_FILE_PROVIDER_BUNDLE_ID}"',
        '"PRODUCT_BUNDLE_IDENTIFIER=${MACOS_FILE_PROVIDER_UI_BUNDLE_ID}"',
        '"OC_APPLICATION_GROUP=${MACOS_APP_GROUP}"',
    )
    for relative in (
        "admin/osx/macosx.entitlements.cmake",
        "shell_integration/MacOSX/FinderSyncExt.entitlements.cmake",
        "shell_integration/MacOSX/FileProviderExt.entitlements.cmake",
        "shell_integration/MacOSX/FileProviderUIExt.entitlements.cmake",
    ):
        checks.contains(relative, "<string>@MACOS_APP_GROUP@</string>")
    checks.contains(
        "cmake/modules/MacOSXBundleInfo.plist.in",
        "<string>@APPLICATION_REV_DOMAIN@</string>",
        "<string>@BRAND_URI_HANDLER_ALIAS@</string>",
        "<string>@MACOS_APP_GROUP@</string>",
    )
    checks.contains(
        "admin/win/msi/OEM.wxi.in",
        '@BRAND_URI_HANDLER_ALIAS@',
        '@WINDOWS_APP_ID@',
    )
    checks.contains("src/gui/application.cpp", "SetCurrentProcessExplicitAppUserModelID")

    # Render the main plist with representative values and verify that it is
    # valid XML/plist after CMake substitution.
    plist_text = (ROOT / "cmake/modules/MacOSXBundleInfo.plist.in").read_text(encoding="utf-8")
    replacements = {
        "MACOSX_BUNDLE_LOCALIZATIONS": "        <string>en</string>",
        "APPLICATION_NAME": "SeaByte Cloud",
        "APPLICATION_NAME_XML_ESCAPED": "SeaByte Cloud",
        "APPLICATION_ICON_NAME": "SeaByte",
        "APPLICATION_REV_DOMAIN": "pl.seabyte.cloud",
        "APPLICATION_VENDOR_XML_ESCAPED": "SeaByte",
        "APPLICATION_EXECUTABLE": "SeaByteCloud",
        "APPLICATION_VIRTUALFILE_SUFFIX": "seabyte",
        "APPLICATION_URI_HANDLER_SCHEME": "nc",
        "BRAND_URI_HANDLER_ALIAS": "seabytecloud",
        "MACOS_APP_GROUP": "group.pl.seabyte.cloud",
        "MIRALL_VERSION_STRING": "33.0.7-seabyte.1",
        "MIRALL_VERSION_FULL": "33.0.7.0",
    }
    for key, value in replacements.items():
        plist_text = plist_text.replace(f"@{key}@", value)
    try:
        parsed = plistlib.loads(plist_text.encode())
    except Exception as error:  # pragma: no cover - details reported to the user
        checks.require(False, f"rendered main macOS plist is invalid: {error}")
    else:
        checks.require(parsed.get("CFBundleIdentifier") == "pl.seabyte.cloud", "main macOS bundle ID is wrong")
        checks.require(
            parsed.get("CFBundleURLTypes", [{}])[0].get("CFBundleURLSchemes") == ["nc", "seabytecloud"],
            "main macOS URL schemes are wrong",
        )
        checks.require(
            parsed.get("NCFPKAppGroupIdentifier") == "group.pl.seabyte.cloud",
            "main macOS app group is wrong",
        )


def read_allowlist() -> list[re.Pattern[str]]:
    patterns: list[re.Pattern[str]] = []
    for raw_line in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            patterns.append(re.compile(line))
    return patterns


def looks_user_visible(path: Path, line: str) -> bool:
    lowered = line.lower()
    if "nextcloud" not in lowered or "spdx-" in lowered:
        return False
    if path.suffix == ".ui":
        return bool(re.search(r"<string(?:\s[^>]*)?>[^<]*nextcloud", line, re.IGNORECASE))
    if path.suffix == ".qml":
        return bool(re.search(r"\b(?:text|title|placeholderText|toolTip)\s*:.*nextcloud", line, re.IGNORECASE))
    return bool(
        re.search(
            r"(?:\btr\s*\(|QStringLiteral\s*\(|QLatin1String\s*\(|"
            r"QByteArrayLiteral\s*\(|setText\s*\(|setTitle\s*\().*nextcloud",
            line,
            re.IGNORECASE,
        )
    )


def check_visible_upstream_brand(checks: Checks) -> None:
    allow = read_allowlist()
    unexpected: list[str] = []
    for base in (ROOT / "src/gui", ROOT / "src/libsync"):
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if not looks_user_visible(path, line):
                    continue
                relative = path.relative_to(ROOT).as_posix()
                finding = f"{relative}:{number}:{line.strip()}"
                if not any(pattern.search(finding) for pattern in allow):
                    unexpected.append(finding)
    checks.require(
        not unexpected,
        "unexpected user-visible Nextcloud literal(s):\n  " + "\n  ".join(unexpected),
    )


def check_translations(checks: Checks) -> None:
    for relative in ("branding/translations/seabyte_en.ts", "branding/translations/seabyte_pl.ts"):
        checks.contains(
            relative,
            "<name>OCC::Theme</name>",
            "<source>Based on Nextcloud Desktop</source>",
            "<source>&lt;p&gt;Application updates are provided by SeaByte.&lt;/p&gt;</source>",
        )
    checks.contains(
        "CMakeLists.txt",
        "branding/translations/seabyte_*.ts",
        "set(TRANSLATIONS ${TRANS_FILES} ${SEABYTE_TRANS_FILES})",
    )


def check_build_automation(checks: Checks) -> None:
    checks.contains(
        "scripts/build-windows.ps1",
        "windows-msvc2022_64-cl",
        "stable-33.0",
        "SeaByte-Cloud-Setup-x64-",
        "SEABYTE_WINDOWS_CERT_SHA1",
        "SHA256SUMS",
    )
    checks.contains(
        "scripts/build-macos.sh",
        "--disable-auto-updater",
        "--build-file-provider-module",
        "universal2",
        "SEABYTE_MAC_CODE_SIGN_IDENTITY",
        "SHA256SUMS",
    )
    checks.contains(
        ".github/workflows/build-seabyte.yml",
        "Windows x64 MSI",
        "macOS package",
        "Regenerate and verify branding",
        "actions/upload-artifact@v4",
    )
    checks.contains(
        "branding/seabyte-branding.cmake",
        'set(BUILD_WIN_MSI ON CACHE BOOL "Build the SeaByte WiX MSI integration" FORCE)',
    )


def check_sources(checks: Checks) -> None:
    expected_hashes = {
        "seabyte-back-logo.svg": "c2a4a15b20342886cdd0ae47c89506ab598755c82fc1130716c779ecb2b7d1aa",
        "seabyte-full-logo.svg": "aacab6767f936d7405ae1c061f3b5b318a245ad4a6abf239d748fd4b0af9fb60",
        "seabyte-only-logo.svg": "af95aa18ac285df0912c7f6cbc07a612f0bf8fdeda5175818278056dc7fcfad3",
    }
    for name, expected in expected_hashes.items():
        digest = hashlib.sha256((ROOT / "branding/source" / name).read_bytes()).hexdigest()
        checks.require(digest == expected, f"original source asset changed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    args = parser.parse_args()
    checks = Checks()

    for group in (
        check_identity,
        check_version,
        check_assets,
        check_platform_ids,
        check_translations,
        check_build_automation,
        check_sources,
        check_visible_upstream_brand,
    ):
        group(checks)

    if checks.failures:
        print(f"SeaByte branding checks FAILED ({len(checks.failures)} failure(s)):", file=sys.stderr)
        for failure in checks.failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"SeaByte branding checks passed ({checks.passed} assertions).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
