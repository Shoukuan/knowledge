<#
Run a safe, guided git-filter-repo workflow on a mirror clone.

This script prints the exact commands and (optionally) runs them.
By default it will NOT push to remote. Use -Execute to perform the local mirror filtering steps.

Usage examples:
  # Dry run (show commands):
  .\scripts\run_git_filter_repo.ps1 -RepoUrl "git@github.com:owner/knowledge.git"

  # Execute the local mirror clone + filter (will NOT push):
  .\scripts\run_git_filter_repo.ps1 -RepoUrl "git@github.com:owner/knowledge.git" -Execute

Prerequisites:
  - git installed
  - git-filter-repo installed and on PATH (recommended)
    install: pip install git-filter-repo

Important: This script will not push changes. After verifying results, perform the push manually following the documented steps.
#>

param(
    [Parameter(Mandatory=$true)] [string]$RepoUrl,
    [string]$MirrorDir = "repo-filter.git",
    [string]$PathsFile = "scripts/paths-to-remove.txt",
    [switch]$Execute
)

function Check-Command($cmd) {
    $proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c where $cmd" -NoNewWindow -PassThru -Wait -ErrorAction SilentlyContinue
    return $proc.ExitCode -eq 0
}

if (-not (Test-Path $PathsFile)) {
    Write-Error "Paths file not found: $PathsFile. Run scripts/remove_large_files.ps1 first."
    exit 1
}

Write-Host "Preparing git-filter-repo workflow"
Write-Host "Repo URL: $RepoUrl"
Write-Host "Mirror directory: $MirrorDir"
Write-Host "Paths file: $PathsFile"

$absPaths = (Resolve-Path $PathsFile).ProviderPath
$pathsArg = "../$($PathsFile -replace '\\','/')"

Write-Host "\nPlanned steps (dry-run):" -ForegroundColor Cyan
Write-Host "1) Create a mirror clone (local backup):`n   git clone --mirror $RepoUrl $MirrorDir" -ForegroundColor Yellow
Write-Host "2) Run git-filter-repo inside the mirror to remove listed paths:`n   cd $MirrorDir`n   git filter-repo --paths-from-file $pathsArg --invert-paths" -ForegroundColor Yellow
Write-Host "3) Cleanup and verify:`n   git reflog expire --expire=now --all`n   git gc --prune=now --aggressive" -ForegroundColor Yellow
Write-Host "4) Inspect results locally. If OK, push changes to remote (manual, with team coordination)." -ForegroundColor Yellow

if (-not $Execute) {
    Write-Host "\nDry-run complete. To perform the local mirror filtering run this script with -Execute." -ForegroundColor Green
    exit 0
}

Write-Host "\nExecuting steps..." -ForegroundColor Green

if (-not (Check-Command 'git')) {
    Write-Error "git not found on PATH. Install git and retry."; exit 1
}

# Optional check for git-filter-repo
try {
    & git filter-repo --help > $null 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Host "Warning: 'git filter-repo' not found; ensure it's installed (pip install git-filter-repo)." -ForegroundColor Yellow }
} catch {
    Write-Host "Warning: Unable to run 'git filter-repo' check; ensure it's installed." -ForegroundColor Yellow
}

if (Test-Path $MirrorDir) {
    Write-Error "Mirror directory '$MirrorDir' already exists. Remove or choose a different MirrorDir."; exit 1
}

Write-Host "Cloning mirror..."
$rc = & git clone --mirror $RepoUrl $MirrorDir
if ($LASTEXITCODE -ne 0) { Write-Error "git clone --mirror failed."; exit 1 }

Push-Location $MirrorDir

Write-Host "Running git-filter-repo (this rewrites history inside mirror)..."
Write-Host "Command: git filter-repo --paths-from-file $pathsArg --invert-paths" -ForegroundColor Cyan

# Run the filter-repo command
& git filter-repo --paths-from-file $pathsArg --invert-paths
if ($LASTEXITCODE -ne 0) { Write-Error "git filter-repo failed."; Pop-Location; exit 1 }

Write-Host "Expiring reflogs and running gc..."
& git reflog expire --expire=now --all
& git gc --prune=now --aggressive

Write-Host "Filtering complete. Mirror is at: $(Resolve-Path .)." -ForegroundColor Green
Write-Host "DO NOT push automatically. Inspect the mirror, verify repository size and integrity, then push to remote with team coordination." -ForegroundColor Yellow
Write-Host "Suggested verification commands:" -ForegroundColor Cyan
Write-Host "  du -sh .    # check pack size (use appropriate tool on Windows)"
Write-Host "  git log --stat --all | grep '<removed-file-name>'  # verify removed files absent" 

Pop-Location

Write-Host "Script finished." -ForegroundColor Green
