@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0production\voxel_model\launch.ps1" -Stop
if errorlevel 1 pause
