<!--
  SPDX-FileCopyrightText: 2026 SeaByte
  SPDX-License-Identifier: GPL-2.0-or-later
-->
# Signing and notarization

Unsigned builds are valid for internal testing and are named `-unsigned`.
Release builds should be signed by real SeaByte credentials. No certificate,
private key or password belongs in the repository.

## Windows Authenticode

Use a publicly trusted code-signing certificate available as PFX or through a
managed signing service. Sign every shipped EXE/DLL before MSI harvesting and
sign the final MSI. Use SHA-256 and a trusted RFC 3161 timestamp so signatures
remain valid after certificate expiry.

The local script expects an already imported certificate and:

```text
SEABYTE_WINDOWS_CERT_SHA1
SEABYTE_WINDOWS_TIMESTAMP_URL   optional; defaults to DigiCert
```

GitHub Actions imports a temporary PFX only when both secrets exist:

```text
WINDOWS_PFX_BASE64
WINDOWS_PFX_PASSWORD
```

Encode the binary PFX as a single-line Base64 secret. The workflow deletes the
temporary PFX after import and never prints the password. For a cloud HSM,
replace only the import/signing step while keeping the same build and artifact
gates.

## macOS Developer ID

The app and every nested framework, helper and extension must be signed in
inside-out order with:

- Developer ID Application certificate;
- hardened runtime;
- the generated main, Finder Sync, File Provider and File Provider UI
  entitlements;
- App Group `group.pl.seabyte.cloud`.

The upstream mac-crafter signer uses `codesign --options=runtime --timestamp`
and preserves the matching entitlements. The DMG is signed, submitted with
`notarytool`, and stapled when all notarization inputs are present. A Developer
ID Installer identity is only required if a signed `.pkg` is introduced; the
current deliverables are DMG and ZIP.

GitHub secrets:

```text
MACOS_CERTIFICATE_BASE64
MACOS_CERTIFICATE_PASSWORD
MACOS_CODE_SIGN_IDENTITY
APPLE_ID
APPLE_APP_PASSWORD
APPLE_TEAM_ID
```

The certificate should be a PKCS#12 export containing the Developer ID
Application private key. `APPLE_APP_PASSWORD` is an Apple app-specific
password, not the account password. The workflow creates an ephemeral
keychain. It signs when the certificate and identity secrets are present;
otherwise it produces an explicitly unsigned artifact. Notarization runs only
when Apple ID, app password and Team ID are all supplied.

Before release, verify:

```bash
codesign --verify --deep --strict --verbose=2 "SeaByte Cloud.app"
spctl --assess --type execute --verbose=4 "SeaByte Cloud.app"
xcrun stapler validate "SeaByte Cloud.dmg"
```
