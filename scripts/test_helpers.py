#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试辅助函数模块
提供创建测试数据的辅助函数
"""

import os
import sys
import random
import string
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, RegisterSecret, Material, UserMaterial
from werkzeug.security import generate_password_hash


def generate_random_string(length=8):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def create_test_user(username=None, email=None, password='Test123!', is_admin=False, is_super_admin=False):
    """
    创建测试用户
    
    Args:
        username: 用户名（可选，自动生成）
        email: 邮箱（可选，自动生成）
        password: 密码
        is_admin: 是否为管理员
        is_super_admin: 是否为超级管理员
    
    Returns:
        User对象
    """
    if not username:
        username = f'test_user_{generate_random_string(6)}'
    if not email:
        email = f'{username}@test.com'
    
    # 检查用户是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return existing_user
    
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        is_admin=is_admin,
        is_super_admin=is_super_admin
    )
    
    db.session.add(user)
    db.session.commit()
    
    return user


def create_test_secret(secret=None, expires_at=None, is_used=False, user_id=None):
    """
    创建测试卡密
    
    Args:
        secret: 卡密字符串（可选，自动生成）
        expires_at: 过期时间（可选，默认30天后）
        is_used: 是否已使用
        user_id: 绑定的用户ID
    
    Returns:
        RegisterSecret对象
    """
    if not secret:
        secret = generate_random_string(16).upper()
    
    if not expires_at:
        expires_at = datetime.now() + timedelta(days=30)
    
    register_secret = RegisterSecret(
        secret=secret,
        expires_at=expires_at,
        is_used=is_used,
        user_id=user_id
    )
    
    db.session.add(register_secret)
    db.session.commit()
    
    return register_secret


def create_test_material(name=None, description='测试素材描述', user_id=None):
    """
    创建测试素材
    
    Args:
        name: 素材名称（可选，自动生成）
        description: 素材描述
        user_id: 创建者用户ID
    
    Returns:
        Material对象
    """
    if not name:
        name = f'测试素材_{generate_random_string(6)}'
    
    material = Material(
        name=name,
        description=description,
        user_id=user_id,
        view_count=0,
        download_count=0
    )
    
    db.session.add(material)
    db.session.commit()
    
    return material


def create_test_user_material(user_id, material_id, name=None):
    """
    创建测试用户素材
    
    Args:
        user_id: 用户ID
        material_id: 原始素材ID
        name: 素材名称（可选）
    
    Returns:
        UserMaterial对象
    """
    if not name:
        name = f'用户素材_{generate_random_string(6)}'
    
    user_material = UserMaterial(
        user_id=user_id,
        material_id=material_id,
        name=name
    )
    
    db.session.add(user_material)
    db.session.commit()
    
    return user_material


def init_test_db():
    """初始化测试数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建测试用户
        test_user = create_test_user(
            username='demo_user',
            email='demo@test.com',
            password='Demo123!'
        )
        
        # 创建测试管理员
        admin_user = create_test_user(
            username='demo_admin',
            email='admin@test.com',
            password='Admin123!',
            is_admin=True
        )
        
        # 创建测试卡密
        create_test_secret(user_id=test_user.id)
        
        # 创建测试素材
        create_test_material(user_id=admin_user.id)
        
        print('测试数据库初始化完成！')
        print(f'测试用户: demo_user / Demo123!')
        print(f'测试管理员: demo_admin / Admin123!')


if __name__ == '__main__':
    init_test_db()
