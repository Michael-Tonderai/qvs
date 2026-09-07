# tools\Setup-Venv.ps1
#
# QVS: create the virtual environment and install the toolchain into it.
#
# This is the ONLY place in the project where `py` is used. Everything afterwards
# goes through .\.venv\Scripts\python.exe explicitly (D-011), which is what removes
# "which interpreter am I on" as a question that can be asked - and what makes the
# Microsoft Store python.exe alias stub unreachable by accident.
#
# The interpreter is requested as -3.12 specifically rather than by default, so that
# installing a newer Python later cannot silently change what this project builds on
# (D-010).
#
# Output streams to the artefact line by line rather than being buffered, so an
# interrupted pip install still leaves a readable record of how far it got.
#
# Idempotent: if .venv already exists the script reports it and reinstalls
# dependencies rather than recreating the environment. Pass -Recreate to delete and
# rebuild from scratch.
#
# Run it with:
#   .\tools\Setup-Venv.ps1

[CmdletBinding()]
param(
    [switch] $Recreate
)

$ErrorActionPreference = 'Continue'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$ReportDir = Join-Path $RepoRoot 'dev_reports'
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}
$OutFile = Join-Path $ReportDir 'setup_venv.txt'

# Header written immediately so the artefact exists from the first second
Set-Content -Path $OutFile -Encoding UTF8 -Value @(
    'QVS VIRTUAL ENVIRONMENT SETUP',
    "WHEN     : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "REPOROOT : $RepoRoot",
    'STATUS   : RUNNING',
    ('-' * 78)
)
function Log([string] $t) { Add-Content -Path $OutFile -Value $t -Encoding UTF8 }
function LogHead([string] $t) { Log ''; Log "=== $t ===" }

$VenvDir = Join-Path $RepoRoot '.venv'
$VenvPy  = Join-Path $VenvDir 'Scripts\python.exe'
$verdict = 'FAILED'

Push-Location $RepoRoot
try {
    # --------------------------------------------------------------- launcher ---
    LogHead 'PYTHON LAUNCHER'
    if (-not (Get-Command 'py' -ErrorAction SilentlyContinue)) {
        Log 'FATAL: the py launcher is not on PATH. Cannot create the environment.'
        throw 'py launcher missing'
    }
    Log ((py -0p 2>&1 | Out-String).TrimEnd())

    # ------------------------------------------------------------ create/reuse ---
    LogHead 'ENVIRONMENT'
    if ($Recreate -and (Test-Path $VenvDir)) {
        Log 'Recreate requested - removing the existing .venv'
        Remove-Item -Path $VenvDir -Recurse -Force
    }

    if (Test-Path $VenvPy) {
        Log '.venv already exists - reusing it and reinstalling dependencies.'
    }
    else {
        Log 'Creating .venv on Python 3.12 ...'
        $create = (py -3.12 -m venv .venv 2>&1 | Out-String).TrimEnd()
        if ($create) { Log $create }

        if (-not (Test-Path $VenvPy)) {
            Log 'FATAL: .venv\Scripts\python.exe was not created.'
            throw 'venv creation failed'
        }
        Log 'Created.'
    }

    Log "interpreter : $VenvPy"
    Log "version     : $((& $VenvPy --version 2>&1 | Out-String).Trim())"

    # ------------------------------------------------------------ pip upgrade ---
    # Done through `python -m pip` rather than pip.exe: on Windows, pip cannot
    # replace its own running executable, and `-m pip` is the documented way round it.
    LogHead 'PIP UPGRADE'
    & $VenvPy -m pip install --upgrade pip 2>&1 | ForEach-Object {
        $line = ($_ | Out-String).TrimEnd()
        if ($line) { Log $line }
    }

    # --------------------------------------------------------------- install ---
    LogHead 'INSTALL requirements-dev.txt'
    & $VenvPy -m pip install -r requirements-dev.txt 2>&1 | ForEach-Object {
        $line = ($_ | Out-String).TrimEnd()
        if ($line) { Log $line }
    }

    # ---------------------------------------------------------------- verify ---
    LogHead 'INSTALLED PACKAGES'
    Log ((& $VenvPy -m pip list 2>&1 | Out-String).TrimEnd())

    LogHead 'TOOL VERSIONS (from inside the venv)'
    foreach ($probe in @(
        @{ Label = 'django'; Args = @('-c', 'import django; print(django.get_version())') },
        @{ Label = 'pytest'; Args = @('-m', 'pytest', '--version') },
        @{ Label = 'ruff';   Args = @('-m', 'ruff', '--version') },
        @{ Label = 'bandit'; Args = @('-m', 'bandit', '--version') }
    )) {
        try {
            $v = (& $VenvPy @($probe.Args) 2>&1 | Out-String).Trim()
            Log "$($probe.Label) : $v"
        }
        catch {
            Log "$($probe.Label) : ERROR - $($_.Exception.Message)"
        }
    }

    Log ''
    Log ('-' * 78)
    Log 'STATUS   : COMPLETED'
    $verdict = 'VENV READY'
}
catch {
    Log ''
    Log ('-' * 78)
    Log "EXCEPTION: $($_.Exception.Message)"
    Log 'STATUS   : FAILED'
    $verdict = "FAILED  $($_.Exception.Message)"
}
finally {
    Pop-Location
}

Write-Host $verdict
Write-Host '  -> dev_reports\setup_venv.txt'
