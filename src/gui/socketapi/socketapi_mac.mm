/*
 * SPDX-FileCopyrightText: 2022 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: GPL-2.0-or-later
 */

#import <Cocoa/Cocoa.h>
#import <QUrl>

#include "application.h"

namespace OCC
{

QUrl socketApiSocketUrl()
{
    NSString *appGroupId = @MACOS_APP_GROUP;
    NSURL *container = [[NSFileManager defaultManager] containerURLForSecurityApplicationGroupIdentifier:appGroupId];
    NSURL *socket = [container URLByAppendingPathComponent:@"s" isDirectory:NO];

    return QUrl::fromNSURL(socket);
}

}
