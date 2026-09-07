# tools\Install-Toolchain.ps1
#
# QVS step 2: install the missing toolchain via winget.
#
# Derived from dev_reports\bootstrap.txt on 2026-09-07, which found this machine has
# only VS Code and winget. Everything else in the QVS toolchain is absent.
#
# MUST BE RUN FROM AN ELEVATED POWERSHELL (Run as administrator). winget itself does
# not always need elevation, but several of these package installers do, and being
# prompted halfway through a batch is worse than starting elevated.
#
# Claude Code is deliberately NOT installed here. It has its own non-admin installer
# and installing it via winget as well would leave two copies in different locations
# with PATH deciding which one runs - a known and silent version-mismatch trap.
#
# Run it with:
#   powershell -ExecutionPolicy Bypass -File ".\tools\Install-Toolchain.ps1"
#
# Everything is logged to dev_reports\install_toolchain.txt for Claude to read.

[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$ReportDir = Join-Path $RepoRoot 'dev_reports'
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}
$OutFile = Join-Path $ReportDir 'install_toolchain.txt'

$L = New-Object System.Collections.ArrayList
function Add-Line([string] $Text) { [void] $L.Add($Text); Write-Host $Text }

Add-Line 'QVS TOOLCHAIN INSTALL'
Add-Line "WHEN : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line "USER : $env:USERNAME"

# Elevation check. Not fatal - winget may still succeed - but recorded so that a
# later failure can be attributed rather than guessed at.
$identity  = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
$elevated  = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Add-Line "ELEVATED : $elevated"
if (-not $elevated) {
    Add-Line 'WARNING: not running as administrator. Some installers may prompt or fail.'
}
Add-Line ('-' * 78)

if (-not (Get-Command 'winget' -ErrorAction SilentlyContinue)) {
    Add-Line 'FATAL: winget not found. Cannot continue.'
    Set-Content -Path $OutFile -Value $L.ToArray() -Encoding UTF8
    exit 1
}

# Package IDs are exact (-e) so winget cannot silently resolve to a similarly named
# package. Python is pinned to 3.12 per D-010: one version locally, in CI and in
# Docker, because version drift between them is a pure time cost on a deadline.
$packages = @(
    @{ Id = 'Git.Git';             Label = 'Git for Windows' },
    @{ Id = 'Python.Python.3.12';  Label = 'Python 3.12 (with the py launcher)' },
    @{ Id = 'GitHub.cli';          Label = 'GitHub CLI (gh)' },
    @{ Id = 'Docker.DockerDesktop'; Label = 'Docker Desktop' }
)

foreach ($p in $packages) {
    Add-Line ''
    Add-Line "=== $($p.Label)  [$($p.Id)] ==="
    try {
        $output = winget install --id $p.Id -e `
                    --accept-package-agreements `
                    --accept-source-agreements 2>&1 | Out-String
        Add-Line $output.TrimEnd()
        Add-Line "exit code: $LASTEXITCODE"
    }
    catch {
        Add-Line "EXCEPTION: $($_.Exception.Message)"
    }
}

Add-Line ''
Add-Line ('-' * 78)
Add-Line 'INSTALL PHASE COMPLETE'
Add-Line ''
Add-Line 'NEXT, AND IN THIS ORDER:'
Add-Line '  1. Close this terminal completely. PATH changes are not picked up by a'
Add-Line '     terminal that was already open when the installers ran.'
Add-Line '  2. Open a NEW, NON-ELEVATED PowerShell and install Claude Code:'
Add-Line '       irm https://claude.ai/install.ps1 | iex'
Add-Line '  3. Close that terminal too, then open a third one and re-run:'
Add-Line '       .\tools\Bootstrap.ps1'
Add-Line '  4. Docker Desktop may require a reboot before the docker command works.'
Add-Line '     That is expected and is not needed until the end of Sprint A.'

Set-Content -Path $OutFile -Value $L.ToArray() -Encoding UTF8
Write-Host ''
Write-Host "Log written to: $OutFile"
