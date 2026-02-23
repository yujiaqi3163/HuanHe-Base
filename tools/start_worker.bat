@echo off
chcp 65001 >nul
echo ========================================
echo   Celery Worker 启动脚本
echo ========================================
echo.
echo 正在启动 Celery Worker...
echo.
echo [提示] 请确保：
echo   1. Redis 已启动
echo   2. 虚拟环境已激活
echo.
echo ========================================
echo.

celery -A celery_config worker --loglevel=info --pool=solo

if errorlevel 1 (
    echo.
    echo ========================================
    echo   启动失败！
    echo ========================================
    echo.
    echo 请检查：
    echo   1. Redis 是否在运行
    echo   2. 虚拟环境是否已激活
    echo   3. 依赖是否已安装（pip install -r requirements.txt）
    echo.
)

echo.
pause
