# SPDX-FileCopyrightText: 2026 SeaByte
# SPDX-License-Identifier: GPL-2.0-or-later

# Version of the upstream source baseline. The branding tests verify that this
# matches VERSION.cmake.
set(SEABYTE_UPSTREAM_VERSION "33.0.7")

# SeaByte packaging revision. Override with
# -DSEABYTE_RELEASE_REVISION=<integer> or the environment variable of the same
# name.
if(NOT DEFINED SEABYTE_RELEASE_REVISION)
    if(DEFINED ENV{SEABYTE_RELEASE_REVISION} AND NOT "$ENV{SEABYTE_RELEASE_REVISION}" STREQUAL "")
        set(SEABYTE_RELEASE_REVISION "$ENV{SEABYTE_RELEASE_REVISION}")
    else()
        set(SEABYTE_RELEASE_REVISION "1")
    endif()
endif()
set(SEABYTE_RELEASE_REVISION "${SEABYTE_RELEASE_REVISION}" CACHE STRING "SeaByte packaging revision")

set(MIRALL_VERSION_SUFFIX "-seabyte.${SEABYTE_RELEASE_REVISION}" CACHE STRING "SeaByte version suffix" FORCE)

