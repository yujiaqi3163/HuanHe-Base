import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db

def migrate_user_table():
    app = create_app()
    
    with app.app_context():
        try:
            # 尝试直接添加列（SQLite）
            with db.engine.connect() as conn:
                # 检查 avatar 列是否存在
                result = conn.execute(db.text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                
                if 'avatar' not in columns:
                    print('添加 avatar 列...')
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN avatar VARCHAR(500)"))
                    print('avatar 列添加成功')
                
                if 'bio' not in columns:
                    print('添加 bio 列...')
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN bio VARCHAR(200)"))
                    print('bio 列添加成功')
                
                if 'gender' not in columns:
                    print('添加 gender 列...')
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN gender VARCHAR(10)"))
                    print('gender 列添加成功')
                
                if 'birthday' not in columns:
                    print('添加 birthday 列...')
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN birthday DATE"))
                    print('birthday 列添加成功')
                
                conn.commit()
                print('数据库迁移成功！')
                
        except Exception as e:
            print(f'迁移出错: {e}')
            print('尝试其他方式...')
            
            try:
                # 如果上面的方法失败，尝试使用 db.session.execute
                db.session.execute(db.text("ALTER TABLE users ADD COLUMN avatar VARCHAR(500)"))
                db.session.execute(db.text("ALTER TABLE users ADD COLUMN bio VARCHAR(200)"))
                db.session.execute(db.text("ALTER TABLE users ADD COLUMN gender VARCHAR(10)"))
                db.session.execute(db.text("ALTER TABLE users ADD COLUMN birthday DATE"))
                db.session.commit()
                print('数据库迁移成功！')
            except Exception as e2:
                print(f'第二种方法也失败: {e2}')
                print('如果表已经有这些列，请忽略此错误')

if __name__ == '__main__':
    migrate_user_table()
