#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 SeaByte
# SPDX-License-Identifier: GPL-2.0-or-later

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
build_root="${SEABYTE_MAC_BUILD_ROOT:-${repo_root}/.build/macos}"
dist_dir="${repo_root}/dist/macos"
arch_mode="${SEABYTE_MAC_ARCH:-arm64}"
skip_tests=0

usage() {
    echo "Usage: $0 [--arch arm64|x86_64|universal2] [--skip-tests]"
}

while (($#)); do
    case "$1" in
        --arch)
            arch_mode="${2:?missing value for --arch}"
            shift 2
            ;;
        --skip-tests)
            skip_tests=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage >&2
            exit 2
            ;;
    esac
done

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "SeaByte macOS packages must be built on macOS." >&2
    exit 1
fi
if [[ "$arch_mode" != "arm64" && "$arch_mode" != "x86_64" && "$arch_mode" != "universal2" ]]; then
    echo "Unsupported architecture: $arch_mode" >&2
    exit 2
fi
for command in git python3 swift xcodebuild brew ctest ditto shasum; do
    command -v "$command" >/dev/null || {
        echo "Required command is missing: $command" >&2
        exit 1
    }
done
if ! xcodebuild -version >/dev/null 2>&1; then
    echo "Full Xcode is required; Command Line Tools alone are insufficient." >&2
    exit 1
fi

python3 "${repo_root}/tools/branding/check_branding.py"
mkdir -p "$build_root" "$dist_dir"

mac_crafter_dir="${repo_root}/admin/osx/mac-crafter"
revision="${SEABYTE_RELEASE_REVISION:-1}"
version="33.0.7-seabyte.${revision}"
signature_label="unsigned"
code_sign_identity="${SEABYTE_MAC_CODE_SIGN_IDENTITY:-}"
enable_custom_updater="${SEABYTE_ENABLE_CUSTOM_UPDATER:-0}"
if [[ "$enable_custom_updater" == "1" || "$enable_custom_updater" == "ON" || "$enable_custom_updater" == "true" ]]; then
    if [[ -z "${CUSTOM_UPDATE_URL:-}" ]]; then
        echo "CUSTOM_UPDATE_URL is required when SEABYTE_ENABLE_CUSTOM_UPDATER is enabled." >&2
        exit 2
    fi
    if [[ -z "${CUSTOM_SPARKLE_PUBLIC_KEY:-}" ]]; then
        echo "CUSTOM_SPARKLE_PUBLIC_KEY is required when the macOS updater is enabled." >&2
        exit 2
    fi
    export ENABLE_CUSTOM_UPDATER=ON
else
    export ENABLE_CUSTOM_UPDATER=OFF
fi

build_one_arch() {
    local arch="$1"
    local arch_build="${build_root}/${arch}"
    local arch_product="${arch_build}/product"
    local args=(
        build "$repo_root"
        --arch "$arch"
        --build-path "$arch_build"
        --product-path "$arch_product"
        --build-type Release
        --app-name "SeaByte Cloud"
        --client-blueprints-git-ref stable-33.0
        --kde-blueprints-git-ref stable-33.0
        --build-file-provider-module
        --override-server-url "https://cloud.seabyte.pl"
    )
    if [[ "$ENABLE_CUSTOM_UPDATER" == "OFF" ]]; then
        args+=(--disable-auto-updater)
    fi
    if ((skip_tests == 0)); then
        args+=(--build-tests)
    fi
    if [[ -n "$code_sign_identity" && "$arch_mode" != "universal2" ]]; then
        args+=(--code-sign-identity "$code_sign_identity")
        signature_label="signed"
    fi
    (
        cd "$mac_crafter_dir"
        swift run mac-crafter "${args[@]}"
    )
    if ((skip_tests == 0)); then
        local test_dir="${arch_build}/$( [[ "$arch" == "arm64" ]] && echo macos-clang-arm64 || echo macos-64-clang )/build/nextcloud-client/work/build"
        ctest --test-dir "$test_dir" --output-on-failure --timeout 300
    fi
}

if [[ "$arch_mode" == "universal2" ]]; then
    build_one_arch x86_64
    build_one_arch arm64
    universal_product="${build_root}/universal/product"
    mkdir -p "$universal_product"
    python3 "${repo_root}/admin/osx/make_universal.py" \
        "${build_root}/x86_64/product/SeaByte Cloud.app" \
        "${build_root}/arm64/product/SeaByte Cloud.app" \
        "$universal_product"
    app_path="${universal_product}/SeaByte Cloud.app"

    # lipo invalidates nested signatures. Re-sign the merged bundle even for
    # unsigned builds (ad-hoc identity "-") so macOS can verify its structure.
    identity="${code_sign_identity:--}"
    arm_work="${build_root}/arm64/macos-clang-arm64/build/nextcloud-client/work/build"
    (
        cd "$mac_crafter_dir"
        swift run mac-crafter codesign \
            "$app_path" "$identity" \
            "${arm_work}/admin/osx/macosx.entitlements" \
            "${arm_work}/shell_integration/MacOSX/FileProviderExt.entitlements" \
            "${arm_work}/shell_integration/MacOSX/FileProviderUIExt.entitlements" \
            "${arm_work}/shell_integration/MacOSX/FinderSyncExt.entitlements"
    )
    [[ -n "$code_sign_identity" ]] && signature_label="signed"
else
    build_one_arch "$arch_mode"
    app_path="${build_root}/${arch_mode}/product/SeaByte Cloud.app"
fi

if [[ "$signature_label" == "signed" || "$arch_mode" == "universal2" ]]; then
    codesign --verify --deep --strict --verbose=2 "$app_path"
fi

artifact_arch="$arch_mode"
zip_path="${dist_dir}/SeaByte-Cloud-${version}-${artifact_arch}-${signature_label}.zip"
ditto -c -k --sequesterRsrc --keepParent "$app_path" "$zip_path"

dmg_work="${build_root}/dmg"
mkdir -p "$dmg_work"
dmg_args=(
    create-dmg "$app_path"
    --product-path "$dmg_work"
    --build-path "$build_root"
    --app-name "SeaByte Cloud"
)
if [[ -n "$code_sign_identity" ]]; then
    dmg_args+=(--package-signing-id "$code_sign_identity")
fi
if [[ -n "${SEABYTE_APPLE_ID:-}" && -n "${SEABYTE_APPLE_PASSWORD:-}" && -n "${SEABYTE_APPLE_TEAM_ID:-}" ]]; then
    dmg_args+=(
        --apple-id "$SEABYTE_APPLE_ID"
        --apple-password "$SEABYTE_APPLE_PASSWORD"
        --apple-team-id "$SEABYTE_APPLE_TEAM_ID"
    )
fi
(
    cd "$mac_crafter_dir"
    swift run mac-crafter "${dmg_args[@]}"
)
dmg_path="${dist_dir}/SeaByte-Cloud-${version}-${artifact_arch}-${signature_label}.dmg"
mv "${dmg_work}/SeaByte Cloud.dmg" "$dmg_path"

git_sha="$(git -C "$repo_root" rev-parse HEAD)"
printf '%s\n' \
    '{' \
    '  "product": "SeaByte Cloud",' \
    '  "upstream_version": "33.0.7",' \
    "  \"brand_revision\": \"${revision}\"," \
    "  \"architecture\": \"${artifact_arch}\"," \
    "  \"signature\": \"${signature_label}\"," \
    "  \"git_sha\": \"${git_sha}\"" \
    '}' >"${dist_dir}/build-metadata.json"
(
    cd "$dist_dir"
    shasum -a 256 ./*.dmg ./*.zip build-metadata.json > SHA256SUMS
)
echo "Created ${dmg_path} and ${zip_path}"
