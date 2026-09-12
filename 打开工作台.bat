@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在打开 MATH-AI-LAB 工作台...
call "%~dp0tools\qt_workbench\launch.cmd"
if errorlevel 1 (
  echo.
  echo 启动失败。日志：
  echo   %TEMP%\math-ai-lab-qt-launch.log
  echo 也可先安装窗口组件：
  echo   python -m pip install -r tools\qt_workbench\requirements.txt
  pause
  exit /b 1
)
exit /b 0
