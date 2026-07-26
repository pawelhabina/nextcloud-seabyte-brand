# SPDX-FileCopyrightText: 2026 SeaByte
# SPDX-License-Identifier: GPL-2.0-or-later

# Central SeaByte Cloud OEM configuration.
#
# Every public option can be overridden with a CMake cache argument, for
# example `-DDEFAULT_SERVER_URL=https://staging.example`, or with an
# environment variable of the same name when no CMake value was supplied.

function(seabyte_cache_string variable default_value description)
    if(NOT DEFINED ${variable})
        if(DEFINED ENV{${variable}} AND NOT "$ENV{${variable}}" STREQUAL "")
            set(_seabyte_value "$ENV{${variable}}")
        else()
            set(_seabyte_value "${default_value}")
        endif()
        set(${variable} "${_seabyte_value}" CACHE STRING "${description}" FORCE)
    else()
        set(${variable} "${${variable}}" CACHE STRING "${description}" FORCE)
    endif()
endfunction()

function(seabyte_cache_bool variable default_value description)
    if(NOT DEFINED ${variable})
        if(DEFINED ENV{${variable}} AND NOT "$ENV{${variable}}" STREQUAL "")
            set(_seabyte_value "$ENV{${variable}}")
        else()
            set(_seabyte_value "${default_value}")
        endif()
        set(${variable} "${_seabyte_value}" CACHE BOOL "${description}" FORCE)
    else()
        set(${variable} "${${variable}}" CACHE BOOL "${description}" FORCE)
    endif()
endfunction()

seabyte_cache_string(BRAND_DISPLAY_NAME "SeaByte Cloud" "User-visible application name")
seabyte_cache_string(BRAND_SHORT_NAME "SeaByte" "Short user-visible brand name")
seabyte_cache_string(BRAND_FOLDER_NAME "seabyte.pl" "Default local sync folder name")
seabyte_cache_string(BRAND_COMPANY "SeaByte" "Publisher and vendor name")
seabyte_cache_string(BRAND_DOMAIN "seabyte.pl" "Brand DNS domain")
seabyte_cache_string(BRAND_WEBSITE "https://seabyte.pl" "Brand website")
seabyte_cache_string(DEFAULT_SERVER_URL "https://cloud.seabyte.pl" "Pre-filled server URL")
seabyte_cache_string(BRAND_CONFIG_NAME "seabytecloud" "Private settings and data namespace")
seabyte_cache_string(BRAND_LOCAL_EDIT_URI_SCHEME "nc" "Server-compatible local-edit URI scheme")
seabyte_cache_string(BRAND_URI_HANDLER_ALIAS "seabytecloud" "SeaByte-specific URL handler alias")

seabyte_cache_string(WINDOWS_EXECUTABLE_NAME "SeaByteCloud" "Windows executable base name")
seabyte_cache_string(WINDOWS_APP_ID "pl.seabyte.cloud" "Windows AppUserModelID")
seabyte_cache_string(WINDOWS_INSTALLER_BASENAME "SeaByte-Cloud-Setup" "Windows installer file base name")

seabyte_cache_string(MACOS_BUNDLE_ID "pl.seabyte.cloud" "macOS main application bundle identifier")
seabyte_cache_string(MACOS_FILE_PROVIDER_BUNDLE_ID "pl.seabyte.cloud.fileprovider" "macOS File Provider bundle identifier")
seabyte_cache_string(MACOS_FILE_PROVIDER_UI_BUNDLE_ID "pl.seabyte.cloud.fileproviderui" "macOS File Provider UI bundle identifier")
seabyte_cache_string(MACOS_FINDER_EXTENSION_BUNDLE_ID "pl.seabyte.cloud.findersync" "macOS Finder Sync bundle identifier")
seabyte_cache_string(MACOS_APP_GROUP "group.pl.seabyte.cloud" "macOS application group")
seabyte_cache_string(MACOS_TEAM_ID "" "Apple Developer Team ID; intentionally empty for unsigned builds")

seabyte_cache_string(CUSTOM_UPDATE_URL "" "SeaByte updater feed URL")
seabyte_cache_bool(ENABLE_CUSTOM_UPDATER OFF "Build the updater against CUSTOM_UPDATE_URL")
seabyte_cache_bool(ALLOW_CUSTOM_SERVER ON "Allow users to edit the pre-filled server URL")

include("${CMAKE_CURRENT_LIST_DIR}/version.cmake")

# Public application identity.
set(APPLICATION_NAME "${BRAND_DISPLAY_NAME}")
set(APPLICATION_SHORTNAME "${BRAND_SHORT_NAME}")
set(APPLICATION_EXECUTABLE "${WINDOWS_EXECUTABLE_NAME}")
set(APPLICATION_CONFIG_NAME "${BRAND_CONFIG_NAME}")
set(APPLICATION_DOMAIN "${BRAND_DOMAIN}")
set(APPLICATION_VENDOR "${BRAND_COMPANY}")
set(APPLICATION_HELP_URL "${BRAND_WEBSITE}" CACHE STRING "SeaByte help URL" FORCE)
set(APPLICATION_ICON_NAME "SeaByte")
set(APPLICATION_ICON_SET "SVG")
set(APPLICATION_SERVER_URL "${DEFAULT_SERVER_URL}" CACHE STRING "Pre-filled SeaByte server URL" FORCE)
set(APPLICATION_SERVER_URL_ENFORCE OFF)
if(NOT ALLOW_CUSTOM_SERVER)
    set(APPLICATION_SERVER_URL_ENFORCE ON)
endif()
set(APPLICATION_REV_DOMAIN "${MACOS_BUNDLE_ID}")
set(APPLICATION_URI_HANDLER_SCHEME "${BRAND_LOCAL_EDIT_URI_SCHEME}")
set(APPLICATION_VIRTUALFILE_SUFFIX "seabyte" CACHE STRING "SeaByte virtual file suffix" FORCE)
set(LINUX_PACKAGE_SHORTNAME "seabyte-cloud")
set(LINUX_APPLICATION_ID "${APPLICATION_REV_DOMAIN}.desktop")
set(DEVELOPMENT_TEAM "${MACOS_TEAM_ID}" CACHE STRING "Apple Developer Team ID" FORCE)

# Never consume the official Nextcloud update channel. An empty custom feed
# always compiles the updater out.
set(APPLICATION_UPDATE_URL "${CUSTOM_UPDATE_URL}" CACHE STRING "SeaByte updater feed" FORCE)
set(BUILD_UPDATER "${ENABLE_CUSTOM_UPDATER}" CACHE BOOL "Build SeaByte updater" FORCE)
if(ENABLE_CUSTOM_UPDATER AND CUSTOM_UPDATE_URL STREQUAL "")
    message(FATAL_ERROR "ENABLE_CUSTOM_UPDATER requires a non-empty CUSTOM_UPDATE_URL")
endif()

# Avoid importing or migrating settings belonging to Nextcloud Desktop.
set(APPLICATION_DISPLAY_LEGACY_IMPORT_DIALOG OFF CACHE BOOL "Display legacy import dialog" FORCE)
set(DISABLE_ACCOUNT_MIGRATION ON CACHE BOOL "Disable account migration" FORCE)

# Brand colours and generated resources.
set(NEXTCLOUD_BACKGROUND_COLOR "#2c89b9" CACHE STRING "SeaByte primary colour" FORCE)
set(APPLICATION_WIZARD_HEADER_BACKGROUND_COLOR "#2c89b9" CACHE STRING "Wizard header background" FORCE)
set(APPLICATION_WIZARD_HEADER_TITLE_COLOR "#ffffff" CACHE STRING "Wizard header text" FORCE)
set(APPLICATION_WIZARD_USE_CUSTOM_LOGO ON CACHE BOOL "Use SeaByte wizard logo" FORCE)
set(WIN_SETUP_BITMAP_PATH "${CMAKE_SOURCE_DIR}/admin/win/nsi")
set(MAC_INSTALLER_BACKGROUND_FILE "${CMAKE_SOURCE_DIR}/admin/osx/installer-background.png" CACHE STRING "SeaByte macOS installer background" FORCE)

# Windows identities are deliberately unrelated to upstream values so both
# products can be installed side-by-side.
set(WIN_SHELLEXT_CONTEXT_MENU_GUID "{830322E5-6A2C-479B-9558-A9E8D24584E0}")
set(WIN_SHELLEXT_OVERLAY_GUID_ERROR "{A2D60418-8B23-467B-8C59-9DAE4FAC9647}")
set(WIN_SHELLEXT_OVERLAY_GUID_OK "{FAACB63E-64DC-406C-A8D0-B2C7CEA187ED}")
set(WIN_SHELLEXT_OVERLAY_GUID_OK_SHARED "{F5AF8550-7151-4AE0-848F-9BF14D82F4AD}")
set(WIN_SHELLEXT_OVERLAY_GUID_SYNC "{CCCFA00C-6DBE-432B-964B-84B4C816DB1A}")
set(WIN_SHELLEXT_OVERLAY_GUID_WARNING "{1A63043F-F4DA-4D69-A110-C8D10BCE0057}")
set(WIN_MSI_UPGRADE_CODE "ED5B76B7-440E-4EB4-AD96-E354A9CC3EFA")

set(CFAPI_SHELLEXT_APPID_REG "{CC1D6B1F-7250-44C8-B6CB-A6258604B171}")
set(CFAPI_SHELLEXT_CUSTOM_STATE_HANDLER_CLASS_ID "5933A4BC-3E47-4489-A863-14EF63C2AD83")
set(CFAPI_SHELLEXT_CUSTOM_STATE_HANDLER_CLASS_ID_REG "{${CFAPI_SHELLEXT_CUSTOM_STATE_HANDLER_CLASS_ID}}")
set(CFAPI_SHELLEXT_THUMBNAIL_HANDLER_CLASS_ID "E1FDB344-BA3C-4C36-91D7-2316C5121546")
set(CFAPI_SHELLEXT_THUMBNAIL_HANDLER_CLASS_ID_REG "{${CFAPI_SHELLEXT_THUMBNAIL_HANDLER_CLASS_ID}}")
