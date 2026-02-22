
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User


def migrate_device_lock():
    """迁移设备锁字段"""
    app = create_app()
    with app.app_context():
        try:
            # 检查字段是否已存在
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'bound_device_id' not in columns:
                # 使用 ALTER TABLE 添加字段
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE users ADD COLUMN bound_device_id VARCHAR(200)'))
                    conn.commit()
                print('✅ bound_device_id 字段添加成功！')
            else:
                print('ℹ️ bound_device_id 字段已存在，无需添加')
            
            print('🎉 设备锁迁移完成！')
            
        except Exception as e:
            print(f'❌ 迁移失败: {str(e)}')
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    migrate_device_lock()

