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
            
            # 检查账号是否已存在
            existing_user = User.query.filter_by(username=username).first()
            
            if existing_user:
                print(f'  ℹ️ 账号 "{username}" 已存在，跳过创建')
                
                # 确保是超级管理员
                if not existing_user.is_super_admin:
                    existing_user.is_super_admin = True
                    existing_user.is_admin = True
                    db.session.commit()
                    print(f'  ✅ 已将 "{username}" 升级为超级管理员')
                
                skipped_count += 1
                continue
            
            # 创建新账号
            admin = User(
                username=username,
                email=admin_info['email'],
                is_admin=True,
                is_super_admin=True
            )
            admin.password = admin_info['password']
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
