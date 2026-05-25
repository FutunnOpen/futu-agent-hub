# Futu Skills Hub CLI — Windows PowerShell installer
# Usage (PowerShell):
#   iwr -useb "https://raw.githubusercontent.com/FutunnOpen/futu-agent-hub/feature/v202060511-add-skill/futu-install.ps1" | iex
#
# Override remote git repo:
#   $env:FUTU_SKILLHUB_REPO_URL  = "https://github.com/FutunnOpen/futu-agent-hub"
#   $env:FUTU_SKILLHUB_REPO_REF  = "feature/v202060511-add-skill"
#   $env:FUTU_SKILLHUB_REPO_PATH = "manager"

$ErrorActionPreference = "Stop"

$HubHome = "$env:USERPROFILE\.futu-skillhub"
$CliDest = "$HubHome\futu-skill-manager"
$BinDir  = "$env:USERPROFILE\.local\bin"
$Wrapper = "$BinDir\futu-skills.bat"

$FallbackRepoUrl  = "https://github.com/FutunnOpen/futu-agent-hub"
$FallbackRepoRef  = "feature/v202060511-add-skill"
$FallbackRepoPath = "manager"

$RemoteRepoUrl  = if ($env:FUTU_SKILLHUB_REPO_URL)  { $env:FUTU_SKILLHUB_REPO_URL  } else { $FallbackRepoUrl  }
$RemoteRepoRef  = if ($env:FUTU_SKILLHUB_REPO_REF)  { $env:FUTU_SKILLHUB_REPO_REF  } else { $FallbackRepoRef  }
$RemoteRepoPath = if ($env:FUTU_SKILLHUB_REPO_PATH) { $env:FUTU_SKILLHUB_REPO_PATH } else { $FallbackRepoPath }

function Die([string]$msg) {
    Write-Error "error: $msg"
    exit 1
}

# Detect Python 3 (python3 first, then python if it is Python 3)
$Python = $null
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $Python = "python3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    try {
        $ver = & python -c "import sys; print(sys.version_info[0])" 2>$null
        if ([string]$ver.Trim() -eq "3") { $Python = "python" }
    } catch {}
}
if (-not $Python) {
    Die "Python 3 is required. Install from https://python.org and ensure it is on PATH."
}
Write-Host "Using Python: $Python"

# Create install directories
New-Item -ItemType Directory -Force -Path $CliDest | Out-Null
New-Item -ItemType Directory -Force -Path $BinDir  | Out-Null

# Clone CLI from remote repo
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Die "git is required to clone the CLI"
}
Write-Host "Cloning CLI from: $RemoteRepoUrl (ref $RemoteRepoRef)"
$TmpRepo = Join-Path $env:TEMP "futu-skill-manager-$(New-Guid)"
git clone --depth=1 --branch $RemoteRepoRef $RemoteRepoUrl $TmpRepo
if ($LASTEXITCODE -ne 0) { Die "git clone failed" }

$Src = if ($RemoteRepoPath) { Join-Path $TmpRepo $RemoteRepoPath } else { $TmpRepo }
if (-not (Test-Path $Src)) {
    Remove-Item -Recurse -Force $TmpRepo -ErrorAction SilentlyContinue
    Die "cli_repo_path not found in repo: $RemoteRepoPath"
}
Copy-Item -Recurse -Force (Join-Path $Src "*") $CliDest
Remove-Item -Recurse -Force $TmpRepo -ErrorAction SilentlyContinue

# Write .bat wrapper — works in both CMD and PowerShell
$batContent = "@echo off`r`n$Python `"%USERPROFILE%\.futu-skillhub\futu-skill-manager\futu_skills.py`" %*`r`n"
[System.IO.File]::WriteAllText($Wrapper, $batContent, [System.Text.Encoding]::ASCII)

# Smoke test
$smokeOut = & $Python "$CliDest\futu_skills.py" --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Smoke test OK: $smokeOut"
} else {
    Die "CLI smoke test failed"
}

# Add BinDir to user PATH (persistent)
$userPath = [Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::User)
if ($userPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$BinDir;$userPath", [System.EnvironmentVariableTarget]::User)
    Write-Host "Added $BinDir to user PATH (takes effect in new shells)"
}
# Also update current session immediately
$env:PATH = "$BinDir;$env:PATH"

# Refresh discovery skill
& $Wrapper refresh-discovery 2>$null | Out-Null

Write-Host ""
Write-Host "Installed: $Wrapper"
Write-Host ""
Write-Host "To use futu-skills right away in this session, run:"
Write-Host "  `$env:PATH = `"$BinDir;`$env:PATH`""
Write-Host ""
Write-Host "Try: futu-skills search news"
Write-Host "     futu-skills detect"
Write-Host "     npx skills add futu-news-search"
Write-Host ""
Write-Host "[CLI_PATH] $Wrapper"
