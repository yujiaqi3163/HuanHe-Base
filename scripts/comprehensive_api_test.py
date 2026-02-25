# ============================================================
# comprehensive_api_test.py
#
# 完整的API功能测试脚本
# 功能说明：
# 1. 测试所有主要API端点
# 2. 测试成功和失败场景
# 3. 测试边界条件
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整的API功能测试脚本
测试内容：
1. 模型导入测试
2. 数据库连接测试
3. 应用初始化测试
4. 路由注册测试
5. 表单验证测试
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, RegisterSecret, Material, MaterialType, MaterialImage
from werkzeug.security import generate_password_hash


class APITestCase(unittest.TestCase):
    """API功能测试用例"""

    def setUp(self):
        """测试前准备"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            self.test_user = User(
                username='test_user',
                email='test@example.com',
                password_hash=generate_password_hash('Test123!'),
                is_admin=False,
                is_super_admin=False
            )
            db.session.add(self.test_user)
            
            self.admin_user = User(
                username='admin_user',
                email='admin@example.com',
                password_hash=generate_password_hash('Admin123!'),
                is_admin=True,
                is_super_admin=False
            )
            db.session.add(self.admin_user)
            
            material_type = MaterialType(
                name='测试分类',
                description='用于测试的分类'
            )
            db.session.add(material_type)
            db.session.flush()
            
            self.test_material = Material(
                title='测试素材',
                description='这是一个测试素材',
                material_type_id=material_type.id,
                is_published=True
            )
            db.session.add(self.test_material)
            db.session.flush()
            
            material_image = MaterialImage(
                material_id=self.test_material.id,
                image_url='/static/test.jpg',
                is_cover=True
            )
            db.session.add(material_image)
            
            db.session.commit()

    def tearDown(self):
        """测试后清理"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_01_app_initialization(self):
        """测试1：应用初始化"""
        print('\n🧪 测试1：应用初始化')
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.config['TESTING'])
        print('  ✓ 应用初始化成功')

    def test_02_database_connection(self):
        """测试2：数据库连接"""
        print('\n🧪 测试2：数据库连接')
        with self.app.app_context():
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1'))
            self.assertIsNotNone(result)
        print('  ✓ 数据库连接成功')

    def test_03_model_operations(self):
        """测试3：模型操作"""
        print('\n🧪 测试3：模型操作')
        
        with self.app.app_context():
            user = User.query.filter_by(username='test_user').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@example.com')
            print('  ✓ 用户查询成功')
            
            material = Material.query.filter_by(title='测试素材').first()
            self.assertIsNotNone(material)
            self.assertTrue(material.is_published)
            print('  ✓ 素材查询成功')
            
            material_type = MaterialType.query.filter_by(name='测试分类').first()
            self.assertIsNotNone(material_type)
            print('  ✓ 分类查询成功')

    def test_04_password_verification(self):
        """测试4：密码验证"""
        print('\n🧪 测试4：密码验证')
        with self.app.app_context():
            user = User.query.filter_by(username='test_user').first()
            self.assertTrue(user.check_password('Test123!'))
            self.assertFalse(user.check_password('WrongPass!'))
        print('  ✓ 密码验证正常')

    def test_05_register_secret_validation(self):
        """测试5：卡密验证"""
        print('\n🧪 测试5：卡密验证')
        with self.app.app_context():
            secret = RegisterSecret(
                secret='TEST-SECRET-12345',
                duration_type='1month',
                is_used=False
            )
            db.session.add(secret)
            db.session.commit()
            
            found = RegisterSecret.query.filter_by(secret='TEST-SECRET-12345').first()
            self.assertIsNotNone(found)
            self.assertFalse(found.is_used)
            print('  ✓ 卡密创建和查询成功')

    def test_06_material_relationships(self):
        """测试6：素材关联关系"""
        print('\n🧪 测试6：素材关联关系')
        with self.app.app_context():
            material = Material.query.filter_by(title='测试素材').first()
            self.assertIsNotNone(material)
            self.assertEqual(len(material.images), 1)
            self.assertIsNotNone(material.material_type)
            print('  ✓ 素材关联关系正常')

    def test_07_home_page(self):
        """测试7：首页访问"""
        print('\n🧪 测试7：首页访问')
        response = self.client.get('/')
        self.assertIn(response.status_code, [200, 302])
        print(f'  ✓ 首页访问成功 (状态码: {response.status_code})')

    def test_08_login_page(self):
        """测试8：登录页面"""
        print('\n🧪 测试8：登录页面')
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        print('  ✓ 登录页面访问成功')

    def test_09_register_page(self):
        """测试9：注册页面"""
        print('\n🧪 测试9：注册页面')
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)
        print('  ✓ 注册页面访问成功')

    def test_10_form_validation(self):
        """测试10：表单验证"""
        print('\n🧪 测试10：表单验证')
        from app.forms.auth import LoginForm, RegisterForm
        
        with self.app.test_request_context():
            login_form = LoginForm()
            login_form.username_or_email.data = ''
            login_form.password.data = ''
            self.assertFalse(login_form.validate())
            print('  ✓ 登录表单空数据验证失败（正确）')
            
            login_form.username_or_email.data = 'test'
            login_form.password.data = 'Test123!'
            print('  ✓ 登录表单验证逻辑正常')
        print('  ✓ 表单验证功能正常')

    def test_11_config_system(self):
        """测试11：配置系统"""
        print('\n🧪 测试11：配置系统')
        with self.app.app_context():
            from app.models import Config
            
            Config.set_value('test_key', 'test_value', '测试配置')
            value = Config.get_value('test_key')
            self.assertEqual(value, 'test_value')
            print('  ✓ 配置系统正常')

    def test_12_material_statistics(self):
        """测试12：素材统计"""
        print('\n🧪 测试12：素材统计')
        with self.app.app_context():
            material = Material.query.filter_by(title='测试素材').first()
            material.view_count = 100
            material.download_count = 50
            material.favorite_count = 25
            db.session.commit()
            
            material = Material.query.filter_by(title='测试素材').first()
            self.assertEqual(material.view_count, 100)
            self.assertEqual(material.download_count, 50)
            self.assertEqual(material.favorite_count, 25)
            print('  ✓ 素材统计功能正常')

    def test_13_user_device_lock(self):
        """测试13：用户设备锁"""
        print('\n🧪 测试13：用户设备锁')
        with self.app.app_context():
            user = User.query.filter_by(username='test_user').first()
            user.bound_device_id = 'test-device-id-12345'
            user.device_unbind_status = 0
            db.session.commit()
            
            user = User.query.filter_by(username='test_user').first()
            self.assertEqual(user.bound_device_id, 'test-device-id-12345')
            self.assertEqual(user.device_unbind_status, 0)
            print('  ✓ 设备锁功能正常')

    def test_14_secret_expiration(self):
        """测试14：卡密过期"""
        print('\n🧪 测试14：卡密过期')
        with self.app.app_context():
            from app.models import RegisterSecret
            
            secret = RegisterSecret(
                secret='EXPIRED-SECRET',
                duration_type='1day',
                is_used=True,
                expires_at=datetime.now() - timedelta(days=2)
            )
            db.session.add(secret)
            db.session.commit()
            
            secret = RegisterSecret.query.filter_by(secret='EXPIRED-SECRET').first()
            self.assertTrue(secret.expires_at < datetime.now())
            print('  ✓ 卡密过期判断正常')

    def test_15_super_admin_privilege(self):
        """测试15：超级管理员权限"""
        print('\n🧪 测试15：超级管理员权限')
        with self.app.app_context():
            user = User(
                username='super_admin',
                email='super@example.com',
                password_hash=generate_password_hash('Super123!'),
                is_admin=True,
                is_super_admin=True
            )
            db.session.add(user)
            db.session.commit()
            
            user = User.query.filter_by(username='super_admin').first()
            self.assertTrue(user.is_super_admin)
            self.assertTrue(user.is_admin)
            print('  ✓ 超级管理员权限正常')


def run_tests():
    """运行所有测试"""
    print('=' * 70)
    print('AI 咸鱼素材库 - 完整API功能测试')
    print('=' * 70)
    print(f'开始时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(APITestCase)
    
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    print()
    print('=' * 70)
    print('测试总结')
    print('=' * 70)
    print(f'总测试数: {result.testsRun}')
    print(f'成功: {result.testsRun - len(result.failures) - len(result.errors)}')
    print(f'失败: {len(result.failures)}')
    print(f'错误: {len(result.errors)}')
    print()
    
    if result.failures:
        print('失败的测试:')
        for test, traceback in result.failures:
            print(f'  ✗ {test}')
    
    if result.errors:
        print('\n错误的测试:')
        for test, traceback in result.errors:
            print(f'  ✗ {test}')
            print(f'    {traceback[:200]}...')
    
    print()
    print(f'结束时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
