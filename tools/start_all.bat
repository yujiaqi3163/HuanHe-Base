@echo off
chcp 65001 >nul
echo ========================================
echo   Flask 项目完整启动工具
echo ========================================
echo.
echo [提示] 此脚本需要你手动在多个终端中启动服务
echo.
echo ========================================
echo   步骤 1：检查并启动 Redis
echo ========================================
echo.
echo 请确保 Redis 已启动！
echo.
echo 如果 Redis 未安装，请先安装 Redis：
echo   - 下载：https://github.com/microsoftarchive/redis/releases
echo   - 或者使用 Memurai（Windows 版 Redis）
echo.
echo 或者使用 Docker 启动 Redis：
echo   docker run -d -p 6379:6379 redis:alpine
echo.
pause

echo.
echo ========================================
echo   步骤 2：启动 Celery Worker
echo ========================================
echo.
echo 请在新的终端窗口中运行：
echo   celery -A celery_config worker --loglevel=info --pool=solo
echo.
echo 或者双击运行：start_worker.bat
echo.
pause

echo.
echo ========================================
echo   步骤 3：启动 Flask 应用
echo ========================================
echo.
echo 请在新的终端窗口中运行：
echo   python run.py
echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo 访问地址：http://127.0.0.1:5000
echo.
pause
