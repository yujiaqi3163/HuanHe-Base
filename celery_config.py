# Celery 配置文件
import os
from celery import Celery
from dotenv import load_dotenv

# 加载环境变量--从.env文件加载.
load_dotenv()

# 创建 Celery 实例
celery_app = Celery(
    'my_flask_app',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    include=['app.tasks']
)

# Celery 配置
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 单个任务最大执行时间 300 秒
    task_soft_time_limit=240,  # 软时间限制 240 秒
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 自动发现任务
celery_app.autodiscover_tasks(['app'])

if __name__ == '__main__':
    celery_app.start()
