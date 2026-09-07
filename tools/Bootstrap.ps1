# tools\Bootstrap.ps1
#
# QVS step 1: audit the machine before anything is built.
#
# This script only READS. It installs nothing, changes no setting and creates no
# project file. Its whole job is to produce dev_reports\bootstrap.txt so Claude can
# see exactly what this machine has, rather than assuming.
#
# Run it with:
#   powershell -ExecutionPolicy Bypass -File ".\tools\Bootstrap.ps1"
#
# The -ExecutionPolicy Bypass is there because a fresh Windows install blocks script
# execution by default. The script reports the current policy so we can decide
# whether to set it properly once, instead of prefixing every run.

[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'

$RepoRoot  = Split-Path -Parent $PSScriptRoot
$ReportDir = Join-Path $RepoRoot 'dev_reports'
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}
$OutFile = Join-Path $ReportDir 'bootstrap.txt'

$L = New-Object System.Collections.ArrayList
function Add-Line([string] $Text) { [void] $L.Add($Text) }
function Add-Rule { [void] $L.Add('-' * 78) }
function Add-Head([string] $Text) {
    [void] $L.Add('')
    [void] $L.Add("=== $Text ===")
}

# ---------------------------------------------------------------- environment ---
Add-Line 'QVS BOOTSTRAP AUDIT'
Add-Line "WHEN      : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Add-Line "HOST      : $env:COMPUTERNAME"
Add-Line "USER      : $env:USERNAME"
Add-Line "REPOROOT  : $RepoRoot"
Add-Line "PSVERSION : $($PSVersionTable.PSVersion)"
Add-Line "OS        : $([System.Environment]::OSVersion.VersionString)"
Add-Line "ARCH      : $env:PROCESSOR_ARCHITECTURE"
Add-Rule

# ------------------------------------------------------------ execution policy ---
# Matters because tools\*.ps1 are the whole working method for this project. If the
# effective policy is Restricted, every run needs a Bypass prefix, which is friction
# we should remove once rather than pay for on every command.
Add-Head 'EXECUTION POLICY'
try {
    Add-Line "Effective: $(Get-ExecutionPolicy)"
    Add-Line ((Get-ExecutionPolicy -List | Out-String).Trim())
}
catch {
    Add-Line "ERROR: $($_.Exception.Message)"
}

# --------------------------------------------------------------- tool presence ---
# Get-Command guards each probe so a missing tool is reported as absent rather than
# throwing and ending the audit early.
Add-Head 'TOOLCHAIN'

$tools = @(
    @{ Name = 'git';     Args = @('--version');  Purpose = 'version control - required' },
    @{ Name = 'py';      Args = @('-V');         Purpose = 'Windows Python launcher - required' },
    @{ Name = 'python';  Args = @('--version');  Purpose = 'system Python - informational only' },
    @{ Name = 'gh';      Args = @('--version');  Purpose = 'GitHub CLI - issues and PRs' },
    @{ Name = 'docker';  Args = @('--version');  Purpose = 'REQ-N-003 deployment' },
    @{ Name = 'claude';  Args = @('--version');  Purpose = 'Claude Code CLI' },
    @{ Name = 'code';    Args = @('--version');  Purpose = 'VS Code CLI' },
    @{ Name = 'winget';  Args = @('--version');  Purpose = 'package installs' },
    @{ Name = 'node';    Args = @('--version');  Purpose = 'informational only' }
)

foreach ($t in $tools) {
    $name = $t.Name
    Add-Line ''
    Add-Line "--- $name  [$($t.Purpose)]"
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($null -eq $cmd) {
        Add-Line 'NOT INSTALLED'
    }
    else {
        Add-Line "path   : $($cmd.Source)"
        try {
            $v = (& $name @($t.Args) 2>&1 | Out-String).Trim()
            if ([string]::IsNullOrWhiteSpace($v)) { $v = '(no version output)' }
            Add-Line "version: $v"
        }
        catch {
            Add-Line "version: ERROR - $($_.Exception.Message)"
        }
    }
}

# ------------------------------------------------------------ python inventory ---
# py -0p lists every interpreter the launcher knows about. We need to confirm a 3.12
# is present before creating the virtual environment (D-010: one version everywhere).
Add-Head 'PYTHON INTERPRETERS KNOWN TO THE LAUNCHER'
if (Get-Command 'py' -ErrorAction SilentlyContinue) {
    try   { Add-Line ((py -0p 2>&1 | Out-String).Trim()) }
    catch { Add-Line "ERROR: $($_.Exception.Message)" }
}
else {
    Add-Line 'py launcher not installed - skipped'
}

# ------------------------------------------------------------------- git state ---
Add-Head 'GIT STATE'
if (Get-Command 'git' -ErrorAction SilentlyContinue) {
    $gitDir = Join-Path $RepoRoot '.git'
    Add-Line "repo initialised: $(Test-Path $gitDir)"
    Push-Location $RepoRoot
    try {
        $n = (git config --get user.name  2>&1 | Out-String).Trim()
        $e = (git config --get user.email 2>&1 | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($n)) { $n = '(unset)' }
        if ([string]::IsNullOrWhiteSpace($e)) { $e = '(unset)' }
        Add-Line "user.name       : $n"
        Add-Line "user.email      : $e"
        Add-Line "remotes         :"
        Add-Line ((git remote -v 2>&1 | Out-String).Trim())
    }
    catch { Add-Line "ERROR: $($_.Exception.Message)" }
    finally { Pop-Location }
}
else {
    Add-Line 'git not installed - skipped'
}

# ------------------------------------------------------------- gh auth status ---
Add-Head 'GITHUB CLI AUTH'
if (Get-Command 'gh' -ErrorAction SilentlyContinue) {
    try   { Add-Line ((gh auth status 2>&1 | Out-String).Trim()) }
    catch { Add-Line "ERROR: $($_.Exception.Message)" }
}
else {
    Add-Line 'gh not installed - skipped'
}

# ------------------------------------------------------------- repo contents ---
Add-Head 'REPO ROOT CONTENTS'
try {
    $items = Get-ChildItem -Path $RepoRoot -Force | Select-Object Mode, Length, Name
    if ($null -eq $items) { Add-Line '(empty)' }
    else { Add-Line (($items | Format-Table -AutoSize | Out-String).Trim()) }
}
catch { Add-Line "ERROR: $($_.Exception.Message)" }

Add-Line ''
Add-Rule
Add-Line 'END OF AUDIT'

Set-Content -Path $OutFile -Value $L.ToArray() -Encoding UTF8
Write-Host ''
Write-Host "Bootstrap audit written to: $OutFile"
Write-Host 'Tell Claude it is done. Do not paste the contents.'
Write-Host ''
