param([switch]$NoBrowser, [switch]$Stop)
$ErrorActionPreference = 'Stop'
$appDir = $PSScriptRoot
$url = 'http://127.0.0.1:8766'
Set-Location -LiteralPath $appDir
if ($Stop) {
    $listeners = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort 8766 -State Listen -ErrorAction SilentlyContinue
    foreach ($listener in $listeners) {
        $serverProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($listener.OwningProcess)"
        $expectedScript = Join-Path $appDir 'server.mjs'
        if ($serverProcess.Name -ne 'node.exe' -or -not $serverProcess.CommandLine.Contains($expectedScript)) {
            throw 'Port 8766 belongs to another application; left running.'
        }
        $health = Invoke-RestMethod -Uri "$url/api/health" -TimeoutSec 2
        if ($health.busy) { throw 'Generation is running. Cancel it in the browser before stopping.' }
        Stop-Process -Id $listener.OwningProcess
    }
    Write-Output 'PIXEL voxel local stopped.'
    exit 0
}
if (-not (Test-Path -LiteralPath (Join-Path $appDir 'node_modules/three/package.json'))) {
    & npm.cmd ci --ignore-scripts --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw 'Dependency install failed.' }
}
function Get-AppHealth {
    try { return Invoke-RestMethod -Uri "$url/api/health" -TimeoutSec 2 } catch { return $null }
}
$health = Get-AppHealth
if ($health -and $health.app -ne 'pixel-voxel-local') { throw 'Port 8766 belongs to another application.' }
if (-not $health) {
    $nodePath = (Get-Command node.exe).Source
    $env:VOXEL_CODEX = (Get-Command codex.exe).Source
    $outDir = Join-Path $appDir 'output'
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    $serverPath = Join-Path $appDir 'server.mjs'
    $process = Start-Process -FilePath $nodePath -ArgumentList @('"' + $serverPath + '"') -WorkingDirectory $appDir -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $outDir 'server.log') -RedirectStandardError (Join-Path $outDir 'server-error.log')
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Milliseconds 300
        $health = Get-AppHealth
        if ($health -and $health.app -eq 'pixel-voxel-local') { break }
        if ($process.HasExited) { throw 'Local server failed. See production/voxel_model/output/server-error.log.' }
    }
    if (-not $health) { throw 'Local server did not become ready.' }
}
Write-Output "PIXEL voxel local: $url"
if (-not $NoBrowser) { Start-Process $url }
