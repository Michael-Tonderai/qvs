# tools\Session-Open.ps1
#
# QVS session-open census. Implements HANDOVER.md Section 0.4.
#
# Derives the repository's actual state so a session never has to trust the claim in
# the last SESSION_LOG block. Everything here is READ ONLY - it changes nothing.
#
# HEAD is read directly from .git\refs rather than from a git summary command,
# because a summary can be stale, truncated or reformatted, whereas the ref file is
# the thing itself.
#
# REVISED IN SESSION 002 for three defects found on its first real run:
#
#   1. WORKING TREE MISCLASSIFIED. The tree was judged on whether
#      `git status --porcelain` returned anything at all, so a repository with
#      untracked files and no commits reported DIRTY. DIRTY is the one signal
#      Section 0.5 uses to mean "the other account is mid-session", and a false
#      positive on it stops a session for no reason - which is worse than no signal,
#      because a signal that cries wolf gets overridden by habit. Classification is
#      now made on the porcelain status codes: every line prefixed ?? is UNTRACKED
#      ONLY, anything else is a tracked modification and therefore genuinely dirty.
#
#   2. THE "NO COMMITS" FALLBACK NEVER FIRED. `git log` on an unborn branch writes to
#      stderr. Merging that into the pipeline with 2>&1 turned it into a nine-line
#      NativeCommandError dump, and the fallback tested for empty output, which error
#      text is not. The census therefore carried what looked like a script crash but
#      was the normal state of a fresh repository. Commit presence is now established
#      with `git rev-parse --verify HEAD` and its exit code, and git's stderr goes to
#      $null rather than into the pipeline.
#
#   3. THE LOG TAIL WAS MOJIBAKE. Get-Content ran without -Encoding UTF8, so
#      PowerShell 5.1 decoded a UTF-8 file as ANSI. Fixed here, and removed as a class
#      by D-018 - repository text is ASCII only, enforced by tools\Check-Ascii.ps1.
#
# The artefact is written as ASCII with no byte order mark, for the same reason. One
# consequence worth knowing: a filename containing non-ASCII would render as a
# question mark in the tree listing. On this project that would itself be a finding.
#
# Run it with:
#   .\tools\Session-Open.ps1

[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$ReportDir = Join-Path $RepoRoot 'dev_reports'
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}
$OutFile = Join-Path $ReportDir 'session_open.txt'

$L = New-Object System.Collections.ArrayList
function Add-Line([string] $Text) { [void] $L.Add($Text) }
function Add-Head([string] $Text) {
    [void] $L.Add('')
    [void] $L.Add("=== $Text ===")
}

Add-Line 'QVS SESSION OPEN CENSUS'
Add-Line "WHEN     : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line "REPOROOT : $RepoRoot"
Add-Line ('-' * 78)

$GitDir = Join-Path $RepoRoot '.git'
$IsRepo = Test-Path $GitDir

# Set from the working-tree section and reported on the console, so the two lines the
# script prints carry the one fact a session most needs before it reads anything.
$TreeVerdict = 'unknown'

# ------------------------------------------------------------------ git: HEAD ---
Add-Head 'HEAD (read from .git, not from a summary command)'
if (-not $IsRepo) {
    Add-Line 'NOT A GIT REPOSITORY - repository has not been initialised yet.'
}
else {
    $HeadFile = Join-Path $GitDir 'HEAD'
    $headRaw  = (Get-Content -Path $HeadFile -Raw -Encoding UTF8 -ErrorAction SilentlyContinue)
    if ($null -ne $headRaw) { $headRaw = $headRaw.Trim() }
    Add-Line ".git\HEAD        : $headRaw"

    if ($headRaw -match '^ref:\s*(.+)$') {
        $refPath = $Matches[1].Trim()
        $branch  = $refPath -replace '^refs/heads/', ''
        Add-Line "branch           : $branch"

        # Loose ref first; fall back to packed-refs if the branch has been packed
        $localRef = Join-Path $GitDir ($refPath -replace '/', '\')
        if (Test-Path $localRef) {
            Add-Line "local HEAD sha   : $((Get-Content $localRef -Raw -Encoding UTF8).Trim())"
        }
        else {
            $packed = Join-Path $GitDir 'packed-refs'
            if (Test-Path $packed) {
                $hit = Select-String -Path $packed -Pattern ([regex]::Escape($refPath)) -SimpleMatch |
                       Select-Object -First 1
                if ($hit) { Add-Line "local HEAD sha   : $(($hit.Line -split '\s+')[0])  [packed-refs]" }
                else      { Add-Line 'local HEAD sha   : (no commits yet on this branch)' }
            }
            else {
                Add-Line 'local HEAD sha   : (no commits yet on this branch)'
            }
        }

        $remoteRef = Join-Path $GitDir "refs\remotes\origin\$branch"
        if (Test-Path $remoteRef) {
            Add-Line "origin HEAD sha  : $((Get-Content $remoteRef -Raw -Encoding UTF8).Trim())"
        }
        else {
            Add-Line 'origin HEAD sha  : (branch not on origin - nothing pushed yet)'
        }
    }
    else {
        Add-Line 'branch           : DETACHED HEAD'
    }
}

# --------------------------------------------------------------- git: the tree ---
# Defect 1. Untracked is not dirty. HANDOVER.md Section 0.5 reads DIRTY as "the other
# account is mid-session"; untracked files are simply work that has never been added.
Add-Head 'WORKING TREE'
if (-not $IsRepo) {
    Add-Line 'skipped - not a repository'
    $TreeVerdict = 'no repo'
}
else {
    Push-Location $RepoRoot
    try {
        $statusLines = @(& git status --porcelain 2>$null | Where-Object { $_ -ne '' })

        $untracked = @($statusLines | Where-Object { $_ -match '^\?\?' })
        $modified  = @($statusLines | Where-Object { $_ -notmatch '^\?\?' })

        if ($statusLines.Count -eq 0) {
            Add-Line 'clean'
            $TreeVerdict = 'clean'
        }
        elseif ($modified.Count -eq 0) {
            $TreeVerdict = 'untracked only'
            Add-Line "UNTRACKED ONLY - $($untracked.Count) new path(s), no tracked modifications."
            Add-Line 'This is NOT dirty. It does not mean the other account is mid-session.'
            Add-Line ''
            foreach ($u in $untracked) { Add-Line "  $u" }
        }
        else {
            $TreeVerdict = 'DIRTY'
            Add-Line "DIRTY - $($modified.Count) tracked modification(s). See HANDOVER.md Section 0.5"
            Add-Line 'before proceeding: a dirty tree at session open means the other account is'
            Add-Line 'mid-session. Do not clean it.'
            Add-Line ''
            foreach ($m in $modified)  { Add-Line "  $m" }
            if ($untracked.Count -gt 0) {
                Add-Line ''
                Add-Line "  (plus $($untracked.Count) untracked path(s))"
                foreach ($u in $untracked) { Add-Line "  $u" }
            }
        }

        # ------------------------------------------------------------- commits ---
        # Defect 2. Establish whether a commit exists before asking for a log, rather
        # than asking and interpreting the failure.
        Add-Head 'RECENT COMMITS'
        & git rev-parse --verify -q HEAD 2>$null | Out-Null
        $hasCommits = ($LASTEXITCODE -eq 0)

        if ($hasCommits) {
            $log = (& git log --oneline -10 2>$null | Out-String).TrimEnd()
            if ([string]::IsNullOrWhiteSpace($log)) { Add-Line '(log returned nothing)' }
            else { Add-Line $log }
        }
        else {
            Add-Line '(no commits yet - the branch is unborn, which is the expected state'
            Add-Line ' until the first commit lands)'
        }

        Add-Head 'BRANCHES'
        $branches = (& git branch -a 2>$null | Out-String).TrimEnd()
        if ([string]::IsNullOrWhiteSpace($branches)) {
            Add-Line '(none - a branch appears in refs only once it has a commit)'
        }
        else {
            Add-Line $branches
        }

        Add-Head 'REMOTES'
        $rem = (& git remote -v 2>$null | Out-String).TrimEnd()
        if ([string]::IsNullOrWhiteSpace($rem)) { Add-Line '(no remote configured)' }
        else { Add-Line $rem }
    }
    catch { Add-Line "ERROR: $($_.Exception.Message)" }
    finally { Pop-Location }
}

# --------------------------------------------------------------- the interpreter ---
# CLAUDE.md Section 3: every Python call goes through .venv. Confirm it exists and is
# the expected version.
Add-Head 'VIRTUAL ENVIRONMENT'
$VenvPy = Join-Path $RepoRoot '.venv\Scripts\python.exe'
if (Test-Path $VenvPy) {
    Add-Line "interpreter : $VenvPy"
    try   { Add-Line "version     : $((& $VenvPy --version 2>&1 | Out-String).Trim())" }
    catch { Add-Line "version     : ERROR - $($_.Exception.Message)" }
}
else {
    Add-Line '.venv NOT PRESENT - run .\tools\Setup-Venv.ps1'
}

# ----------------------------------------------------------------- the last block ---
# Defect 3. Read as UTF-8 explicitly. Under D-018 the file should be ASCII anyway, so
# this is belt and braces rather than the fix - the fix is that the character is not
# in the file in the first place.
Add-Head 'SESSION LOG - LAST 40 LINES'
$LogFile = Join-Path $RepoRoot 'docs\SESSION_LOG.md'
if (Test-Path $LogFile) {
    Add-Line ((Get-Content -Path $LogFile -Tail 40 -Encoding UTF8 | Out-String).TrimEnd())
}
else {
    Add-Line 'docs\SESSION_LOG.md not found.'
}

Add-Line ''
Add-Line ('-' * 78)
Add-Line "TREE VERDICT : $TreeVerdict"
Add-Line 'END OF CENSUS'

Set-Content -Path $OutFile -Value $L.ToArray() -Encoding ASCII

Write-Host "Session-open census derived - tree: $TreeVerdict"
Write-Host '  -> dev_reports\session_open.txt'
