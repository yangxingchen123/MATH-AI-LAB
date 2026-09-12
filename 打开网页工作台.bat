@echo off
chcp 65001 >nul
cd /d "%~dp0"

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":3000 .*LISTENING"') do (
  echo 端口 3000 已有服务，直接打开浏览器。
  start "" "http://127.0.0.1:3000/"
  exit /b 0
)

where node >nul 2>&1
if errorlevel 1 goto studio

if not exist "node_modules\" (
  echo 正在安装 Node 依赖...
  call npm ci
  if errorlevel 1 (
    echo 依赖安装失败，回退 tools.studio。
    goto studio
  )
)

if exist "apps\web\.next\BUILD_ID" (
  echo 启动网页界面...
  start "MATH-AI-LAB Web" cmd /c "npm run start --workspace=@math-ai-lab/web"
) else (
  echo 尚未构建生产包，启动开发服务。
  start "MATH-AI-LAB Web" cmd /c "npm run dev"
)

timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:3000/"
exit /b 0

:studio
echo Node 不可用，回退 tools.studio。
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

echo 找不到 Node 或 Python。
pause
exit /b 1

:fail
echo 网页工作台未能启动。可改跑：打开旧版工作台.bat
pause
exit /b 1
