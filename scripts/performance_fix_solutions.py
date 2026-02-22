#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
性能与并发压力 - 修复方案
包含三个问题的具体修复代码：
1. N+1查询优化
2. DeepSeek API异步化
3. 限流机制改进
"""

# ============================================
# 方案1：N+1查询优化
# 路由：/api/latest-materials (app/routes/main/routes.py:500)
# ============================================

def fix_n1_query_example():
    """
    修复N+1查询问题 - 使用joinedload预加载关联数据
    
    修改文件：app/routes/main/routes.py
    修改函数：api_get_latest_materials (line 500)
    """
    from sqlalchemy.orm import joinedload

    # 【优化前】存在N+1查询
    # materials = query.order_by(Material.created_at.desc()).offset(offset).limit(per_page).all()
    # for material in materials:
    #     cover_image = next((img for img in material.images if img.is_cover), None)
    #     material_type_name = material.material_type.name if material.material_type else '未分类'

    # 【优化后】使用joinedload预加载
    materials = query.options(
        joinedload(Material.images),  # 预加载图片关联
        joinedload(Material.material_type)  # 预加载分类关联
    ).order_by(Material.created_at.desc()).offset(offset).limit(per_page).all()

    return materials


# ============================================
# 方案2：DeepSeek API异步化 - 使用Celery
# 函数：optimize_copywriting (app/utils/material_remix.py:16)
# ============================================

CELERY_CONFIG = """
# 在 app/__init__.py 中添加 Celery 配置
from celery import Celery

def create_celery_app(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)
    return celery

# 在 Config 类中添加
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
"""

CELERY_TASKS = """
# 创建文件：app/utils/tasks.py
from celery import shared_task
from app.utils.material_remix import optimize_copywriting as sync_optimize_copywriting
from app.utils.logger import get_logger

logger = get_logger(__name__)

@shared_task(bind=True, max_retries=3)
def optimize_copywriting_task(self, original_text):
    \"\"\"
    异步文案优化任务
    使用 Celery 在后台执行，不阻塞 Flask worker
    \"\"\"
    try:
        result = sync_optimize_copywriting(original_text)
        return {
            'success': True,
            'result': result
        }
    except Exception as e:
        logger.error(f'文案优化任务失败: {e}', exc_info=True)
        self.retry(exc=e, countdown=5)
"""

ASYNC_API_EXAMPLE = """
# 在路由中使用异步任务
@app.route('/api/optimize-copywriting', methods=['POST'])
@login_required
def api_optimize_copywriting():
    \"\"\"
    异步文案优化API
    立即返回任务ID，前端轮询获取结果
    \"\"\"
    from app.utils.tasks import optimize_copywriting_task
    
    data = request.get_json()
    original_text = data.get('text', '')
    
    if not original_text:
        return jsonify({'success': False, 'message': '文案不能为空'}), 400
    
    # 提交异步任务
    task = optimize_copywriting_task.delay(original_text)
    
    return jsonify({
        'success': True,
        'message': '任务已提交',
        'data': {
            'task_id': task.id
        }
    })

@app.route('/api/task-status/<task_id>', methods=['GET'])
@login_required
def api_get_task_status(task_id):
    \"\"\"获取任务状态\"\"\"
    from app.utils.tasks import optimize_copywriting_task
    from celery.result import AsyncResult
    
    task_result = AsyncResult(task_id)
    
    if task_result.state == 'PENDING':
        return jsonify({
            'success': True,
            'status': 'pending',
            'message': '任务处理中...'
        })
    elif task_result.state == 'SUCCESS':
        return jsonify({
            'success': True,
            'status': 'success',
            'data': task_result.result
        })
    elif task_result.state == 'FAILURE':
        return jsonify({
            'success': False,
            'status': 'failure',
            'message': str(task_result.info)
        })
    else:
        return jsonify({
            'success': True,
            'status': task_result.state.lower()
        })
"""


# ============================================
# 方案3：限流机制改进 - 使用Redis实现分布式限流
# 文件：app/utils/rate_limit.py
# ============================================

REDIS_RATE_LIMIT = """
# 改进版限流装饰器 - 使用Redis
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import redis
import os

# Redis连接
redis_client = None

def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_url = os.environ.get('REDIS_URL') or 'redis://localhost:6379/1'
        redis_client = redis.from_url(redis_url)
    return redis_client

def rate_limit_redis(key_prefix, max_requests=5, time_window=60):
    \"\"\"
    基于Redis的分布式限流装饰器
    支持多进程/多worker环境
    \"\"\"
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_login import current_user
            
            # 获取用户标识
            if current_user and current_user.is_authenticated:
                user_identifier = f\"user_{current_user.id}\"
            else:
                user_identifier = f\"ip_{request.remote_addr}\"
            
            rate_key = f\"{key_prefix}:{user_identifier}\"
            r = get_redis_client()
            
            try:
                # 使用Redis管道实现原子操作
                pipe = r.pipeline()
                now = datetime.now()
                
                # 移除时间窗口外的记录
                cutoff = (now - timedelta(seconds=time_window)).timestamp()
                pipe.zremrangebyscore(rate_key, 0, cutoff)
                
                # 获取当前请求数
                pipe.zcard(rate_key)
                
                # 添加新请求
                current_timestamp = now.timestamp()
                pipe.zadd(rate_key, {str(current_timestamp): current_timestamp})
                
                # 设置过期时间
                pipe.expire(rate_key, time_window + 10)
                
                # 执行管道
                _, request_count, _, _ = pipe.execute()
                
                if request_count >= max_requests:
                    return jsonify({
                        'success': False,
                        'message': f'请求过于频繁，请稍后重试（限制{max_requests}次/{time_window}秒）'
                    }), 429
                
            except Exception as e:
                # Redis不可用时降级到内存限流
                from app.utils.rate_limit import rate_limit as memory_rate_limit
                return memory_rate_limit(key_prefix, max_requests, time_window)(f)(*args, **kwargs)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
"""


# ============================================
# 方案4：快速优化 - 不使用Celery的临时方案
# ============================================

THREADING_FALLBACK = """
# 如果暂时不想配置Celery，可以使用线程池作为临时方案
from concurrent.futures import ThreadPoolExecutor
import functools

# 创建全局线程池
executor = ThreadPoolExecutor(max_workers=4)

def async_task(f):
    \"\"\"简单的异步装饰器 - 使用线程池\"\"\"
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        future = executor.submit(f, *args, **kwargs)
        return future
    return wrapper

# 使用示例
@async_task
def optimize_copywriting_async(original_text):
    return optimize_copywriting(original_text)

# 在路由中使用
@app.route('/api/optimize-copywriting', methods=['POST'])
@login_required
def api_optimize_copywriting_simple():
    data = request.get_json()
    original_text = data.get('text', '')
    
    future = optimize_copywriting_async(original_text)
    
    # 可以选择等待结果（仍会阻塞，但线程池有隔离）
    # 或者返回任务ID让前端轮询
    try:
        result = future.result(timeout=10)  # 设置较短的超时
        return jsonify({'success': True, 'data': result})
    except TimeoutError:
        return jsonify({'success': False, 'message': '处理超时，请稍后重试'}), 504
"""


# ============================================
# 应用优化代码
# ============================================

def apply_api_latest_materials_optimization():
    """
    直接修改 app/routes/main/routes.py 中的 api_get_latest_materials 函数
    修复N+1查询问题
    """
    import fileinput
    import os

    file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'app', 'routes', 'main', 'routes.py'
    )

    # 查找并替换代码
    old_code = """    # 查询素材
    query = Material.query

    # 添加搜索条件（按标题搜索）
    if search_keyword:
        query = query.filter(Material.title.contains(search_keyword))

    # 根据排序参数排序
    if sort_by == 'view':
        materials = query.order_by(Material.view_count.desc()).offset(offset).limit(per_page).all()
    elif sort_by == 'favorite':
        materials = query.order_by(Material.favorite_count.desc()).offset(offset).limit(per_page).all()
    elif sort_by == 'download':
        materials = query.order_by(Material.download_count.desc()).offset(offset).limit(per_page).all()
    else:
        materials = query.order_by(Material.created_at.desc()).offset(offset).limit(per_page).all()"""

    new_code = """    # 查询素材 - 使用joinedload预加载关联数据，避免N+1查询
    from sqlalchemy.orm import joinedload
    query = Material.query.options(
        joinedload(Material.images),
        joinedload(Material.material_type)
    )

    # 添加搜索条件（按标题搜索）
    if search_keyword:
        query = query.filter(Material.title.contains(search_keyword))

    # 根据排序参数排序
    if sort_by == 'view':
        materials = query.order_by(Material.view_count.desc()).offset(offset).limit(per_page).all()
    elif sort_by == 'favorite':
        materials = query.order_by(Material.favorite_count.desc()).offset(offset).limit(per_page).all()
    elif sort_by == 'download':
        materials = query.order_by(Material.download_count.desc()).offset(offset).limit(per_page).all()
    else:
        materials = query.order_by(Material.created_at.desc()).offset(offset).limit(per_page).all()"""

    print("【提示】请手动修改 app/routes/main/routes.py 中的 api_get_latest_materials 函数")
    print("将查询部分替换为使用 joinedload 的版本")
    print("\n需要添加的导入:")
    print("from sqlalchemy.orm import joinedload")


if __name__ == '__main__':
    print("=" * 70)
    print("性能与并发压力 - 修复方案")
    print("=" * 70)
    print("\n【方案概览】")
    print("1. N+1查询优化 - 使用joinedload")
    print("2. DeepSeek API异步化 - 使用Celery + Redis")
    print("3. 限流机制改进 - 使用Redis分布式限流")
    print("\n【快速修复】")
    apply_api_latest_materials_optimization()
    print("\n【详细代码】")
    print("请查看本文件中的各个方案代码段")
    print("=" * 70)
