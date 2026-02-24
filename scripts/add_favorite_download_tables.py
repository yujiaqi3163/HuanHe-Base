import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import UserFavorite, UserDownload

app = create_app()

with app.app_context():
    print('正在创建新表...')
    db.create_all()
    print('✅ UserFavorite 和 UserDownload 表创建成功！')
