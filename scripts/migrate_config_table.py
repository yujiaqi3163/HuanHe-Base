# ============================================================
# migrate_config_table.py
# 
# 配置表迁移脚本
# 功能说明：
# 1. 迁移系统配置数据
# ============================================================

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Config


def migrate_config_table():
    """迁移配置表"""
    app = create_app()
    with app.app_context():
        try:
            # 创建所有表（包含configs表）
            db.create_all()
            print('✅ 配置表创建成功！')
            
            # 初始化默认配置
            default_configs = [
                ('customer_service_wechat', 'your_kefu_wechat', '客服微信号')
            ]
            
            for key, value, description in default_configs:
                if not Config.query.filter_by(key=key).first():
                    config = Config(key=key, value=value, description=description)
                    db.session.add(config)
                    print(f'✅ 添加默认配置: {key} = {value}')
            
            db.session.commit()
            print('🎉 配置表迁移完成！')
            
        except Exception as e:
            print(f'❌ 迁移失败: {str(e)}')
            import traceback
            traceback.print_exc()
            
            # 备用方案：直接执行SQL
            try:
                from sqlalchemy import text
                with db.engine.connect() as conn:
                    # 检查表是否存在
                    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='configs'"))
                    if not result.fetchone():
                        conn.execute(text("""
                            CREATE TABLE configs (
                                id INTEGER PRIMARY KEY,
                                key VARCHAR(100) UNIQUE NOT NULL,
                                value TEXT,
                                description VARCHAR(200),
                                created_at DATETIME NOT NULL,
                                updated_at DATETIME NOT NULL
                            )
                        """))
                        conn.commit()
                        print('✅ 配置表创建成功（备用方案）！')
                        
                        # 插入默认数据
                        from datetime import datetime
                        now = datetime.utcnow()
                        conn.execute(
                            text("INSERT INTO configs (key, value, description, created_at, updated_at) VALUES (:key, :value, :description, :now, :now)"),
                            {'key': 'customer_service_wechat', 'value': 'your_kefu_wechat', 'description': '客服微信号', 'now': now}
                        )
                        conn.commit()
                        print('✅ 默认配置添加成功！')
            except Exception as e2:
                print(f'❌ 备用方案也失败: {str(e2)}')


if __name__ == '__main__':
    migrate_config_table()
