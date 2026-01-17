<#
PowerShell helper to prepare a list of paths to remove from Git history.

Usage (dry-run, non-destructive):
  1. Review reports/large_files.csv
  2. Run: .\scripts\remove_large_files.ps1 -CsvPath reports/large_files.csv -OutPaths scripts/paths-to-remove.txt
  3. Inspect scripts/paths-to-remove.txt, convert backslashes to forward slashes if needed
  4. Follow instructions in scripts/git_history_cleanup.md to run git-filter-repo or BFG

Notes:
 - This script only prepares the paths file and optionally creates a mirror backup clone.
 - It will NOT run `git filter-repo` or push to remote.
#>

param(
    [string]$CsvPath = "reports/large_files.csv",
    [string]$OutPaths = "scripts/paths-to-remove.txt",
    [string]$RepoUrl = "",
    [switch]$CreateMirrorBackup
)

if (-not (Test-Path $CsvPath)) {
    Write-Error "CSV not found: $CsvPath"
    exit 1
}

$lines = Get-Content $CsvPath | Select-Object -Skip 1
$paths = @()
foreach ($l in $lines) {
    if ($l.Trim() -eq '') { continue }
    $cols = $l -split ',',3
    $p = $cols[0]
    # Normalize to forward slashes for git-filter-repo compatibility
    $p = $p -replace '\\','/'
    $paths += $p
}

# Write unique sorted paths
$unique = $paths | Sort-Object -Unique
$dir = Split-Path $OutPaths -Parent
if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
$unique | Out-File -FilePath $OutPaths -Encoding utf8
Write-Host "Wrote $(($unique).Count) paths to $OutPaths"

if ($CreateMirrorBackup) {
    if ([string]::IsNullOrEmpty($RepoUrl)) {
        Write-Error "Repo URL must be provided for mirror backup (use -RepoUrl)."
        exit 1
    }
    $mirrorDir = "repo-backup.git"
    Write-Host "Creating mirror clone: git clone --mirror $RepoUrl $mirrorDir"
    git clone --mirror $RepoUrl $mirrorDir
    if ($LASTEXITCODE -ne 0) { Write-Error "git clone failed"; exit 1 }
    Write-Host "Mirror clone created at: $mirrorDir"
    Write-Host "Next: cd $mirrorDir and run git filter-repo using $OutPaths (see scripts/git_history_cleanup.md)"
}

Write-Host "Script finished. Inspect $OutPaths and follow git_history_cleanup.md for next steps."
