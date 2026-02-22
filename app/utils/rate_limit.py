from functools import wraps
from flask import request, jsonify, session
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# 内存存储的限流记录
rate_limit_records = {}

def rate_limit(key_prefix, max_requests=5, time_window=60):
    """
    限流装饰器
    
    Args:
        key_prefix: 限流键的前缀，用于区分不同接口
        max_requests: 时间窗口内最大请求次数
        time_window: 时间窗口（秒）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取用户标识（优先使用user_id，其次使用IP）
            from flask_login import current_user
            if current_user and current_user.is_authenticated:
                user_identifier = f"user_{current_user.id}"
            else:
                user_identifier = f"ip_{request.remote_addr}"
            
            # 构建限流键
            rate_key = f"{key_prefix}_{user_identifier}"
            
            now = datetime.now()
            
            # 清理过期的记录
            if rate_key in rate_limit_records:
                # 过滤掉时间窗口外的记录
                rate_limit_records[rate_key] = [
                    t for t in rate_limit_records[rate_key] 
                    if now - t < timedelta(seconds=time_window)
                ]
            
            # 初始化记录列表
            if rate_key not in rate_limit_records:
                rate_limit_records[rate_key] = []
            
            # 检查是否超过限制
            if len(rate_limit_records[rate_key]) >= max_requests:
                logger.warning(f"请求频率超限: {rate_key}")
                return jsonify({
                    'success': False,
                    'message': f'请求过于频繁，请稍后重试（限制{max_requests}次/{time_window}秒）'
                }), 429
            
            # 记录此次请求
            rate_limit_records[rate_key].append(now)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
