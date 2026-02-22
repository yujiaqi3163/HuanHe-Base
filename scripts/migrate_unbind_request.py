
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User


def migrate_unbind_request():
    """迁移设备解绑申请字段"""
    app = create_app()
    with app.app_context():
        try:
            # 检查字段是否已存在
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'device_unbind_status' not in columns:
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE users ADD COLUMN device_unbind_status INTEGER DEFAULT 0 NOT NULL'))
                    conn.commit()
                print('✅ device_unbind_status 字段添加成功！')
            else:
                print('ℹ️ device_unbind_status 字段已存在，无需添加')
            
            if 'device_unbind_requested_at' not in columns:
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE users ADD COLUMN device_unbind_requested_at DATETIME'))
                    conn.commit()
                print('✅ device_unbind_requested_at 字段添加成功！')
            else:
                print('ℹ️ device_unbind_requested_at 字段已存在，无需添加')
            
            print('🎉 设备解绑申请字段迁移完成！')
            
        except Exception as e:
            print(f'❌ 迁移失败: {str(e)}')
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    migrate_unbind_request()

