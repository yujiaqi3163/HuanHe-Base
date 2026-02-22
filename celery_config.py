# Celery 配置文件
import os
from celery import Celery
from dotenv import load_dotenv

# 1. 第一步：先加载环境变量，确保后面 os.environ 能读到数据
load_dotenv()

# 2. 第二步：创建 Celery 实例（注意：这里去掉了 include 参数，防止循环导入）
celery_app = Celery(
    'my_flask_app',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# 3. 第三步：配置 Celery 参数
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,        # 单个任务最大执行时间 300 秒
    task_soft_time_limit=240,   # 软时间限制 240 秒
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 4. 第四步：最后加载任务。此时 celery_app 已经完全定义好了
# 这样 app.tasks 导入 celery_app 时，拿到的就是一个完整的对象
celery_app.autodiscover_tasks(['app'])

if __name__ == '__main__':
    celery_app.start()