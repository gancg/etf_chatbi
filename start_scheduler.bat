@echo off
chcp 65001 >nul
echo ========================================
echo ETF ChatBI 调度器 - 后台启动
echo ========================================
echo.

REM 检查是否已经在运行
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "scheduler" >nul
if %errorlevel% equ 0 (
    echo [警告] 调度器可能已经在运行
    echo.
    choice /C YN /M "是否重新启动"
    if errorlevel 2 exit /b
)

echo [1/3] 启动调度器(后台运行)...
start /B python scheduler.py

echo [2/3] 等待初始化...
timeout /t 3 /nobreak >nul

echo [3/3] 检查启动状态...
if exist scheduler.log (
    echo.
    echo [成功] 调度器已启动
    echo.
    echo 查看日志: type scheduler.log
    echo 实时监控: Get-Content scheduler.log -Wait -Tail 20
    echo.
    echo 停止调度器: taskkill /F /IM python.exe
) else (
    echo.
    echo [提示] 正在启动,请稍候检查scheduler.log
)

echo.
echo ========================================
pause
