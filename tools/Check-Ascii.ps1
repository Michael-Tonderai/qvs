# tools\Check-Ascii.ps1
#
# QVS ASCII purity check. Implements D-018.
#
# THE PROBLEM THIS SOLVES: PowerShell 5.1 decodes a UTF-8 file that carries no byte
# order mark as ANSI. Every non-ASCII character in a document or a script therefore
# arrives corrupted in any artefact a tools\ script produces, and any string
# comparison that touches one fails for a reason that looks like document drift
# rather than like an encoding fault. That is the worst kind of failure: it points
# the reader at the wrong problem.
#
# The project's answer is not to handle the encoding correctly everywhere. It is to
# remove the problem: repository text files contain ASCII only. "Section 3", not a
# section sign. A hyphen, not an em dash. Straight quotes, not curly ones. Once every
# file is ASCII, the bytes decode identically under ANSI and under UTF-8, and the
# whole class of defect is absent rather than managed. Same reasoning as D-012 on
# line endings.
#
# This script is what makes that rule enforceable rather than aspirational. It is
# READ ONLY - it reports. tools\Fix-Encoding.ps1 repairs.
#
# It also reports a byte order mark as a failure. A BOM is not an ASCII byte, and a
# BOM at the head of a file is the other half of the same problem: it is invisible in
# an editor and it breaks the first line of anything that parses the file.
#
# Run it with:
#   .\tools\Check-Ascii.ps1

[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$ReportDir = Join-Path $RepoRoot 'dev_reports'
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}
$OutFile = Join-Path $ReportDir 'check_ascii.txt'

$L = New-Object System.Collections.ArrayList
$script:Fails = 0

function Add-Line([string] $t) { [void] $L.Add($t) }
function Add-Head([string] $t) { [void] $L.Add(''); [void] $L.Add("=== $t ===") }

# ---------------------------------------------------------------- file selection ---
# Directories that hold generated, vendored or version-controlled internals are
# skipped. dev_reports is skipped because artefacts are working evidence, not
# repository text, and a git status line could legitimately carry a non-ASCII
# filename through into one.
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

# --------------------------------------------------------------------- reporting ---
# The offending character is never echoed into the artefact. Printing it would either
# corrupt again on the way out or, in an ASCII artefact, silently become a question
# mark - and a report about invisible characters must not itself hide them. The code
# point is printed instead, and the surrounding line is rendered with each offender
# replaced by <U+XXXX>, so the location is obvious at a glance.
function ConvertTo-SafeLine {
    param([string] $Line)

    $sb = New-Object System.Text.StringBuilder
    foreach ($ch in $Line.ToCharArray()) {
        $code = [int] $ch
        if ($code -gt 127) {
            [void] $sb.Append(('<U+{0:X4}>' -f $code))
        }
        else {
            [void] $sb.Append($ch)
        }
    }
    return $sb.ToString()
}

Add-Line 'QVS ASCII PURITY CHECK'
Add-Line "WHEN     : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line "REPOROOT : $RepoRoot"
Add-Line ('-' * 78)

$files = @(Get-RepoTextFiles -Root $RepoRoot)
Add-Line "scanned  : $($files.Count) text file(s)"

$MaxFindings   = 300
$findingCount  = 0
$dirtyFiles    = 0
$bomFiles      = 0
$truncated     = $false

Add-Head 'FINDINGS'

foreach ($f in $files) {
    $rel = $f.FullName.Substring($RepoRoot.Length).TrimStart('\')

    # BOM is checked on the raw bytes, because by the time the file has been decoded
    # the mark has already been consumed and is no longer visible as content.
    $hasBom = $false
    try {
        $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
        if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            $hasBom = $true
        }
    }
    catch {
        Add-Line "  ERROR $rel - could not read bytes: $($_.Exception.Message)"
        $script:Fails++
        continue
    }

    if ($hasBom) {
        Add-Line "  FAIL  $rel - byte order mark present at offset 0"
        $bomFiles++
        $script:Fails++
    }

    $text = $null
    try   { $text = Get-Content -Path $f.FullName -Raw -Encoding UTF8 -ErrorAction Stop }
    catch { Add-Line "  ERROR $rel - could not decode as UTF-8: $($_.Exception.Message)"
            $script:Fails++
            continue }

    if ([string]::IsNullOrEmpty($text)) { continue }

    $lines     = $text -split "\r?\n"
    $fileDirty = $false

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ([string]::IsNullOrEmpty($line)) { continue }

        $codes = @()
        foreach ($ch in $line.ToCharArray()) {
            $code = [int] $ch
            if ($code -gt 127) { $codes += ('U+{0:X4}' -f $code) }
        }
        if ($codes.Count -eq 0) { continue }

        $fileDirty = $true
        $findingCount++

        if ($findingCount -le $MaxFindings) {
            $safe = ConvertTo-SafeLine -Line $line
            if ($safe.Length -gt 110) { $safe = $safe.Substring(0, 110) + ' ...' }
            $unique = @($codes | Sort-Object -Unique) -join ' '
            Add-Line "  FAIL  ${rel}:$($i + 1)  [$unique]"
            Add-Line "        $safe"
        }
        else {
            $truncated = $true
        }
    }

    if ($fileDirty) {
        $dirtyFiles++
        $script:Fails++
    }
}

if ($findingCount -eq 0 -and $bomFiles -eq 0) {
    Add-Line '  PASS  no non-ASCII characters and no byte order marks found'
}
if ($truncated) {
    Add-Line ''
    Add-Line "  ... output truncated at $MaxFindings finding(s). Total: $findingCount"
}

# ----------------------------------------------------------------------- verdict ---
Add-Line ''
Add-Line ('-' * 78)
Add-Line "FILES SCANNED     : $($files.Count)"
Add-Line "FILES WITH BOM    : $bomFiles"
Add-Line "FILES NON-ASCII   : $dirtyFiles"
Add-Line "LINES NON-ASCII   : $findingCount"

if ($script:Fails -eq 0) {
    Add-Line 'VERDICT  : ASCII CLEAN'
}
else {
    Add-Line 'VERDICT  : NON-ASCII PRESENT - run .\tools\Fix-Encoding.ps1'
}

# Written as ASCII with no byte order mark. A report whose own encoding violates the
# rule it enforces is not a report anyone should trust.
Set-Content -Path $OutFile -Value $L.ToArray() -Encoding ASCII

if ($script:Fails -eq 0) {
    Write-Host "ASCII CLEAN  ($($files.Count) file(s) scanned)"
}
else {
    Write-Host "NON-ASCII PRESENT  $dirtyFiles file(s), $findingCount line(s), $bomFiles BOM"
}
Write-Host '  -> dev_reports\check_ascii.txt'
