param(
    [string]$Login,
    [int]$Count = 3,
    [switch]$RankOnly,
    [switch]$FreshLogin
)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$venvPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    & python -m venv (Join-Path $PSScriptRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Python virtual environment creation failed.' }
}
& $venvPython -c "import instaloader; assert instaloader.__version__ == '4.15.3'"
if ($LASTEXITCODE -ne 0) {
    & $venvPython -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
}
$downloadArgs = @((Join-Path $PSScriptRoot 'download_reels.py'), '--count', $Count)
if (-not $Login) {
    $loginSettings = Join-Path $env:LOCALAPPDATA 'PIXELvideo\instagram\login.json'
    if (Test-Path -LiteralPath $loginSettings) {
        $Login = (Get-Content -Encoding UTF8 -LiteralPath $loginSettings -Raw | ConvertFrom-Json).username
    }
}
if ($Login) { $downloadArgs += @('--login', $Login) }
if ($RankOnly) { $downloadArgs += '--rank-only' }
if ($FreshLogin) { $downloadArgs += '--fresh-login' }
& $venvPython @downloadArgs
exit $LASTEXITCODE
