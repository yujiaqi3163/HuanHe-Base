# ============================================================
# update_admin_emails.py
# 
# 更新现有超级管理员的邮箱地址
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User


def update_emails():
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('更新超级管理员邮箱')
        print('=' * 60)
        print()
        
        # 账号和邮箱映射
        email_updates = [
            ('pc_yujiaqi', '2798479668@qq.com'),
            ('pe_yujiaqi', 'aa13178775196@163.com')
        ]
        
        updated_count = 0
        
        for username, new_email in email_updates:
            user = User.query.filter_by(username=username).first()
            if user:
                old_email = user.email
                if old_email != new_email:
                    user.email = new_email
                    print(f'  ✅ {username}: {old_email} → {new_email}')
                    updated_count += 1
                else:
                    print(f'  ℹ️ {username}: 邮箱已是 {new_email}，无需更新')
            else:
                print(f'  ❌ {username}: 账号不存在')
        
        if updated_count > 0:
            db.session.commit()
            print()
            print(f'🎉 共更新 {updated_count} 个邮箱')
        else:
            print()
            print('没有需要更新的邮箱')
        
        print('=' * 60)


if __name__ == '__main__':
    update_emails()
