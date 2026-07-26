# SPDX-FileCopyrightText: 2026 SeaByte
# SPDX-License-Identifier: GPL-2.0-or-later

[CmdletBinding()]
param(
    [string]$BuildRoot = "",
    [switch]$SkipDependencyInstall,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
Set-StrictMode -Version Latest

if ($env:OS -ne "Windows_NT") {
    throw "SeaByte Windows packages must be built on Windows."
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if ([string]::IsNullOrWhiteSpace($BuildRoot)) {
    $BuildRoot = Join-Path $RepoRoot ".build\windows"
}
$BuildRoot = [System.IO.Path]::GetFullPath($BuildRoot)
$CraftMaster = Join-Path $BuildRoot "CraftMaster"
$CraftTarget = "windows-msvc2022_64-cl"
$CraftConfig = Join-Path $RepoRoot "craftmaster.ini"
$DistDir = Join-Path $RepoRoot "dist\windows"

foreach ($Command in @("git", "python", "cmake")) {
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        throw "Required command is missing: $Command"
    }
}

python (Join-Path $RepoRoot "tools\branding\check_branding.py")
if ($LASTEXITCODE -ne 0) {
    throw "SeaByte branding checks failed."
}

New-Item -ItemType Directory -Force -Path $BuildRoot, $DistDir | Out-Null

if (-not (Test-Path (Join-Path $CraftMaster "CraftMaster.py"))) {
    git clone --depth=1 https://invent.kde.org/packaging/craftmaster.git $CraftMaster
    if ($LASTEXITCODE -ne 0) {
        throw "Could not clone KDE CraftMaster."
    }
}

function Invoke-Craft {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & python (Join-Path $CraftMaster "CraftMaster.py") --config $CraftConfig --target $CraftTarget -c @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "KDE Craft failed: $($Arguments -join ' ')"
    }
}

if (-not $SkipDependencyInstall) {
    Invoke-Craft --add-blueprint-repository "https://github.com/nextcloud/craft-blueprints-kde.git|stable-33.0|"
    Invoke-Craft --add-blueprint-repository "https://github.com/nextcloud/desktop-client-blueprints.git|stable-33.0|"
    Invoke-Craft craft
    Invoke-Craft --install-deps nextcloud-client
}

$Candle = Get-Command candle.exe -ErrorAction SilentlyContinue
if (-not $Candle) {
    $Candle = Get-ChildItem "${env:ProgramFiles(x86)}" -Recurse -Filter candle.exe -ErrorAction SilentlyContinue |
        Select-Object -First 1
}
if (-not $Candle -and -not $SkipDependencyInstall -and (Get-Command choco.exe -ErrorAction SilentlyContinue)) {
    & choco.exe install wixtoolset --yes --no-progress
    if ($LASTEXITCODE -ne 0) {
        throw "Could not install WiX Toolset v3."
    }
    $Candle = Get-ChildItem "${env:ProgramFiles(x86)}" -Recurse -Filter candle.exe -ErrorAction SilentlyContinue |
        Select-Object -First 1
}
if (-not $Candle) {
    throw "WiX Toolset v3 candle.exe was not found."
}
$CandlePath = if ($Candle.PSObject.Properties.Name -contains "Source") { $Candle.Source } else { $Candle.FullName }
$env:WIX = Split-Path (Split-Path $CandlePath -Parent) -Parent

Invoke-Craft --buildtype Release --src-dir $RepoRoot --options "nextcloud-client.buildTests=True" nextcloud-client

$ClientBuild = Join-Path $RepoRoot "$CraftTarget\build\nextcloud-client\work\build"
if (-not (Test-Path $ClientBuild)) {
    throw "Expected client build directory not found: $ClientBuild"
}

if (-not $SkipTests) {
    & ctest --test-dir $ClientBuild --output-on-failure --timeout 300
    if ($LASTEXITCODE -ne 0) {
        throw "C++ test suite failed."
    }
}

$Image = Get-ChildItem (Join-Path $RepoRoot "$CraftTarget\build\nextcloud-client") -Directory -Filter "image-Release-*" |
    Where-Object { Test-Path (Join-Path $_.FullName "bin\SeaByteCloud.exe") } |
    Select-Object -First 1
if (-not $Image) {
    throw "KDE Craft image containing bin\SeaByteCloud.exe was not found."
}

$SignatureLabel = "unsigned"
$CertificateSha1 = $env:SEABYTE_WINDOWS_CERT_SHA1
if (-not [string]::IsNullOrWhiteSpace($CertificateSha1)) {
    $SignTool = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Recurse -Filter signtool.exe |
        Sort-Object FullName -Descending |
        Select-Object -First 1
    if (-not $SignTool) {
        throw "SEABYTE_WINDOWS_CERT_SHA1 is set, but signtool.exe was not found."
    }
    $TimestampUrl = if ($env:SEABYTE_WINDOWS_TIMESTAMP_URL) {
        $env:SEABYTE_WINDOWS_TIMESTAMP_URL
    } else {
        "http://timestamp.digicert.com"
    }
    $Signable = Get-ChildItem $Image.FullName -Recurse -File |
        Where-Object { $_.Extension -in @(".exe", ".dll") }
    foreach ($File in $Signable) {
        & $SignTool.FullName sign /sha1 $CertificateSha1 /fd SHA256 /tr $TimestampUrl /td SHA256 $File.FullName
        if ($LASTEXITCODE -ne 0) {
            throw "Authenticode signing failed: $($File.FullName)"
        }
    }
    $SignatureLabel = "signed"
}

$MsiBuildDir = Join-Path $Image.FullName "msi"
$MakeMsi = Join-Path $MsiBuildDir "make-msi.bat"
if (-not (Test-Path $MakeMsi)) {
    throw "Installed WiX MSI support files were not found: $MakeMsi"
}

Push-Location $MsiBuildDir
try {
    & cmd.exe /D /C "`"$MakeMsi`" `"$($Image.FullName)`""
    if ($LASTEXITCODE -ne 0) {
        throw "WiX MSI creation failed."
    }
} finally {
    Pop-Location
}

$Msi = Get-ChildItem $MsiBuildDir -File -Filter "SeaByte-Cloud-Setup-x64-*.msi" |
    Sort-Object LastWriteTimeUtc -Descending |
    Select-Object -First 1
if (-not $Msi) {
    throw "SeaByte MSI was not created."
}

if ($SignatureLabel -eq "signed") {
    & $SignTool.FullName sign /sha1 $CertificateSha1 /fd SHA256 /tr $TimestampUrl /td SHA256 $Msi.FullName
    if ($LASTEXITCODE -ne 0) {
        throw "MSI Authenticode signing failed."
    }
}

$BaseName = [System.IO.Path]::GetFileNameWithoutExtension($Msi.Name)
$FinalMsi = Join-Path $DistDir "$BaseName-$SignatureLabel.msi"
Copy-Item $Msi.FullName $FinalMsi -Force

$GitSha = (git -C $RepoRoot rev-parse HEAD).Trim()
$Metadata = [ordered]@{
    product = "SeaByte Cloud"
    upstream_version = "33.0.7"
    brand_revision = if ($env:SEABYTE_RELEASE_REVISION) { $env:SEABYTE_RELEASE_REVISION } else { "1" }
    architecture = "x64"
    signature = $SignatureLabel
    git_sha = $GitSha
}
$Metadata | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $DistDir "build-metadata.json")

$Hashes = Get-ChildItem $DistDir -File |
    Where-Object { $_.Name -ne "SHA256SUMS" } |
    Sort-Object Name |
    ForEach-Object {
        $Hash = (Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLowerInvariant()
        "$Hash  $($_.Name)"
    }
$Hashes | Set-Content -Encoding ascii (Join-Path $DistDir "SHA256SUMS")
Write-Host "Created $FinalMsi"
