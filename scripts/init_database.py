#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化与迁移整合脚本
一键创建数据库并执行所有必要的迁移
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import (
    User, Config, MaterialType, Material, MaterialImage,
    RegisterSecret, UserMaterial, UserMaterialImage
)


def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('开始初始化数据库...')
        print('=' * 60)
        
        # 1. 创建所有表
        print('\n[步骤 1/7] 创建数据库表...')
        try:
            db.create_all()
            print('✅ 数据库表创建成功！')
        except Exception as e:
            print(f'❌ 创建表失败: {e}')
            return False
        
        # 2. 迁移用户表
        print('\n[步骤 2/7] 迁移用户表...')
        migrate_user_table()
        
        # 3. 迁移设备锁字段
        print('\n[步骤 3/7] 迁移设备锁字段...')
        migrate_device_lock()
        
        # 4. 迁移解绑申请字段
        print('\n[步骤 4/7] 迁移解绑申请字段...')
        migrate_unbind_request()
        
        # 5. 迁移卡密表
        print('\n[步骤 5/7] 迁移卡密表...')
        migrate_secrets_table()
        
        # 6. 迁移用户素材表
        print('\n[步骤 6/7] 迁移用户素材表...')
        migrate_user_material_tables()
        
        # 7. 初始化配置表
        print('\n[步骤 7/7] 初始化配置表...')
        init_config_table()
        
        print('\n' + '=' * 60)
        print('🎉 数据库初始化完成！')
        print('=' * 60)
        
        return True


def migrate_user_table():
    """迁移用户表，添加avatar、bio、gender、birthday字段"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            if 'avatar' not in columns:
                conn.execute(db.text("ALTER TABLE users ADD COLUMN avatar VARCHAR(500)"))
                print('  ✅ 添加 avatar 列')
            
            if 'bio' not in columns:
                conn.execute(db.text("ALTER TABLE users ADD COLUMN bio VARCHAR(200)"))
                print('  ✅ 添加 bio 列')
            
            if 'gender' not in columns:
                conn.execute(db.text("ALTER TABLE users ADD COLUMN gender VARCHAR(10)"))
                print('  ✅ 添加 gender 列')
            
            if 'birthday' not in columns:
                conn.execute(db.text("ALTER TABLE users ADD COLUMN birthday DATE"))
                print('  ✅ 添加 birthday 列')
            
            conn.commit()
            print('  ✅ 用户表迁移完成')
    except Exception as e:
        print(f'  ℹ️ 用户表迁移跳过或已完成: {e}')


def migrate_device_lock():
    """迁移设备锁字段"""
    try:
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'bound_device_id' not in columns:
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN bound_device_id VARCHAR(200)'))
                conn.commit()
            print('  ✅ 添加 bound_device_id 列')
        else:
            print('  ℹ️ bound_device_id 已存在')
    except Exception as e:
        print(f'  ℹ️ 设备锁迁移跳过: {e}')


def migrate_unbind_request():
    """迁移解绑申请字段"""
    try:
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        added = False
        
        if 'device_unbind_status' not in columns:
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN device_unbind_status INTEGER DEFAULT 0'))
                conn.commit()
            print('  ✅ 添加 device_unbind_status 列')
            added = True
        
        if 'device_unbind_requested_at' not in columns:
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE users ADD COLUMN device_unbind_requested_at DATETIME'))
                conn.commit()
            print('  ✅ 添加 device_unbind_requested_at 列')
            added = True
        
        if not added:
            print('  ℹ️ 解绑申请字段已存在')
    except Exception as e:
        print(f'  ℹ️ 解绑申请迁移跳过: {e}')


def migrate_secrets_table():
    """迁移卡密表"""
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(register_secrets)"))
            columns = [row[1] for row in result]
            
            if 'duration_type' not in columns:
                conn.execute(db.text("ALTER TABLE register_secrets ADD COLUMN duration_type VARCHAR(20) DEFAULT 'permanent'"))
                print('  ✅ 添加 duration_type 列')
            
            if 'expires_at' not in columns:
                conn.execute(db.text("ALTER TABLE register_secrets ADD COLUMN expires_at DATETIME"))
                print('  ✅ 添加 expires_at 列')
            
            conn.execute(db.text("UPDATE register_secrets SET duration_type = 'permanent' WHERE duration_type IS NULL"))
            conn.commit()
            print('  ✅ 卡密表迁移完成')
    except Exception as e:
        print(f'  ℹ️ 卡密表迁移跳过: {e}')


def migrate_user_material_tables():
    """迁移用户素材表"""
    try:
        db.create_all()
        print('  ✅ 用户素材表已就绪')
    except Exception as e:
        print(f'  ℹ️ 用户素材表迁移跳过: {e}')


def init_config_table():
    """初始化配置表"""
    try:
        default_configs = [
            ('customer_service_wechat', 'your_kefu_wechat', '客服微信号')
        ]
        
        for key, value, description in default_configs:
            if not Config.query.filter_by(key=key).first():
                config = Config(key=key, value=value, description=description)
                db.session.add(config)
                print(f'  ✅ 添加默认配置: {key}')
        
        db.session.commit()
        print('  ✅ 配置表初始化完成')
    except Exception as e:
        print(f'  ℹ️ 配置表初始化跳过: {e}')


def create_sample_data():
    """创建示例数据（可选）"""
    app = create_app()
    
    with app.app_context():
        print('\n' + '=' * 60)
        print('创建示例数据...')
        print('=' * 60)
        
        # 创建示例分类
        print('\n[1/4] 创建示例分类...')
        if not MaterialType.query.first():
            types = [
                MaterialType(name='朋友圈', description='朋友圈素材', sort_order=1),
                MaterialType(name='小红书', description='小红书素材', sort_order=2),
                MaterialType(name='抖音', description='抖音素材', sort_order=3)
            ]
            db.session.add_all(types)
            db.session.commit()
            print('  ✅ 示例分类创建成功')
        else:
            print('  ℹ️ 分类已存在，跳过')
        
        # 创建超级管理员
        print('\n[2/4] 创建超级管理员...')
        if not User.query.filter_by(is_super_admin=True).first():
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_super_admin=True
            )
            admin.password = 'Aa123456!'
            db.session.add(admin)
            db.session.commit()
            print('  ✅ 超级管理员创建成功')
            print('  用户名: admin')
            print('  密码: Aa123456!')
        else:
            print('  ℹ️ 超级管理员已存在，跳过')
        
        # 创建测试卡密
        print('\n[3/4] 创建测试卡密...')
        if not RegisterSecret.query.first():
            secrets = [
                RegisterSecret(secret='sk-test-permanent-001', duration_type='permanent'),
                RegisterSecret(secret='sk-test-1year-001', duration_type='1year'),
                RegisterSecret(secret='sk-test-1month-001', duration_type='1month'),
                RegisterSecret(secret='sk-test-1day-001', duration_type='1day')
            ]
            db.session.add_all(secrets)
            db.session.commit()
            print('  ✅ 测试卡密创建成功')
            print('  sk-test-permanent-001 (永久)')
            print('  sk-test-1year-001 (1年)')
            print('  sk-test-1month-001 (1个月)')
            print('  sk-test-1day-001 (1天)')
        else:
            print('  ℹ️ 卡密已存在，跳过')
        
        print('\n' + '=' * 60)
        print('🎉 示例数据创建完成！')
        print('=' * 60)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--sample':
        success = init_database()
        if success:
            create_sample_data()
    else:
        print('使用方法:')
        print('  python scripts/init_database.py          # 仅初始化数据库')
        print('  python scripts/init_database.py --sample # 初始化数据库并创建示例数据\n')
        
        confirm = input('是否初始化数据库？(y/n): ')
        if confirm.lower() == 'y':
            init_database()
