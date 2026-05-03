@echo off
chcp 65001 >nul
echo ========================================
echo ETF ChatBI 助手 - 快速启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python,请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 检查依赖包...
pip list | findstr "tushare" >nul
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
) else (
    echo [完成] 依赖包已安装
)

echo.
echo [2/4] 检查环境变量配置...
if not exist .env (
    echo [提示] 未找到.env文件,请复制.env.example并配置
    echo        或设置系统环境变量
) else (
    echo [完成] 检测到.env配置文件
)

echo.
echo [3/4] 初始化数据库...
python -c "from database import DatabaseManager; db = DatabaseManager(); db.create_tables(); db.close(); print('[完成] 数据库初始化成功')"

echo.
echo [4/4] 启动Web UI...
echo.
echo ========================================
echo 请在浏览器访问: http://localhost:7860
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python stock_analysis_assistant.py

pause
