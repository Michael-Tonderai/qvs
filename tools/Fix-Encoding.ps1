# tools\Fix-Encoding.ps1
#
# QVS one-time text normaliser. Implements D-018, and enforces D-012 while it is here.
#
# It does three things to every repository text file:
#
#   1. Replaces known typographic characters with ASCII equivalents - the section
#      sign becomes "Section", em and en dashes become hyphens, curly quotes become
#      straight ones, and so on. The map below is the whole contract: a character
#      that is not in it is NOT guessed at. It is reported as UNMAPPED and left
#      exactly as it is, for a human to decide about.
#
#   2. Strips a byte order mark if one is present, and rewrites the file as UTF-8
#      with no BOM. Once the content is ASCII this is the same byte sequence either
#      way, which is the entire point of D-018.
#
#   3. Converts CRLF to LF. D-012 says LF everywhere with no exception, and
#      .gitattributes enforces it at commit time. Doing it here as well costs nothing
#      and means the working tree matches what git will store, so a diff never shows
#      a whole-file change for a reason nobody can see.
#
# WHY THE SECTION SIGN IS NOT IN THE MAP. Its replacement is a word, so it needs a
# space after it, and a plain character-for-string replacement of "<sign> 3" yields
# two spaces. The obvious remedy - a tidy-up pass that collapses a doubled space
# after the word - requires this script to contain that doubled space as a literal,
# and this script normalises itself along with everything else. The first dry run, on
# 2026-09-07, reported that it would rewrite itself with zero substitutions: it was
# about to collapse its own tidy-up literal and leave behind a while loop whose
# condition is always true. So the sign is handled by a regex that consumes any
# spaces that follow it, the doubled space is never created, and there is no second
# pass to be destroyed. The pattern is spelled \u00A7, which is ASCII in the source,
# so the script cannot match itself.
#
# SAFETY. There are no commits in this repository yet, so there is no `git checkout`
# to undo a bad conversion. Two mechanisms stand in for it:
#
#   -DryRun   reports every change it would make and writes nothing at all.
#   Backups   every file that is about to change is copied to
#             dev_reports\encoding_backup\ first, preserving its relative path.
#             dev_reports is gitignored, so backups never reach the history.
#
# Run the dry run first, read the artefact, then run it for real:
#   .\tools\Fix-Encoding.ps1 -DryRun
#   .\tools\Fix-Encoding.ps1
#
# Use -Exclude to hold a file back, matched against the relative path:
#   .\tools\Fix-Encoding.ps1 -Exclude 'docs\SESSION_LOG.md'
#
# Verify with .\tools\Check-Ascii.ps1 afterwards. This script's own report is a
# claim; that script is the check.

[CmdletBinding()]
param(
    [switch]   $DryRun,
    [string[]] $Exclude = @()
)

$ErrorActionPreference = 'Continue'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$ReportDir = Join-Path $RepoRoot 'dev_reports'
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}
$OutFile   = Join-Path $ReportDir 'fix_encoding.txt'
$BackupDir = Join-Path $ReportDir 'encoding_backup'

$L = New-Object System.Collections.ArrayList
function Add-Line([string] $t) { [void] $L.Add($t) }
function Add-Head([string] $t) { [void] $L.Add(''); [void] $L.Add("=== $t ===") }

# --------------------------------------------------------------- the section sign ---
# Handled separately from the map, for the reason set out in the header. Trailing
# spaces and tabs are consumed so that both "<sign>0.6" and "<sign> 0.6" come out as
# one word, one space, the number.
$SectionPattern     = "\u00A7[ \t]*"
$SectionReplacement = 'Section '

# ------------------------------------------------------------ the substitution map ---
# Keys are written as numeric character codes rather than as the characters
# themselves, so this file stays ASCII and cannot rewrite its own map.
$Map = [ordered] @{
    ([char] 0x2014) = '-'          # em dash
    ([char] 0x2013) = '-'          # en dash
    ([char] 0x2011) = '-'          # non-breaking hyphen
    ([char] 0x2018) = "'"          # left single quote
    ([char] 0x2019) = "'"          # right single quote / apostrophe
    ([char] 0x201C) = '"'          # left double quote
    ([char] 0x201D) = '"'          # right double quote
    ([char] 0x00AB) = '"'          # left guillemet
    ([char] 0x00BB) = '"'          # right guillemet
    ([char] 0x2026) = '...'        # ellipsis
    ([char] 0x2192) = '->'         # rightwards arrow
    ([char] 0x2190) = '<-'         # leftwards arrow
    ([char] 0x2022) = '-'          # bullet
    ([char] 0x00B7) = '-'          # middle dot
    ([char] 0x00A0) = ' '          # non-breaking space
    ([char] 0x2009) = ' '          # thin space
    ([char] 0x200B) = ''           # zero width space
    ([char] 0xFEFF) = ''           # byte order mark as a character
}

# ---------------------------------------------------------------- file selection ---
# Identical set to tools\Check-Ascii.ps1. The duplication is deliberate: these two
# scripts must agree about what "a repository text file" means, and a shared helper
# file would be a third thing to keep in sync for the sake of twenty lines.
$SkipDirs = @(
    '.git', '.venv', 'dev_reports', '__pycache__', '.pytest_cache',
    '.ruff_cache', '.mypy_cache', 'htmlcov', 'node_modules', 'staticfiles'
)
$TextExt = @(
    '.md', '.txt', '.ps1', '.py', '.toml', '.cfg', '.ini',
    '.yml', '.yaml', '.json', '.html', '.css', '.js', '.sql'
)
$TextNames = @(
    '.gitignore', '.gitattributes', '.dockerignore',
    'Dockerfile', 'Makefile', 'LICENSE'
)

function Get-RepoTextFiles {
    param([string] $Root)

    Get-ChildItem -Path $Root -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object {
            $rel   = $_.FullName.Substring($Root.Length).TrimStart('\')
            $parts = $rel -split '\\'
            $blocked = $false
            foreach ($p in $parts) { if ($SkipDirs -contains $p) { $blocked = $true } }
            $isText = ($TextExt -contains $_.Extension.ToLower()) -or ($TextNames -contains $_.Name)
            (-not $blocked) -and $isText
        } |
        Sort-Object FullName
}

Add-Line 'QVS TEXT NORMALISATION'
Add-Line "WHEN     : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line "REPOROOT : $RepoRoot"
Add-Line ("MODE     : " + $(if ($DryRun) { 'DRY RUN - nothing will be written' } else { 'APPLY' }))
if ($Exclude.Count -gt 0) {
    Add-Line "EXCLUDED : $($Exclude -join ', ')"
}
Add-Line ('-' * 78)

$files = @(Get-RepoTextFiles -Root $RepoRoot)
Add-Line "candidates : $($files.Count) text file(s)"

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

$changedFiles  = 0
$totalSubs     = 0
$totalCrlf     = 0
$bomStripped   = 0
$unmappedFiles = 0
$errors        = 0

Add-Head 'PER FILE'

foreach ($f in $files) {
    $rel = $f.FullName.Substring($RepoRoot.Length).TrimStart('\')

    $skip = $false
    foreach ($x in $Exclude) {
        if ($rel -ieq $x -or $rel -ilike $x) { $skip = $true }
    }
    if ($skip) {
        Add-Line "  SKIP  $rel  (excluded by request)"
        continue
    }

    $original = $null
    try   { $original = Get-Content -Path $f.FullName -Raw -Encoding UTF8 -ErrorAction Stop }
    catch { Add-Line "  ERROR $rel - could not read: $($_.Exception.Message)"; $errors++; continue }

    if ($null -eq $original) { $original = '' }

    $text = $original

    # -- BOM, checked on the raw bytes ------------------------------------------------
    $hadBom = $false
    try {
        $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
        if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            $hadBom = $true
        }
    }
    catch { }

    # -- substitutions ---------------------------------------------------------------
    $fileSubs = 0
    $detail   = @()

    $sectionCount = ([regex]::Matches($text, $SectionPattern)).Count
    if ($sectionCount -gt 0) {
        $text      = [regex]::Replace($text, $SectionPattern, $SectionReplacement)
        $fileSubs += $sectionCount
        $detail   += ('U+00A7 x{0}' -f $sectionCount)
    }

    foreach ($k in $Map.Keys) {
        $needle = [string] $k
        $count  = ([regex]::Matches($text, [regex]::Escape($needle))).Count
        if ($count -gt 0) {
            $text      = $text.Replace($needle, [string] $Map[$k])
            $fileSubs += $count
            $detail   += ('U+{0:X4} x{1}' -f [int] $k, $count)
        }
    }

    # -- line endings (D-012) --------------------------------------------------------
    $crlf = ([regex]::Matches($text, "\r\n")).Count
    if ($crlf -gt 0) { $text = $text -replace "\r\n", "`n" }

    # -- anything left that we do not have a rule for --------------------------------
    # Not guessed at. Reported and left alone, because a wrong substitution inside a
    # governance document is worse than a character that needs a human decision.
    $residual = @()
    foreach ($ch in $text.ToCharArray()) {
        $code = [int] $ch
        if ($code -gt 127) { $residual += ('U+{0:X4}' -f $code) }
    }
    $residual = @($residual | Sort-Object -Unique)

    $needsWrite = ($text -ne $original) -or $hadBom

    if (-not $needsWrite -and $residual.Count -eq 0) {
        continue
    }

    $flags = @()
    if ($fileSubs -gt 0) { $flags += "$fileSubs sub(s): $($detail -join ', ')" }
    if ($crlf -gt 0)     { $flags += "$crlf CRLF -> LF" }
    if ($hadBom)         { $flags += 'BOM stripped' }
    if ($residual.Count -gt 0) {
        $flags += "UNMAPPED: $($residual -join ' ')"
        $unmappedFiles++
    }
    # A file that would be written with nothing to report is a defect in this script,
    # not a no-op. It is what the 2026-09-07 dry run surfaced. Say so rather than
    # printing a blank line.
    if ($flags.Count -eq 0) {
        $flags += 'CHANGED WITH NO REPORTED REASON - investigate before applying'
    }

    $verb = if ($DryRun) { 'WOULD' } else { 'FIXED' }
    Add-Line "  $verb $rel"
    Add-Line "        $($flags -join ' | ')"

    $totalSubs   += $fileSubs
    $totalCrlf   += $crlf
    if ($hadBom) { $bomStripped++ }
    if ($needsWrite) { $changedFiles++ }

    if (-not $DryRun -and $needsWrite) {
        # Back up before touching anything. There is no commit to fall back on.
        try {
            $dest    = Join-Path $BackupDir $rel
            $destDir = Split-Path -Parent $dest
            if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
            Copy-Item -LiteralPath $f.FullName -Destination $dest -Force
        }
        catch {
            Add-Line "        ERROR backup failed, file NOT modified: $($_.Exception.Message)"
            $errors++
            continue
        }

        try {
            [System.IO.File]::WriteAllText($f.FullName, $text, $Utf8NoBom)
        }
        catch {
            Add-Line "        ERROR write failed: $($_.Exception.Message)"
            $errors++
        }
    }
}

if ($changedFiles -eq 0 -and $unmappedFiles -eq 0) {
    Add-Line '  (nothing to change - every text file is already ASCII, LF and BOM-free)'
}

# ----------------------------------------------------------------------- verdict ---
Add-Line ''
Add-Line ('-' * 78)
Add-Line "FILES SCANNED   : $($files.Count)"
Add-Line "FILES CHANGED   : $changedFiles"
Add-Line "SUBSTITUTIONS   : $totalSubs"
Add-Line "CRLF CONVERTED  : $totalCrlf"
Add-Line "BOMS STRIPPED   : $bomStripped"
Add-Line "UNMAPPED FILES  : $unmappedFiles"
Add-Line "ERRORS          : $errors"
if (-not $DryRun) {
    Add-Line "BACKUPS         : dev_reports\encoding_backup\"
}

$verdict = ''
if ($errors -gt 0) {
    $verdict = "ERRORS  $errors"
    Add-Line 'VERDICT  : ERRORS - see above before proceeding'
}
elseif ($unmappedFiles -gt 0) {
    $verdict = "NEEDS REVIEW  $unmappedFiles file(s) hold unmapped characters"
    Add-Line 'VERDICT  : NEEDS REVIEW - unmapped characters were left in place'
}
elseif ($DryRun) {
    $verdict = "DRY RUN  $changedFiles file(s) would change"
    Add-Line 'VERDICT  : DRY RUN COMPLETE - nothing was written'
}
elseif ($changedFiles -eq 0) {
    $verdict = 'ALREADY CLEAN'
    Add-Line 'VERDICT  : ALREADY CLEAN'
}
else {
    $verdict = "NORMALISED  $changedFiles file(s)"
    Add-Line 'VERDICT  : NORMALISED - verify with .\tools\Check-Ascii.ps1'
}

Set-Content -Path $OutFile -Value $L.ToArray() -Encoding ASCII

Write-Host $verdict
Write-Host '  -> dev_reports\fix_encoding.txt'
