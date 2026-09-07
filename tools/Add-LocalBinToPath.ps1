# tools\Add-LocalBinToPath.ps1
#
# QVS: put the Claude Code native install directory on the user PATH.
#
# The native installer places claude.exe at %USERPROFILE%\.local\bin but does not
# always add that directory to PATH, so the `claude` command does not resolve.
# This script adds it, once, to the USER scope only.
#
# WHY NOT THE ONE-LINE VERSION: the common idiom is
#     [Environment]::SetEnvironmentVariable('Path', $env:Path + ';...', 'User')
# and it is wrong. $env:Path is the MERGED machine-plus-user path. Writing it back
# into User scope copies every machine-level entry into the user profile, so PATH
# grows a duplicate of itself on each run and machine-level changes stop taking
# effect properly. This script reads the User scope explicitly and appends one entry.
#
# Idempotent: running it twice does nothing the second time.
#
# QUIET (revised 2026-09-07): two lines to the console, everything else to the
# artefact. The first version echoed its whole report, which is exactly the terminal
# noise the dev_reports\ method exists to avoid.
#
# Run it with:
#   .\tools\Add-LocalBinToPath.ps1

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$ReportDir = Join-Path $RepoRoot 'dev_reports'
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}
$OutFile = Join-Path $ReportDir 'path_fix.txt'

$L = New-Object System.Collections.ArrayList
function Add-Line([string] $Text) { [void] $L.Add($Text) }
function Save { Set-Content -Path $OutFile -Value $L.ToArray() -Encoding UTF8 }

Add-Line 'QVS PATH FIX - Claude Code native install directory'
Add-Line "WHEN : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line ('-' * 78)

$TargetDir = Join-Path $env:USERPROFILE '.local\bin'
$ClaudeExe = Join-Path $TargetDir 'claude.exe'

Add-Line "TARGET DIR : $TargetDir"
Add-Line "DIR EXISTS : $(Test-Path $TargetDir)"
Add-Line "claude.exe : $(Test-Path $ClaudeExe)"

if (-not (Test-Path $ClaudeExe)) {
    Add-Line ''
    Add-Line 'ABORTED: claude.exe not found at the expected location. Nothing changed.'
    Save
    Write-Host 'ABORTED  claude.exe not found - nothing changed'
    Write-Host '  -> dev_reports\path_fix.txt'
    exit 1
}

# USER scope only - see the note at the top of this file
$UserPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($null -eq $UserPath) { $UserPath = '' }

Add-Line ''
Add-Line 'USER PATH BEFORE:'
if ([string]::IsNullOrWhiteSpace($UserPath)) {
    Add-Line '  (empty)'
}
else {
    foreach ($entry in ($UserPath -split ';' | Where-Object { $_ -ne '' })) {
        Add-Line "  $entry"
    }
}

# Normalised comparison, so a trailing slash or different casing is not seen as new
$existing = @($UserPath -split ';' | Where-Object { $_ -ne '' } |
              ForEach-Object { $_.TrimEnd('\').ToLowerInvariant() })
$needle   = $TargetDir.TrimEnd('\').ToLowerInvariant()

Add-Line ''
if ($existing -contains $needle) {
    $verdict = 'ALREADY PRESENT  no change made'
    Add-Line 'RESULT: already present. No change made.'
}
else {
    $NewPath = if ([string]::IsNullOrWhiteSpace($UserPath)) { $TargetDir }
               else { $UserPath.TrimEnd(';') + ';' + $TargetDir }

    [Environment]::SetEnvironmentVariable('Path', $NewPath, 'User')

    # Also update the CURRENT session so claude resolves without reopening the terminal
    $env:Path = $env:Path.TrimEnd(';') + ';' + $TargetDir

    $verdict = 'APPENDED  .local\bin added to user PATH'
    Add-Line "RESULT: appended '$TargetDir' to the USER PATH."
    Add-Line 'The current session was also updated.'
}

Add-Line ''
Add-Line 'VERIFY:'
$cmd = Get-Command 'claude' -ErrorAction SilentlyContinue
if ($null -eq $cmd) {
    Add-Line '  claude : NOT RESOLVING in this session - open a new terminal and retry.'
    $verdict = "$verdict (but claude still not resolving)"
}
else {
    Add-Line "  claude : $($cmd.Source)"
    try   { Add-Line "  version: $((& claude --version 2>&1 | Out-String).Trim())" }
    catch { Add-Line "  version: ERROR - $($_.Exception.Message)" }
}

Add-Line ''
Add-Line ('-' * 78)
Add-Line 'END'
Save

Write-Host $verdict
Write-Host '  -> dev_reports\path_fix.txt'
