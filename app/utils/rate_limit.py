from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

limiter = None

def init_limiter(app):
    """
    初始化 Redis 分布式限流器
    
    Args:
        app: Flask 应用实例
    """
    global limiter
    
    # 从环境变量获取 Redis URL，默认使用本地 Redis
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # 初始化限流器
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=redis_url,
        default_limits=["200 per day", "50 per hour"],
        storage_options={
            'socket_connect_timeout': 5,
            'socket_timeout': 10
        }
    )
    
    # 注册全局错误处理器
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """
        限流错误统一处理
        返回 JSON 格式：{"code": 429, "msg": "创作太频繁，请稍后再试"}
        """
        return {
            "code": 429,
            "msg": "创作太频繁，请稍后再试"
        }, 429
    
    return limiter

def get_limiter():
    """
    获取限流器实例
    
    Returns:
        Limiter: 限流器实例
    """
    return limiter
