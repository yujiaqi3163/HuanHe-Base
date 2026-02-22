from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    default_limits=["200 per day", "50 per hour"],
    storage_options={
        'socket_connect_timeout': 5,
        'socket_timeout': 10
    }
)

def init_limiter(app):
    """
    初始化 Redis 分布式限流器（延迟绑定模式）
    
    Args:
        app: Flask 应用实例
    """
    limiter.init_app(app)
    
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
