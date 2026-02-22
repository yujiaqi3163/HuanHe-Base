#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
在现有数据库中添加权限表
保留所有现有数据，只添加权限相关表和数据
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Permission


def add_permissions():
    """添加权限表"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('在现有数据库中添加权限表')
        print('=' * 60)
        
        # 1. 创建权限相关表
        print('\n[1/2] 创建权限表...')
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'permissions' not in tables:
                db.create_all()
                print('✅ 权限表创建成功')
            else:
                print('ℹ️ 权限表已存在')
                
            if 'user_permissions' not in tables:
                db.create_all()
                print('✅ 用户权限关联表创建成功')
            else:
                print('ℹ️ 用户权限关联表已存在')
        except Exception as e:
            print(f'❌ 创建表失败: {e}')
            return False
        
        # 2. 初始化默认权限
        print('\n[2/2] 初始化默认权限...')
        try:
            default_permissions = [
                ('material_manage', '素材管理', '管理素材库的素材'),
                ('secret_manage', '卡密管理', '管理注册卡密'),
                ('user_manage', '用户管理', '管理系统用户'),
                ('type_manage', '分类管理', '管理素材分类'),
                ('config_manage', '设置客服微信', '设置客服微信号')
            ]
            
            added_count = 0
            for code, name, description in default_permissions:
                existing = Permission.query.filter_by(code=code).first()
                if existing:
                    print(f'  ℹ️ {name} 已存在')
                else:
                    perm = Permission(code=code, name=name, description=description)
                    db.session.add(perm)
                    added_count += 1
                    print(f'  ✅ 添加 {name}')
            
            db.session.commit()
            
            if added_count > 0:
                print(f'✅ 成功添加 {added_count} 个权限')
            else:
                print('ℹ️ 所有权限已存在')
                
        except Exception as e:
            print(f'❌ 初始化权限失败: {e}')
            db.session.rollback()
            return False
        
        print('\n' + '=' * 60)
        print('🎉 权限表添加完成！')
        print('=' * 60)
        print('\n所有现有数据已保留！')
        print('现在可以使用权限管理功能了。\n')
        
        return True


if __name__ == '__main__':
    success = add_permissions()
    if not success:
        sys.exit(1)
