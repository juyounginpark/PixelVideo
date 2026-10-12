param([switch]$FreshLogin)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$venvPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
try {
    Write-Host 'PIXELvideo - Instagram sign-in' -ForegroundColor Cyan
    Write-Host 'Enter credentials only in this window. This step does not download Reels.'
    $instagramUsername = (Read-Host 'Instagram username (not email)').Trim().TrimStart('@').ToLowerInvariant()
    if ($instagramUsername -notmatch '^[a-z0-9_.]{1,30}$' -or $instagramUsername -in @('.', '..')) {
        throw 'Invalid Instagram username.'
    }
    if (-not (Test-Path -LiteralPath $venvPython)) {
        throw 'Missing Python environment. Run run_download.ps1 to install it first.'
    }
    $loginArgs = @((Join-Path $PSScriptRoot 'download_reels.py'), '--login', $instagramUsername, '--login-only')
    if ($FreshLogin) { $loginArgs += '--fresh-login' }
    & $venvPython @loginArgs
    if ($LASTEXITCODE -ne 0) {
        throw 'Sign-in did not complete. If Instagram requests verification, finish it in the Instagram app. If rate-limited, retry later.'
    }
    $settingsDirectory = Join-Path $env:LOCALAPPDATA 'PIXELvideo\instagram'
    New-Item -ItemType Directory -Path $settingsDirectory -Force | Out-Null
    @{ username = $instagramUsername; signed_in_at = (Get-Date).ToUniversalTime().ToString('o') } |
        ConvertTo-Json | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $settingsDirectory 'login.json')
    Write-Host 'Sign-in complete. run_download.ps1 will reuse this account.' -ForegroundColor Green
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
}
Read-Host 'Press Enter to close this window' | Out-Null
