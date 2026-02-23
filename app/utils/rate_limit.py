# ============================================================
# rate_limit.py
# 
# Redis 分布式限流模块
# 功能说明：
# 1. 基于 Flask-Limiter 实现分布式限流
# 2. 使用 Redis 作为存储后端（支持多进程/多服务器）
# 3. 统一 429 错误处理，显示等待时间
# 4. 支持多种限流规则（X per minute, X per second）
# ============================================================

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import json
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()


def custom_rate_limit_error_handler(e):
    """
    自定义限流错误处理器
    返回 JSON 格式：{"code": 429, "msg": "创作太频繁，请等待X秒后再试"}
    """
    import re
    
    logger.info('=== 自定义限流错误处理器被触发 ===')
    logger.info(f'原始错误: {str(e)}')
    logger.info(f'错误类型: {type(e)}')
    
    # 尝试从错误描述中提取等待时间
    wait_seconds = 60  # 默认等待60秒
    
    # 解析 Flask-Limiter 的错误信息，例如：
    # "429 Too Many Requests: 2 per 1 minute"
    # "Too Many Requests: 3 per 60 seconds"
    error_msg = str(e)
    
    # 尝试匹配 "X per Y minute(s)" 或 "X per Y second(s)"
    per_minute_match = re.search(r'(\d+)\s+per\s+(\d+)\s*minute', error_msg, re.IGNORECASE)
    per_second_match = re.search(r'(\d+)\s+per\s+(\d+)\s*second', error_msg, re.IGNORECASE)
    
    if per_minute_match:
        # 每分钟 X 次，等待时间约为 (60 / X) 秒
        limit_count = int(per_minute_match.group(1))
        time_window = int(per_minute_match.group(2))
        wait_seconds = max(int((time_window * 60) / limit_count), 1)
    elif per_second_match:
        # 每秒 X 次，等待时间约为 (Y / X) 秒
        limit_count = int(per_second_match.group(1))
        time_window = int(per_second_match.group(2))
        wait_seconds = max(int(time_window / limit_count), 1)
    else:
        # 如果无法解析，使用默认值
        # 根据常见的限流规则推断：
        if "5 per 1 minute" in error_msg:
            wait_seconds = 12
        elif "3 per 1 minute" in error_msg:
            wait_seconds = 20
        elif "2 per 1 minute" in error_msg:
            wait_seconds = 30
    
    logger.info(f'计算的等待时间: {wait_seconds}秒')
    
    from flask import jsonify
    response = jsonify({
        "code": 429,
        "msg": f"创作太频繁，请等待{wait_seconds}秒后再试"
    })
    response.status_code = 429
    
    logger.info(f'返回响应: {response.get_json()}')
    
    return response


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    default_limits=["200 per day", "50 per hour"],
    storage_options={
        'socket_connect_timeout': 30,
        'socket_timeout': 60,
        'retry_on_timeout': True,
        'health_check_interval': 0
    },
    default_limits_exempt_when=lambda: False
)


def init_limiter(app):
    """
    初始化 Redis 分布式限流器（延迟绑定模式）
    
    Args:
        app: Flask 应用实例
    """
    logger.info('=== 初始化限流器 ===')
    limiter.init_app(app)
    
    # 注册 Flask 全局错误处理器（这是最可靠的方式）
    @app.errorhandler(429)
    def global_ratelimit_handler(e):
        logger.info('=== Flask 全局 429 错误处理器被触发 ===')
        return custom_rate_limit_error_handler(e)
