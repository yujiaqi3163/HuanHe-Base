import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db

def migrate_user_material_tables():
    """迁移用户二创素材表"""
    app = create_app()
    
    with app.app_context():
        try:
            # 尝试直接创建表
            db.create_all()
            print('✅ 用户二创素材表创建成功！')
            
        except Exception as e:
            print(f'⚠️ 创建表时出错: {e}')
            print('尝试另一种方式...')
            
            try:
                # 检查表是否存在，如果不存在则创建
                with db.engine.connect() as conn:
                    # 检查 user_materials 表
                    result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_materials'"))
                    if not result.fetchone():
                        print('创建 user_materials 表...')
                        conn.execute(db.text("""
                            CREATE TABLE user_materials (
                                id INTEGER PRIMARY KEY,
                                user_id INTEGER NOT NULL,
                                original_material_id INTEGER,
                                title VARCHAR(200) NOT NULL,
                                description TEXT,
                                original_description TEXT,
                                view_count INTEGER DEFAULT 0 NOT NULL,
                                download_count INTEGER DEFAULT 0 NOT NULL,
                                created_at DATETIME,
                                FOREIGN KEY (user_id) REFERENCES users (id),
                                FOREIGN KEY (original_material_id) REFERENCES materials (id)
                            )
                        """))
                        print('user_materials 表创建成功')
                    
                    # 检查 user_material_images 表
                    result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_material_images'"))
                    if not result.fetchone():
                        print('创建 user_material_images 表...')
                        conn.execute(db.text("""
                            CREATE TABLE user_material_images (
                                id INTEGER PRIMARY KEY,
                                user_material_id INTEGER NOT NULL,
                                image_url VARCHAR(500) NOT NULL,
                                sort_order INTEGER DEFAULT 0 NOT NULL,
                                is_cover BOOLEAN DEFAULT 0 NOT NULL,
                                original_image_url VARCHAR(500),
                                css_recipe TEXT,
                                created_at DATETIME,
                                FOREIGN KEY (user_material_id) REFERENCES user_materials (id)
                            )
                        """))
                        print('user_material_images 表创建成功')
                    
                    conn.commit()
                    print('✅ 数据库迁移完成！')
                    
            except Exception as e2:
                print(f'❌ 迁移失败: {e2}')

if __name__ == '__main__':
    migrate_user_material_tables()
