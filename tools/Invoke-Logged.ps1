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
# STDERR (fixed 2026-09-08, issue #5): the redirection must sit INSIDE the string
# that Invoke-Expression evaluates, not on the Invoke-Expression call. Written as
# `Invoke-Expression $Command 2>&1` the redirection binds to the cmdlet, while the
# native process spawned inside the evaluated string writes its stderr straight past
# it to the console - so a FAILING git command left a non-zero exit code beside a
# silent file, which is the least useful state this runner could be in. Written as
# `Invoke-Expression "$Command 2>&1"` the redirection is parsed as part of the native
# command's own pipeline and stderr is merged at the point it is produced.
#
# CONSTRAINT that follows from that: $Command must be a single command, not a
# pipeline. Appending 2>&1 to a string ending in a pipeline binds the redirection to
# the last element rather than to the command whose stderr is wanted. Every wrapped
# command in this project is a single git, gh or python invocation. If a pipeline is
# ever genuinely needed, wrap the producing command in its own call to this script.
#
# Merged stderr arrives as ErrorRecord objects, which is why they are rendered with
# ToString() rather than Out-String - Out-String wraps each line in the full
# PowerShell error apparatus (+ CategoryInfo, + FullyQualifiedErrorId), turning a
# one-line git message into six lines of formatting. Capturing the output and making
# it unreadable would not be a fix.
#
# ENCODING: artefacts are written as ASCII. PowerShell 5.1's -Encoding UTF8 emits a
# byte order mark, which put an invisible character at the head of every artefact -
# the exact class of corruption D-018 exists to remove, sitting inside the tooling
# that D-018's own checks read. Non-ASCII bytes in command output degrade to '?'.
# That is the intended trade: this repository is ASCII by rule, and a legible
# artefact matters more than faithfully reproducing a character that should not be
# there.
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
Set-Content -Path $OutFile -Encoding ASCII -Value @(
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

    # The redirection sits inside the evaluated string so that it binds to the native
    # command rather than to Invoke-Expression. See the STDERR note in the header.
    Invoke-Expression "$Command 2>&1" | ForEach-Object {
        $text = if ($_ -is [System.Management.Automation.ErrorRecord]) {
            $_.ToString().TrimEnd()
        }
        else {
            ($_ | Out-String).TrimEnd()
        }

        if ($text.Length -gt 0) {
            Add-Content -Path $OutFile -Value $text -Encoding ASCII
            if ($Echo) { Write-Host $text }
            $script:produced = $true
        }
    }

    if (-not $script:produced) {
        Add-Content -Path $OutFile -Value '(no output)' -Encoding ASCII
    }

    $code = $LASTEXITCODE
    Add-Content -Path $OutFile -Encoding ASCII -Value @(
        ('-' * 78),
        "EXITCODE : $code",
        'STATUS   : COMPLETED'
    )
    $verdict = if ($code -eq 0) { 'OK' } else { "NON-ZERO EXIT ($code)" }
}
catch {
    Add-Content -Path $OutFile -Encoding ASCII -Value @(
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
