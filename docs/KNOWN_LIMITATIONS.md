<!--
  SPDX-FileCopyrightText: 2026 SeaByte
  SPDX-License-Identifier: GPL-2.0-or-later
-->
# Known limitations

## Cross-platform

- `nc://` is retained for Nextcloud server local-edit compatibility. Operating
  systems generally allow one handler per URL scheme, so the last installed
  client may own `nc://`. SeaByte also registers `seabytecloud://`, but a
  server must explicitly emit that alias to use it.
- Logs and many internal logging categories, WebDAV namespaces, capabilities,
  class names and server feature names still contain `nextcloud`. They are
  compatibility or attribution tokens, not product branding.
- Existing account data is not imported. SeaByte uses `seabytecloud` settings
  and the `SeaByte Cloud` keychain service, which is safer for coexistence but
  requires accounts to be added again.
- The official updater is absent. Users must install releases manually until
  a signed SeaByte feed is deployed and tested.

## Windows

- Explorer has a system-wide limit and ordering rules for icon overlay
  handlers. SeaByte uses unique GUIDs, but overlays can still be hidden when
  many other products are installed.
- Only one application can own the shared `nc://` registry handler at a time.
- MSI creation, Explorer integration, autostart and uninstall data retention
  require a real Windows smoke test; static checks cannot prove them.
- ProductCode is generated for each MSI build. UpgradeCode remains stable and
  unique to SeaByte.

## macOS

- Finder/File Provider controls some presentation. The provider display name
  is set to `seabyte.pl` and SeaByte artwork is generated, but macOS may cache
  or ignore a custom provider/sidebar icon and may show a system cloud symbol.
  A successful app build does not prove which icon a given macOS release will
  render.
- File Provider and Finder Sync behavior depends on signing, App Group
  entitlements and user approval. Unsigned builds are unsuitable for a final
  integration judgment.
- The optional universal2 path builds both architectures and merges them, but
  it is not certified until exercised on both Intel and Apple Silicon.
- Like Windows, only one installed application is selected for `nc://`.
- Full app, extension, signing and notarization tests require full Xcode and
  real Apple Developer credentials.
