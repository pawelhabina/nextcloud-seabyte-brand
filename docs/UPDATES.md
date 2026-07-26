<!--
  SPDX-FileCopyrightText: 2026 SeaByte
  SPDX-License-Identifier: GPL-2.0-or-later
-->
# SeaByte update channel

## Current policy

Automatic updating is disabled by default:

```text
ENABLE_CUSTOM_UPDATER=OFF
CUSTOM_UPDATE_URL=
APPLICATION_UPDATE_URL=
BUILD_UPDATER=OFF
```

The official `https://updates.nextcloud.org/client/` feed is therefore not
compiled into SeaByte Cloud. The Windows MSI also writes `skipUpdateCheck=1`.
The About UI says that SeaByte supplies application updates.

## Enabling a private channel

Only enable updates after a production HTTPS endpoint, signing keys, rollback
plan and staged rollout have been established:

```bash
ENABLE_CUSTOM_UPDATER=ON \
CUSTOM_UPDATE_URL=https://updates.seabyte.pl/desktop/ \
CUSTOM_SPARKLE_PUBLIC_KEY=BASE64_EDDSA_PUBLIC_KEY \
SEABYTE_ENABLE_CUSTOM_UPDATER=1 \
./scripts/build-macos.sh --arch arm64
```

For Windows, set the first two variables before
`./scripts/build-windows.ps1`. The values are consumed by the central branding
module, so no source edit is required. Enabling the updater still requires a
new signed client build.

The client adds query parameters such as `version`, `platform`, `oem`,
`buildArch`, `versionsuffix`, `channel`, and `msi=true`. macOS also requests
`sparkle=true` and `fileprovider=true`. The service must select only compatible
SeaByte artifacts and must never redirect to an official unbranded package.

## Windows response

For Windows, return UTF-8 XML with the upstream-compatible schema:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<owncloudclient>
  <version>33.0.7.1</version>
  <versionstring>SeaByte Cloud 33.0.7-seabyte.1</versionstring>
  <downloadurl>https://updates.seabyte.pl/desktop/SeaByte-Cloud-Setup-x64-33.0.7-seabyte.1-signed.msi</downloadurl>
  <web>https://seabyte.pl/download</web>
</owncloudclient>
```

`version` must be monotonically comparable by the client's numeric
major/minor/patch/build parser. `downloadurl` must use HTTPS and point to the
signed MSI whose checksum and Authenticode signature were verified before
publication.

## macOS response

When `sparkle=true`, return a Sparkle 2 RSS appcast. The enclosure must point
to the notarized SeaByte update archive, include byte length, a monotonically
increasing `sparkle:version`, the display version, and a valid Sparkle EdDSA
signature. `CUSTOM_SPARKLE_PUBLIC_KEY` is embedded as `SUPublicEDKey`; the
build fails if it is missing while the macOS updater is enabled. Keep the
private key only in the release signing service.

Serve feeds and packages with TLS, immutable versioned paths and appropriate
content types. Retain older signed packages for rollback. Test upgrade,
downgrade rejection, interrupted download and a deliberately invalid
signature before production rollout.
