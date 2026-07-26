# SPDX-FileCopyrightText: 2020 Nextcloud GmbH and Nextcloud contributors
# SPDX-License-Identifier: GPL-2.0-or-later
if(CMAKE_SIZEOF_VOID_P MATCHES 4)
    set(MSI_BUILD_ARCH x86)
else()
    set(MSI_BUILD_ARCH x64)
endif()

string(SUBSTRING ${GIT_SHA1} 0 7 GIT_REVISION)

set(VERSION "${MIRALL_VERSION_MAJOR}.${MIRALL_VERSION_MINOR}.${MIRALL_VERSION_PATCH}.${MIRALL_VERSION_BUILD}")

set(MSI_INSTALLER_FILENAME
    "${WINDOWS_INSTALLER_BASENAME}-${MSI_BUILD_ARCH}-${MIRALL_VERSION}${MIRALL_VERSION_SUFFIX}.msi")

configure_file(RegistryCleanup.vbs.in ${CMAKE_CURRENT_BINARY_DIR}/RegistryCleanup.vbs)
configure_file(OEM.wxi.in ${CMAKE_CURRENT_BINARY_DIR}/OEM.wxi)
configure_file(collect-transform.xsl.in ${CMAKE_CURRENT_BINARY_DIR}/collect-transform.xsl)
configure_file(make-msi.bat.in ${CMAKE_CURRENT_BINARY_DIR}/make-msi.bat)

install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/OEM.wxi
        ${CMAKE_CURRENT_BINARY_DIR}/collect-transform.xsl
        ${CMAKE_CURRENT_BINARY_DIR}/make-msi.bat
        EnsureACL.js
        Platform.wxi
        Nextcloud.wxs
        ${CMAKE_CURRENT_BINARY_DIR}/RegistryCleanup.vbs
        RegistryCleanupCustomAction.wxs
        gui/banner.bmp
        gui/dialog.bmp
    DESTINATION msi/)
