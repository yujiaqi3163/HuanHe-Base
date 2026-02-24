# ============================================================
# create_admin.py
# 
# 只创建超级管理员账号的脚本
# 功能说明：
# 1. 仅创建指定的超级管理员账号
# 2. 不会影响或清除现有数据库数据
# 3. 检查账号是否已存在，避免重复创建
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
只创建超级管理员账号的独立脚本
不清除任何现有数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User


def create_super_admins():
    """创建超级管理员账号（不清除任何数据）"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('创建超级管理员账号')
        print('=' * 60)
        print()
        
        # 定义要创建的超级管理员列表
        super_admins = [
            {
                'username': 'pc_yujiaqi',
                'email': '2798479668@qq.com',
                'password': 'Yun803163'
            },
            {
                'username': 'pe_yujiaqi',
                'email': 'aa13178775196@163.com',
                'password': 'Yun803163'
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for admin_info in super_admins:
            username = admin_info['username']
            email = admin_info['email']
            password = admin_info['password']
            
            # 检查用户名是否已存在
            existing_by_username = User.query.filter_by(username=username).first()
            
            if existing_by_username:
                print(f'  ℹ️ 账号 "{username}" 已存在')
                
                # 更新用户信息
                existing_by_username.is_super_admin = True
                existing_by_username.is_admin = True
                existing_by_username.password = password
                
                # 如果邮箱不同，尝试更新邮箱
                if existing_by_username.email != email:
                    # 检查新邮箱是否被其他用户占用
                    existing_by_email = User.query.filter_by(email=email).first()
                    if existing_by_email and existing_by_email.id != existing_by_username.id:
                        print(f'  ⚠️  邮箱 "{email}" 已被用户 "{existing_by_email.username}" 占用，跳过更新邮箱')
                    else:
                        old_email = existing_by_username.email
                        existing_by_username.email = email
                        print(f'  ✅ 更新邮箱: {old_email} → {email}')
                
                db.session.commit()
                print(f'  ✅ 已更新 "{username}" 的密码和权限')
                skipped_count += 1
                continue
            
            # 用户名不存在，检查邮箱是否已被占用
            existing_by_email = User.query.filter_by(email=email).first()
            
            if existing_by_email:
                print(f'  ⚠️  邮箱 "{email}" 已被用户 "{existing_by_email.username}" 占用，跳过创建账号 "{username}"')
                skipped_count += 1
                continue
            
            # 用户名和邮箱都不存在，正常创建新账号
            admin = User(
                username=username,
                email=email,
                is_admin=True,
                is_super_admin=True
            )
            admin.password = password
            db.session.add(admin)
            
            print(f'  ✅ 创建超级管理员: {username}')
            created_count += 1
        
        # 提交更改
        if created_count > 0:
            db.session.commit()
        
        print()
        print('=' * 60)
        print('账号信息:')
        print('=' * 60)
        
        for admin_info in super_admins:
            print(f'  账号: {admin_info["username"]}')
            print(f'  密码: {admin_info["password"]}')
            print()
        
        print('=' * 60)
        if created_count > 0:
            print(f'🎉 完成！共创建 {created_count} 个新账号')
        if skipped_count > 0:
            print(f'  跳过 {skipped_count} 个已存在的账号')
        print('=' * 60)
        
        return True


if __name__ == '__main__':
    print()
    print('⚠️  注意：此脚本不会清除任何现有数据！')
    print()
    
    confirm = input('确认创建超级管理员账号？(y/n): ')
    if confirm.lower() == 'y':
        try:
            success = create_super_admins()
            if success:
                sys.exit(0)
            else:
                sys.exit(1)
        except Exception as e:
            print(f'\n❌ 出错: {e}')
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print('已取消操作')
        sys.exit(0)
