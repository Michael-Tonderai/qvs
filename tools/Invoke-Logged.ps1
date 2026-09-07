# tools\Invoke-Logged.ps1
#
# QVS command runner. Runs a command from the repo root and writes everything it
# produced to an artefact under dev_reports\, which Claude then reads directly.
#
# Why this exists: Sir Ton never pastes terminal output. Every command's output lands
# in a file on disk and Claude opens it. This is the only sanctioned way to run a
# command whose result Claude needs to see.
#
# QUIET BY DEFAULT (revised 2026-09-07): the console gets a one-line verdict and the
# artefact path. Nothing else. An earlier version echoed every captured line, which
# defeats the purpose - if the output is going to a file for Claude to read, there is
# no reason to also flood the terminal with it. Pass -Echo when you genuinely want to
# watch a long command progress live.
#
# STREAMING: output is appended to the artefact as it is produced, not buffered and
# written at the end. A hung or interrupted command still leaves a readable artefact
# showing what was attempted and how far it got. STATUS in the header tells Claude
# whether the run COMPLETED, FAILED, or is still RUNNING.
#
# Why $PSScriptRoot rather than a hard-coded path: the repo root is derived at run
# time, so the tooling survives the folder being renamed or moved, and the absolute
# path appears nowhere inside it.
#
# Usage (from the repo root):
#   .\tools\Invoke-Logged.ps1 'git status' 'git_status'
#   .\tools\Invoke-Logged.ps1 '.\.venv\Scripts\python.exe manage.py check' 'django_check'
#   .\tools\Invoke-Logged.ps1 '.\.venv\Scripts\pip.exe install -r requirements.txt' 'pip_install' -Echo
#
# The .txt extension is added automatically. Artefacts are overwritten on each run, so
# give a distinct name when comparing a before and an after.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string] $Command,

    [Parameter(Mandatory = $true, Position = 1)]
    [string] $Artefact,

    # Mirror output to the console as well. Off by default.
    [switch] $Echo
)

$ErrorActionPreference = 'Continue'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$ReportDir = Join-Path $RepoRoot 'dev_reports'

if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}

if ($Artefact -notmatch '\.txt$') { $Artefact = "$Artefact.txt" }
$OutFile = Join-Path $ReportDir $Artefact

# Header written immediately, so the artefact exists from the first second
Set-Content -Path $OutFile -Encoding UTF8 -Value @(
    "COMMAND  : $Command",
    "WHEN     : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "REPOROOT : $RepoRoot",
    'STATUS   : RUNNING',
    ('-' * 78)
)

$script:produced = $false
$verdict = 'FAILED'

Push-Location $RepoRoot
try {
    $global:LASTEXITCODE = 0

    # 2>&1 folds stderr into the stream so failures are captured, not lost
    Invoke-Expression $Command 2>&1 | ForEach-Object {
        $text = ($_ | Out-String).TrimEnd()
        if ($text.Length -gt 0) {
            Add-Content -Path $OutFile -Value $text -Encoding UTF8
            if ($Echo) { Write-Host $text }
            $script:produced = $true
        }
    }

    if (-not $script:produced) {
        Add-Content -Path $OutFile -Value '(no output)' -Encoding UTF8
    }

    $code = $LASTEXITCODE
    Add-Content -Path $OutFile -Encoding UTF8 -Value @(
        ('-' * 78),
        "EXITCODE : $code",
        'STATUS   : COMPLETED'
    )
    $verdict = if ($code -eq 0) { 'OK' } else { "NON-ZERO EXIT ($code)" }
}
catch {
    Add-Content -Path $OutFile -Encoding UTF8 -Value @(
        ('-' * 78),
        "EXCEPTION: $($_.Exception.Message)",
        'STATUS   : FAILED (terminating error - command did not complete)'
    )
    $verdict = 'FAILED (terminating error)'
}
finally {
    Pop-Location
}

# Two lines. That is the whole console contract.
Write-Host "$verdict  <  $Command"
Write-Host "  -> dev_reports\$Artefact"
