# tools\Check-Docs.ps1
#
# QVS document staleness check. Implements CLAUDE.md Section 10.
#
# THE PROBLEM THIS SOLVES: a governance document that has silently fallen behind the
# repository is worse than no document, because it is trusted. Recovering a current
# position from a stale one is expensive and demoralising. This script converts
# "did we remember to update the docs" from a discipline into a command.
#
# It is READ ONLY. It changes nothing and fixes nothing - it reports drift.
#
# Four families of check:
#   A  VERSION DRIFT   - tool versions asserted in CLAUDE.md vs what is installed
#   B  DOCUMENT MAP    - every file listed in CLAUDE.md Section 9 exists, and every .md in
#                        docs\ is listed there
#   C  LOG CURRENCY    - are there commits newer than the last SESSION_LOG block
#   D  DECISION REFS   - every D-nnn referenced anywhere is registered in DECISIONS.md
#
# Run it with:
#   .\tools\Check-Docs.ps1
#
# Run it before every commit. It is cheap and it is the only thing standing between
# this project and the staleness spiral.

[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$ReportDir = Join-Path $RepoRoot 'dev_reports'
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}
$OutFile = Join-Path $ReportDir 'check_docs.txt'

$L = New-Object System.Collections.ArrayList
$script:Fails = 0
$script:Warns = 0

function Add-Line([string] $t) { [void] $L.Add($t) }
function Add-Head([string] $t) { [void] $L.Add(''); [void] $L.Add("=== $t ===") }
function Pass([string] $t)     { [void] $L.Add("  PASS  $t") }
function Warn([string] $t)     { [void] $L.Add("  WARN  $t"); $script:Warns++ }
function Fail([string] $t)     { [void] $L.Add("  FAIL  $t"); $script:Fails++ }
function Skip([string] $t)     { [void] $L.Add("  SKIP  $t") }

Add-Line 'QVS DOCUMENT STALENESS CHECK'
Add-Line "WHEN     : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line "REPOROOT : $RepoRoot"
Add-Line ('-' * 78)

$ClaudeMd = Join-Path $RepoRoot 'CLAUDE.md'
if (-not (Test-Path $ClaudeMd)) {
    Add-Line 'FATAL: CLAUDE.md not found. Nothing can be checked against it.'
    Set-Content -Path $OutFile -Value $L.ToArray() -Encoding UTF8
    Write-Host 'FATAL  CLAUDE.md missing'
    Write-Host '  -> dev_reports\check_docs.txt'
    exit 1
}
$ClaudeText = Get-Content -Path $ClaudeMd -Raw

# ============================================================ A: VERSION DRIFT ===
# CLAUDE.md Section 2 states the installed versions. If the machine has moved on and the
# document has not, a future session inherits a lie about its own environment.
Add-Head 'A. VERSION DRIFT (CLAUDE.md section 2 vs the machine)'

function Test-VersionClaim {
    param(
        [string] $Tool,        # command to run
        [string] $VersionArg,  # argument that prints the version
        [string] $Pattern      # regex capturing the version number from its output
    )
    $cmd = Get-Command $Tool -ErrorAction SilentlyContinue
    if ($null -eq $cmd) {
        Warn "$Tool not installed - cannot verify the claim in CLAUDE.md"
        return
    }
    try {
        $raw = (& $Tool $VersionArg 2>&1 | Out-String)
    }
    catch {
        Warn "$Tool failed to report a version"
        return
    }
    if ($raw -match $Pattern) {
        $actual = $Matches[1]
        if ($ClaudeText -match [regex]::Escape($actual)) {
            Pass "$Tool $actual is stated in CLAUDE.md"
        }
        else {
            Fail "$Tool is $actual on this machine but that version does not appear in CLAUDE.md"
        }
    }
    else {
        Warn "$Tool version could not be parsed from its output"
    }
}

Test-VersionClaim -Tool 'git'    -VersionArg '--version' -Pattern 'git version ([0-9][0-9.]*[0-9])'
Test-VersionClaim -Tool 'gh'     -VersionArg '--version' -Pattern 'gh version ([0-9][0-9.]*[0-9])'
Test-VersionClaim -Tool 'docker' -VersionArg '--version' -Pattern 'Docker version ([0-9][0-9.]*[0-9])'
Test-VersionClaim -Tool 'claude' -VersionArg '--version' -Pattern '([0-9]+\.[0-9]+\.[0-9]+)'

# The interpreter is checked against the venv, not the launcher, because the venv is
# what actually runs the code (CLAUDE.md section 3).
$VenvPy = Join-Path $RepoRoot '.venv\Scripts\python.exe'
if (Test-Path $VenvPy) {
    $pv = (& $VenvPy --version 2>&1 | Out-String)
    if ($pv -match 'Python ([0-9]+\.[0-9]+\.[0-9]+)') {
        $actual = $Matches[1]
        if ($ClaudeText -match [regex]::Escape($actual)) { Pass "venv Python $actual is stated in CLAUDE.md" }
        else { Fail "venv Python is $actual but that version does not appear in CLAUDE.md" }
    }
}
else {
    Skip '.venv not present yet - interpreter claim unverifiable'
}

# The repo root is stated in CLAUDE.md. If the folder is ever moved, this catches it.
if ($ClaudeText -match [regex]::Escape($RepoRoot)) { Pass 'repo root path in CLAUDE.md matches reality' }
else { Fail "repo root is '$RepoRoot' but CLAUDE.md states a different path" }

# ============================================================= B: DOCUMENT MAP ===
Add-Head 'B. DOCUMENT MAP (CLAUDE.md section 9)'

$expected = @(
    'CLAUDE.md',
    'docs/HANDOVER.md',
    'docs/SESSION_LOG.md',
    'docs/REQUIREMENTS.md',
    'docs/DECISIONS.md'
)
foreach ($rel in $expected) {
    $full = Join-Path $RepoRoot ($rel -replace '/', '\')
    if (Test-Path $full) {
        if ($ClaudeText -match [regex]::Escape($rel)) { Pass "$rel exists and is on the map" }
        else { Fail "$rel exists but is NOT listed in CLAUDE.md section 9" }
    }
    else {
        Warn "$rel is on the map but does not exist yet"
    }
}

# The reverse direction: a document nobody listed is a document nobody maintains.
$docsDir = Join-Path $RepoRoot 'docs'
if (Test-Path $docsDir) {
    Get-ChildItem -Path $docsDir -Filter '*.md' -File | ForEach-Object {
        $rel = "docs/$($_.Name)"
        if ($ClaudeText -match [regex]::Escape($rel)) { Pass "$rel is listed in section 9" }
        else { Fail "$rel exists in docs\ but is NOT listed in CLAUDE.md section 9" }
    }
}

# ============================================================= C: LOG CURRENCY ===
# The check that matters most. If commits exist that are newer than the newest
# SESSION_LOG block, the log has fallen behind the repository - which is exactly the
# condition that becomes expensive to recover from.
Add-Head 'C. SESSION LOG CURRENCY'

$LogFile = Join-Path $RepoRoot 'docs\SESSION_LOG.md'
if (-not (Test-Path $LogFile)) {
    Fail 'docs\SESSION_LOG.md does not exist'
}
elseif (-not (Test-Path (Join-Path $RepoRoot '.git'))) {
    Skip 'not a git repository yet - cannot compare against commit dates'
}
else {
    $logText = Get-Content -Path $LogFile -Raw
    $dates = [regex]::Matches($logText, '(\d{4}-\d{2}-\d{2})') |
             ForEach-Object { [datetime]::ParseExact($_.Groups[1].Value, 'yyyy-MM-dd', $null) }

    if ($dates.Count -eq 0) {
        Fail 'no dated block found in SESSION_LOG.md'
    }
    else {
        $newestLog = ($dates | Sort-Object)[-1]
        Add-Line "  newest log block  : $($newestLog.ToString('yyyy-MM-dd'))"

        Push-Location $RepoRoot
        try {
            $lastCommitRaw = (git log -1 --format=%cs 2>&1 | Out-String).Trim()
        }
        catch { $lastCommitRaw = '' }
        finally { Pop-Location }

        if ($lastCommitRaw -match '^\d{4}-\d{2}-\d{2}$') {
            $newestCommit = [datetime]::ParseExact($lastCommitRaw, 'yyyy-MM-dd', $null)
            Add-Line "  newest commit     : $lastCommitRaw"
            if ($newestCommit -gt $newestLog) {
                $gap = ($newestCommit - $newestLog).Days
                Fail "SESSION_LOG is $gap day(s) behind the newest commit - the log is STALE"
            }
            else {
                Pass 'SESSION_LOG is level with or ahead of the newest commit'
            }
        }
        else {
            Skip 'no commits yet - nothing to compare against'
        }
    }
}

# =========================================================== D: DECISION REFS ===
# A decision cited in the log but missing from the register cannot be found later,
# and the report's design-decisions section is assembled from that register.
Add-Head 'D. DECISION REFERENCES'

$DecFile = Join-Path $RepoRoot 'docs\DECISIONS.md'
if (-not (Test-Path $DecFile)) {
    Skip 'docs\DECISIONS.md does not exist yet'
}
else {
    $decText = Get-Content -Path $DecFile -Raw
    $registered = @([regex]::Matches($decText, '\bD-(\d{3})\b') |
                    ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
    Add-Line "  registered: $($registered -join ', ')"

    # Scan every file where a decision could plausibly be cited, not just the three
    # governance documents. A D-number cited in a requirements file or a tools script
    # is exactly as unfindable later as one cited in the session log, and restricting
    # the scan to docs is how D-016 was cited unregistered on 2026-09-07.
    $sources = @()
    $sources += Get-ChildItem -Path $RepoRoot -Filter '*.md'  -File -ErrorAction SilentlyContinue
    $sources += Get-ChildItem -Path $RepoRoot -Filter '*.txt' -File -ErrorAction SilentlyContinue
    if (Test-Path $docsDir) {
        $sources += Get-ChildItem -Path $docsDir -Filter '*.md' -File -Recurse -ErrorAction SilentlyContinue
    }
    $toolsDir = Join-Path $RepoRoot 'tools'
    if (Test-Path $toolsDir) {
        $sources += Get-ChildItem -Path $toolsDir -Filter '*.ps1' -File -ErrorAction SilentlyContinue
        $sources += Get-ChildItem -Path $toolsDir -Filter '*.py'  -File -ErrorAction SilentlyContinue
    }
    $sources = @($sources | Select-Object -ExpandProperty FullName -Unique |
                 Where-Object { $_ -ne $DecFile })

    Add-Line "  scanned   : $($sources.Count) file(s)"

    $cited = @()
    foreach ($s in $sources) {
        $t = Get-Content -Path $s -Raw -ErrorAction SilentlyContinue
        if ($null -ne $t) {
            $cited += [regex]::Matches($t, '\bD-(\d{3})\b') | ForEach-Object { $_.Groups[1].Value }
        }
    }
    $cited = @($cited | Sort-Object -Unique)

    $orphans = @($cited | Where-Object { $registered -notcontains $_ })
    if ($orphans.Count -eq 0) { Pass 'every cited D-number is registered' }
    else { foreach ($o in $orphans) { Fail "D-$o is cited but not registered in DECISIONS.md" } }
}

# ===================================================================== verdict ===
Add-Line ''
Add-Line ('-' * 78)
Add-Line "FAILURES : $script:Fails"
Add-Line "WARNINGS : $script:Warns"
if ($script:Fails -eq 0) { Add-Line 'VERDICT  : DOCUMENTS CURRENT' }
else { Add-Line 'VERDICT  : STALE - fix before committing' }

Set-Content -Path $OutFile -Value $L.ToArray() -Encoding UTF8

if ($script:Fails -eq 0) { Write-Host "DOCUMENTS CURRENT  ($script:Warns warning(s))" }
else { Write-Host "STALE  $script:Fails failure(s), $script:Warns warning(s)" }
Write-Host '  -> dev_reports\check_docs.txt'
