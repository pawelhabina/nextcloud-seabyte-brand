//  SPDX-FileCopyrightText: 2024 Nextcloud GmbH and Nextcloud contributors
//  SPDX-License-Identifier: GPL-2.0-or-later

import FileProvider
import NextcloudKit

///
/// The descriptive identifier for the service exposed at certain locations.
///
/// The identifier is derived from the centrally supplied application reverse
/// domain so branded clients never share an XPC service name.
///
let fpUiExtensionServiceName = NSFileProviderServiceName(
    "\((Bundle.main.object(forInfoDictionaryKey: "OCApplicationReverseDomain") as? String) ?? "pl.seabyte.cloud").FPUIExtensionService"
)

///
/// The requirements of the service exposed and dedicated to the file provider user interface extension.
///
@objc protocol FPUIExtensionService {
    ///
    /// Request (re)authentication with the available credentials.
    ///
    /// - Returns: An error in case of failure, otherwise `nil`.
    ///
    func authenticate() async -> NSError?

    ///
    /// Fetch the user agent used by the underlying NextcloudKit.
    ///
    func userAgent() async -> NSString?

    ///
    /// Fetch the credentials used by the file provider extension.
    ///
    func credentials() async -> NSDictionary

    ///
    /// Get a server URL for the given local file provider item.
    ///
    func itemServerPath(identifier: NSFileProviderItemIdentifier) async -> NSString?
}
