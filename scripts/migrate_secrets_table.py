import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入必要的模块
from app import create_app, db
from app.models import RegisterSecret

def migrate_secrets_table():
    """迁移 register_secrets 表，添加新字段"""
    app = create_app()
    
    with app.app_context():
        conn = db.engine.connect()
        
        # 获取表的列信息
        result = conn.execute(db.text("PRAGMA table_info(register_secrets)"))
        columns = [row[1] for row in result]
        
        print(f"当前表的列: {columns}")
        
        # 检查并添加 duration_type 列
        if 'duration_type' not in columns:
            print('添加 duration_type 列...')
            conn.execute(db.text("ALTER TABLE register_secrets ADD COLUMN duration_type VARCHAR(20) DEFAULT 'permanent' NOT NULL"))
            print('duration_type 列添加成功')
        
        # 检查并添加 expires_at 列
        if 'expires_at' not in columns:
            print('添加 expires_at 列...')
            conn.execute(db.text("ALTER TABLE register_secrets ADD COLUMN expires_at DATETIME"))
            print('expires_at 列添加成功')
        
        # 更新现有数据的默认值
        print('更新现有卡密数据...')
        conn.execute(db.text("UPDATE register_secrets SET duration_type = 'permanent' WHERE duration_type IS NULL"))
        
        conn.commit()
        print('数据更新完成')
        
        print('\n✅ 数据库迁移完成！')

if __name__ == '__main__':
    migrate_secrets_table()
