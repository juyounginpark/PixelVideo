param([ValidateSet('msedge', 'chrome')][string]$Browser = 'msedge')
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$venvPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    & python -m venv (Join-Path $PSScriptRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Python environment setup failed.' }
}
& $venvPython -c "import playwright, instaloader"
if ($LASTEXITCODE -ne 0) {
    & $venvPython -m pip install -r (Join-Path $PSScriptRoot 'requirements-browser.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Browser login dependencies failed to install.' }
}
& $venvPython (Join-Path $PSScriptRoot 'browser_login.py') --browser $Browser
exit $LASTEXITCODE
