@echo off
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>&1 && (
  py -3 -m tools.studio launch
  if errorlevel 1 goto fail
  exit /b 0
)

where python >nul 2>&1 && (
  python -m tools.studio launch
  if errorlevel 1 goto fail
  exit /b 0
)

echo 找不到 Python。请安装后勾选 Add python.exe to PATH。
pause
exit /b 1

:fail
echo 启动失败。可改跑：python -m tools.studio serve
pause
exit /b 1
