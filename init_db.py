from app import create_app, db
from app.models import User, RegisterSecret
from datetime import datetime


def init_database():
    app = create_app()
    
    with app.app_context():
        db.create_all()
        print("数据库表创建成功！")
        
        if RegisterSecret.query.count() == 0:
            secrets = [
                'SECRET2025-ADMIN',
                'SECRET2025-USER001',
                'SECRET2025-USER002',
                'SECRET2025-USER003'
            ]
            for secret in secrets:
                register_secret = RegisterSecret(secret=secret)
                db.session.add(register_secret)
            db.session.commit()
            print("注册卡密添加成功！")
        else:
            print("注册卡密已存在，跳过添加。")
        
        if User.query.count() == 0:
            sample_users = [
                User(
                    username='admin',
                    email='admin@example.com',
                    password='admin123',
                    is_admin=True,
                    is_super_admin=True
                ),
                User(
                    username='demo',
                    email='demo@example.com',
                    password='demo123',
                    is_admin=False,
                    is_super_admin=False
                ),
                User(
                    username='test',
                    email='test@example.com',
                    password='test123',
                    is_admin=False,
                    is_super_admin=False
                )
            ]
            db.session.add_all(sample_users)
            db.session.flush()
            
            used_secrets = [
                ('SECRET2025-ADMIN', sample_users[0]),
                ('SECRET2025-USER001', sample_users[1]),
                ('SECRET2025-USER002', sample_users[2])
            ]
            for secret, user in used_secrets:
                rs = RegisterSecret.query.filter_by(secret=secret).first()
                if rs:
                    rs.is_used = True
                    rs.user_id = user.id
                    rs.used_at = datetime.utcnow()
            
            db.session.commit()
            print("示例用户添加成功！")
        else:
            print("数据库已有用户数据，跳过添加。")
        
        print(f"\n当前注册卡密数量: {RegisterSecret.query.count()}")
        print(f"当前用户数量: {User.query.count()}")
        
        print("\n卡密使用状态:")
        for rs in RegisterSecret.query.all():
            status = "已使用" if rs.is_used else "未使用"
            user_info = f" (用户: {rs.user.username})" if rs.user else ""
            print(f"  {rs.secret} - {status}{user_info}")


if __name__ == '__main__':
    init_database()
