# tools\Set-Env.ps1
#
# Loads .env into the current PowerShell session. Delivers D-030.
#
# WHY THIS EXISTS. config/settings.py reads os.environ directly and raises
# ImproperlyConfigured when a key is absent (D-003). Nothing in the project reads .env,
# so a fresh terminal - and every terminal is fresh after a reboot - starts with no
# variables and twelve tests fail. That failure is D-003 working correctly, not a
# defect, so the fix is to supply the environment explicitly rather than to soften the
# check.
#
# WHY NOT python-dotenv. D-030 rejected it. Reading .env inside settings.py would mean
# the container and the CI runner carry a dependency whose only job is to read a file
# that exists in neither, and it would make the local case invisible instead of
# explicit. A variable silently supplied from somewhere is harder to reason about than
# one that is missing loudly.
#
# SCOPE. Variables set here live in this PowerShell session and vanish when the terminal
# closes. That is deliberate: nothing is written to the user or machine environment,
# so a key cannot leak into an unrelated process or survive the session that needed it.
#
# Values are never printed. Only names are echoed, so the output can be pasted into a
# report or a session log without redaction.

[CmdletBinding()]
param(
    # Defaults to the .env beside the repository root. Overridable for a throwaway file.
    [string]$EnvFile
)

$ErrorActionPreference = 'Stop'

# Resolved from the script's own location, not the current directory, so the script
# works when invoked from anywhere in the tree.
$repoRoot = Split-Path -Parent $PSScriptRoot

if (-not $EnvFile) {
    $EnvFile = Join-Path $repoRoot '.env'
}

if (-not (Test-Path -LiteralPath $EnvFile)) {
    Write-Error "No environment file at $EnvFile. Copy .env.example to .env and fill it in."
}

$loaded = @()
$skipped = 0

foreach ($line in Get-Content -LiteralPath $EnvFile) {

    $trimmed = $line.Trim()

    # Blank lines and comments.
    if ($trimmed -eq '' -or $trimmed.StartsWith('#')) {
        continue
    }

    # Split on the FIRST '=' only. A signing key may legitimately contain one, and
    # splitting on all of them would truncate it silently - the worst kind of wrong,
    # because verification would fail with a valid-looking key in place.
    $i = $trimmed.IndexOf('=')
    if ($i -lt 1) {
        $skipped++
        continue
    }

    $name  = $trimmed.Substring(0, $i).Trim()
    $value = $trimmed.Substring($i + 1).Trim()

    # Strip one matched pair of surrounding quotes if present. .env files vary on this
    # and a quoted key that keeps its quotes produces a signature mismatch, not an error.
    if ($value.Length -ge 2) {
        $first = $value.Substring(0, 1)
        $last  = $value.Substring($value.Length - 1, 1)
        if (($first -eq '"' -and $last -eq '"') -or ($first -eq "'" -and $last -eq "'")) {
            $value = $value.Substring(1, $value.Length - 2)
        }
    }

    Set-Item -Path "Env:$name" -Value $value
    $loaded += $name
}

Write-Host "Loaded $($loaded.Count) variable(s) from $EnvFile into this session:"
foreach ($name in $loaded) {
    Write-Host "  $name"
}

if ($skipped -gt 0) {
    Write-Host "Skipped $skipped line(s) with no '=' separator."
}

Write-Host ""
Write-Host "These last until this terminal closes. Every new terminal needs this again."
