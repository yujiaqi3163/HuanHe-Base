# ============================================================
# fix_email_conflict.py
# 
# 解决邮箱冲突问题
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User


def fix_conflict():
    app = create_app()
    
    with app.app_context():
        print('=' * 80)
        print('解决邮箱冲突')
        print('=' * 80)
        print()
        
        # 1. 先把 yujiaqi3163 的邮箱改成其他的
        user_yujiaqi = User.query.filter_by(username='yujiaqi3163').first()
        if user_yujiaqi:
            user_yujiaqi.email = 'yujiaqi3163_old@qq.com'
            print('  ✅ yujiaqi3163 邮箱已改为: yujiaqi3163_old@qq.com')
        
        # 2. 然后更新 pc_yujiaqi 和 pe_yujiaqi 的邮箱
        updates = [
            ('pc_yujiaqi', '2798479668@qq.com'),
            ('pe_yujiaqi', 'aa13178775196@163.com')
        ]
        
        for username, email in updates:
            user = User.query.filter_by(username=username).first()
            if user:
                old_email = user.email
                user.email = email
                print(f'  ✅ {username}: {old_email} → {email}')
        
        db.session.commit()
        
        print()
        print('=' * 80)
        print('完成！')
        print('=' * 80)
        
        # 显示最终结果
        print()
        print('最终用户列表:')
        print('  ' + '-' * 80)
        users = User.query.all()
        print(f'  {"ID":<4} {"用户名":<20} {"邮箱":<30} {"超级管理员":<10}')
        print('  ' + '-' * 80)
        for u in users:
            is_super = '✅' if u.is_super_admin else '❌'
            print(f'  {u.id:<4} {u.username:<20} {u.email:<30} {is_super:<10}')


if __name__ == '__main__':
    fix_conflict()
