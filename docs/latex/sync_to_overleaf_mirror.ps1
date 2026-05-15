<#
.SYNOPSIS
Sync this LaTeX manuscript folder into the flat Overleaf mirror checkout.

.DESCRIPTION
The source manuscript lives in docs\latex inside the MEA Thermodynamics
repository. The mirror checkout is a separate Git repository connected to
Overleaf, and its root should contain the manuscript files directly, not a
nested latex folder.

This script intentionally excludes itself so the mirror remains a clean Overleaf
project. Use -WhatIf to preview the sync without writing to the mirror.
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$MirrorRoot = $env:MEA_OVERLEAF_MIRROR,
    [string[]]$AssetDirectories = @('Figures', 'out', 'sections', 'styles', 'thumbnails'),
    [switch]$CleanBuildFiles
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($MirrorRoot)) {
    throw 'Set MEA_OVERLEAF_MIRROR or pass -MirrorRoot to the Overleaf mirror checkout.'
}

function Resolve-RequiredPath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Label does not exist: $Path"
    }

    return (Resolve-Path -LiteralPath $Path).Path
}

function Invoke-RobocopyChecked {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination,
        [string[]]$ExtraArgs = @()
    )

    $args = @(
        $Source,
        $Destination,
        '/E',
        '/R:2',
        '/W:1',
        '/NFL',
        '/NDL',
        '/NJH',
        '/NJS',
        '/XD',
        '.git',
        '__pycache__',
        '.pytest_cache',
        '/XF',
        (Split-Path -Leaf $PSCommandPath),
        '*.aux',
        '*.bbl',
        '*.blg',
        '*.fdb_latexmk',
        '*.fls',
        '*.log',
        '*.out',
        '*.synctex.gz',
        '*.xdv'
    ) + $ExtraArgs

    if ($WhatIfPreference) {
        $args += '/L'
    }

    & robocopy @args | Out-Host
    $exitCode = $LASTEXITCODE
    if ($exitCode -gt 7) {
        throw "robocopy failed with exit code $exitCode while syncing '$Source' to '$Destination'"
    }
}

$latexSourcePath = Resolve-RequiredPath -Path $PSScriptRoot -Label 'LaTeX source folder'
$mirrorRootPath = Resolve-RequiredPath -Path $MirrorRoot -Label 'Mirror checkout root'
$scriptName = Split-Path -Leaf $PSCommandPath

if (-not (Test-Path -LiteralPath (Join-Path $mirrorRootPath '.git'))) {
    throw "Mirror root is not a Git checkout: $mirrorRootPath"
}

Write-Host "Source LaTeX folder: $latexSourcePath"
Write-Host "Mirror root: $mirrorRootPath"

$latexFiles = Get-ChildItem -LiteralPath $latexSourcePath -File -Force |
    Where-Object { $_.Name -ne $scriptName }

foreach ($file in $latexFiles) {
    $destination = Join-Path $mirrorRootPath $file.Name
    if ($file.LinkType -eq 'HardLink' -and (Test-Path -LiteralPath $destination)) {
        Write-Host "Skipping file already linked to mirror: $($file.FullName)"
        continue
    }

    if ($PSCmdlet.ShouldProcess($destination, "Copy $($file.FullName)")) {
        Copy-Item -LiteralPath $file.FullName -Destination $destination -Force
    }
}

foreach ($assetDirectory in $AssetDirectories) {
    $sourceAssetPath = Join-Path $latexSourcePath $assetDirectory
    if (-not (Test-Path -LiteralPath $sourceAssetPath)) {
        Write-Warning "Skipping missing asset directory: $sourceAssetPath"
        continue
    }

    $destinationAssetPath = Join-Path $mirrorRootPath $assetDirectory
    $sourceAssetItem = Get-Item -LiteralPath $sourceAssetPath -Force
    $sourceAssetTarget = if ($sourceAssetItem.Target) {
        [string]$sourceAssetItem.Target
    } else {
        (Resolve-Path -LiteralPath $sourceAssetPath).Path
    }
    $resolvedDestinationAssetPath = if (Test-Path -LiteralPath $destinationAssetPath) {
        (Resolve-Path -LiteralPath $destinationAssetPath).Path
    } else {
        $destinationAssetPath
    }

    if ($sourceAssetTarget -eq $resolvedDestinationAssetPath) {
        Write-Host "Skipping asset directory already linked to mirror: $sourceAssetPath"
        continue
    }

    if ($PSCmdlet.ShouldProcess($destinationAssetPath, "Sync asset directory $sourceAssetPath")) {
        Invoke-RobocopyChecked -Source $sourceAssetPath -Destination $destinationAssetPath
    }
}

if ($CleanBuildFiles) {
    $buildPatterns = @(
        '*.abs',
        '*.aux',
        '*.bbl',
        '*.blg',
        '*.fdb_latexmk',
        '*.fls',
        '*.log',
        '*.out',
        '*.synctex.gz',
        '*.xdv'
    )

    foreach ($pattern in $buildPatterns) {
        $buildFiles = Get-ChildItem -LiteralPath $mirrorRootPath -Filter $pattern -File -ErrorAction SilentlyContinue
        foreach ($buildFile in $buildFiles) {
            if ($PSCmdlet.ShouldProcess($buildFile.FullName, 'Remove LaTeX build artifact')) {
                Remove-Item -LiteralPath $buildFile.FullName -Force
            }
        }
    }
}

Write-Host 'LaTeX mirror sync complete.'
