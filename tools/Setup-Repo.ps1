# tools\Setup-Repo.ps1
#
# QVS: initialise the git repository and set its identity.
#
# Identity is set at LOCAL scope, not global, so this project cannot accidentally
# author commits under the wrong name if the machine is later used for something
# else - and so nothing here reaches out and changes a global setting.
#
# core.autocrlf is set to false explicitly. .gitattributes already forces LF via
# 'eol=lf', which overrides autocrlf, but leaving autocrlf at its default means the
# two mechanisms disagree on paper. One stated rule, no ambiguity (D-012).
#
# Idempotent: safe to run twice. It will not re-initialise an existing repository.
#
# Run it with:
#   .\tools\Setup-Repo.ps1

[CmdletBinding()]
param(
    [string] $UserName  = 'Tonderai M. Machimbira',
    [string] $UserEmail = 'tonderaimachimbira@gmail.com'
)

$ErrorActionPreference = 'Continue'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$ReportDir = Join-Path $RepoRoot 'dev_reports'
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}
$OutFile = Join-Path $ReportDir 'setup_repo.txt'

$L = New-Object System.Collections.ArrayList
function Add-Line([string] $t) { [void] $L.Add($t) }
function Add-Head([string] $t) { [void] $L.Add(''); [void] $L.Add("=== $t ===") }

Add-Line 'QVS REPOSITORY SETUP'
Add-Line "WHEN     : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line "REPOROOT : $RepoRoot"
Add-Line ('-' * 78)

if (-not (Get-Command 'git' -ErrorAction SilentlyContinue)) {
    Add-Line 'FATAL: git not found on PATH.'
    Set-Content -Path $OutFile -Value $L.ToArray() -Encoding UTF8
    Write-Host 'FATAL  git not on PATH'
    Write-Host '  -> dev_reports\setup_repo.txt'
    exit 1
}

Push-Location $RepoRoot
try {
    $GitDir = Join-Path $RepoRoot '.git'

    Add-Head 'INITIALISE'
    if (Test-Path $GitDir) {
        Add-Line 'Repository already initialised - skipping git init.'
    }
    else {
        # -b main so the default branch is named at creation rather than renamed later
        Add-Line ((git init -b main 2>&1 | Out-String).TrimEnd())
    }

    Add-Head 'IDENTITY (local scope only)'
    git config --local user.name  $UserName  2>&1 | Out-Null
    git config --local user.email $UserEmail 2>&1 | Out-Null
    Add-Line "user.name  : $((git config --local --get user.name  2>&1 | Out-String).Trim())"
    Add-Line "user.email : $((git config --local --get user.email 2>&1 | Out-String).Trim())"

    Add-Head 'LINE ENDINGS'
    git config --local core.autocrlf false 2>&1 | Out-Null
    Add-Line "core.autocrlf : $((git config --local --get core.autocrlf 2>&1 | Out-String).Trim())"
    $ga = Join-Path $RepoRoot '.gitattributes'
    Add-Line ".gitattributes present : $(Test-Path $ga)"

    Add-Head 'STATUS'
    Add-Line ((git status --porcelain 2>&1 | Out-String).TrimEnd())

    Add-Head 'IGNORE CHECK'
    # Confirms .gitignore is actually taking effect before the first commit is made,
    # rather than discovering dev_reports\ in the history afterwards.
    $probe = (git check-ignore -v 'dev_reports/bootstrap.txt' 2>&1 | Out-String).Trim()
    if ([string]::IsNullOrWhiteSpace($probe)) {
        Add-Line 'WARNING: dev_reports\ is NOT being ignored. Check .gitignore.'
    }
    else {
        Add-Line "dev_reports ignored by: $probe"
    }
}
catch {
    Add-Line "EXCEPTION: $($_.Exception.Message)"
}
finally {
    Pop-Location
}

Add-Line ''
Add-Line ('-' * 78)
Add-Line 'END'
Set-Content -Path $OutFile -Value $L.ToArray() -Encoding UTF8

Write-Host 'Repository initialised and identity set'
Write-Host '  -> dev_reports\setup_repo.txt'
