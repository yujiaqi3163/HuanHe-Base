# ============================================================
# list_users.py
# 
# 列出所有用户账号信息
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User


def list_users():
    app = create_app()
    
    with app.app_context():
        print('=' * 80)
        print('所有用户账号列表')
        print('=' * 80)
        print()
        
        users = User.query.all()
        
        if not users:
            print('没有找到用户账号')
            return
        
        print(f'  {"ID":<4} {"用户名":<20} {"邮箱":<30} {"超级管理员":<10} {"管理员":<10}')
        print('  ' + '-' * 80)
        
        for user in users:
            is_super = '✅' if user.is_super_admin else '❌'
            is_admin = '✅' if user.is_admin else '❌'
            print(f'  {user.id:<4} {user.username:<20} {user.email:<30} {is_super:<10} {is_admin:<10}')
        
        print()
        print('=' * 80)
        print(f'总计: {len(users)} 个用户')
        print('=' * 80)


if __name__ == '__main__':
    list_users()
