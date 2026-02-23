# ============================================================
# diagnose_celery.py
# 
# Celery 诊断工具
# 功能说明：
# 1. 检查环境变量配置
# 2. 检查 Redis 连接
# 3. 检查 Celery 配置
# 4. 检查任务模块
# 5. 提供启动建议
# ============================================================

import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print('='*60)
print('Flask + Celery 诊断工具')
print('='*60)

# 1. 检查环境变量
print('\n[1/6] 检查环境变量...')
from dotenv import load_dotenv
load_dotenv()

required_env_vars = [
    'SECRET_KEY',
    'CELERY_BROKER_URL',
    'CELERY_RESULT_BACKEND',
    'REDIS_URL'
]

for var in required_env_vars:
    value = os.environ.get(var)
    status = '✅' if value else '❌'
    print(f'{status} {var}: {value or "未设置"}')

# 2. 检查 Redis 连接
print('\n[2/6] 检查 Redis 连接...')
try:
    import redis
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    r = redis.from_url(redis_url)
    r.ping()
    print('✅ Redis 连接成功')
    
    # 检查 Redis 中的任务
    print(f'   Redis 中现有键数量: {len(r.keys())}')
except Exception as e:
    print(f'❌ Redis 连接失败: {e}')
    print('   请确保 Redis 已启动！')

# 3. 检查 Celery 配置
print('\n[3/6] 检查 Celery 配置...')
try:
    from celery_config import celery_app
    print(f'✅ Celery 实例创建成功')
    print(f'   Broker: {celery_app.conf.broker_url}')
    print(f'   Backend: {celery_app.conf.result_backend}')
except Exception as e:
    print(f'❌ Celery 配置错误: {e}')

# 4. 检查任务模块
print('\n[4/6] 检查任务模块...')
try:
    from app import tasks
    print('✅ 任务模块导入成功')
    
    # 检查任务是否注册
    if hasattr(tasks, 'async_remix_material'):
        print('✅ async_remix_material 任务存在')
    else:
        print('❌ async_remix_material 任务不存在')
except Exception as e:
    print(f'❌ 任务模块导入失败: {e}')

# 5. 检查 Celery Worker 状态
print('\n[5/6] 检查 Celery Worker...')
print('⚠️  请确保在另一个终端运行:')
print('   celery -A celery_config worker --loglevel=info')
print('')
print('   如果没有运行 Worker，任务将一直处于 PENDING 状态！')

# 6. 快速测试
print('\n[6/6] 快速测试建议...')
print('1. 启动 Redis: redis-server')
print('2. 启动 Celery Worker: celery -A celery_config worker --loglevel=info')
print('3. 启动 Flask: python run.py')
print('4. 然后再测试二创功能')

print('\n' + '='*60)
print('诊断完成！')
print('='*60)
