#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
超级管理员初始化脚本
创建或更新超级管理员账号，邮箱：2798479668@qq.com
超级管理员跳过设备锁验证
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User


def create_super_admin():
    """创建或更新超级管理员"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('超级管理员初始化')
        print('=' * 60)
        
        # 超级管理员配置
        admin_username = 'admin'
        admin_email = '2798479668@qq.com'
        admin_password = 'Aa123456!'
        
        print(f'\n用户名: {admin_username}')
        print(f'邮箱: {admin_email}')
        print(f'密码: {admin_password}')
        print('状态: 超级管理员（跳过设备锁验证）\n')
        
        # 检查是否已存在（优先按邮箱）
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            print('ℹ️  找到已存在的管理员账号（按邮箱），正在更新...')
            existing_admin.username = admin_username
            existing_admin.password = admin_password
            existing_admin.is_admin = True
            existing_admin.is_super_admin = True
            existing_admin.bound_device_id = None  # 清除设备绑定
            db.session.commit()
            print('✅ 管理员账号已更新')
        else:
            # 检查用户名是否已存在
            existing_by_username = User.query.filter_by(username=admin_username).first()
            if existing_by_username:
                print('ℹ️  找到已存在的管理员账号（按用户名），正在更新...')
                existing_by_username.email = admin_email
                existing_by_username.password = admin_password
                existing_by_username.is_admin = True
                existing_by_username.is_super_admin = True
                existing_by_username.bound_device_id = None  # 清除设备绑定
                db.session.commit()
                print('✅ 管理员账号已更新')
            else:
                print('📝 创建新的超级管理员账号...')
                admin = User(
                    username=admin_username,
                    email=admin_email,
                    is_admin=True,
                    is_super_admin=True
                )
                admin.password = admin_password
                db.session.add(admin)
                db.session.commit()
                print('✅ 超级管理员账号创建成功')
        
        print('\n' + '=' * 60)
        print('🎉 超级管理员初始化完成！')
        print('=' * 60)
        print('\n登录信息:')
        print(f'  用户名: {admin_username}')
        print(f'  邮箱: {admin_email}')
        print(f'  密码: {admin_password}')
        print('\n特性:')
        print('  ✅ 超级管理员权限')
        print('  ✅ 跳过设备锁验证（可在任意设备登录）')
        print('  ✅ 可访问管理后台所有功能\n')
        
        return True


if __name__ == '__main__':
    success = create_super_admin()
    if not success:
        sys.exit(1)
