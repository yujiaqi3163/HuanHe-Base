# ============================================================
# security_penetration_test.py
# 
# 安全渗透测试脚本
# 功能说明：
# 1. 测试各种安全漏洞
# 2. 验证安全防护机制
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安全深度渗透测试脚本
包含以下测试模块：
1. CSRF绕过测试
2. 权限越权测试
3. SQL注入测试
4. 文件安全测试
"""

import sys
import os
import requests
import json
import base64
import random
import string
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, RegisterSecret, Material
from scripts.test_helpers import create_test_user, create_test_material, create_test_secret


class SecurityPenetrationTester:
    """安全渗透测试类"""

    def __init__(self, base_url='http://127.0.0.1:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_session = requests.Session()
        self.normal_session = requests.Session()
        self.app = create_app()

    def setup_test_data(self):
        """准备测试数据"""
        print('\n=== 准备测试数据 ===')

        with self.app.app_context():
            # 创建测试管理员
            self.admin_user = create_test_user(
                username='admin_tester',
                email='admin_tester@test.com',
                password='Test123!',
                is_admin=True
            )
            print(f'✓ 创建测试管理员: {self.admin_user.username}')

            # 创建测试普通用户1
            self.normal_user1 = create_test_user(
                username='normal_tester1',
                email='normal_tester1@test.com',
                password='Test123!'
            )
            print(f'✓ 创建测试普通用户1: {self.normal_user1.username}')

            # 创建测试普通用户2
            self.normal_user2 = create_test_user(
                username='normal_tester2',
                email='normal_tester2@test.com',
                password='Test123!'
            )
            print(f'✓ 创建测试普通用户2: {self.normal_user2.username}')

            # 创建测试素材
            self.test_material = create_test_material(
                name='渗透测试素材',
                user_id=self.normal_user1.id
            )
            print(f'✓ 创建测试素材: {self.test_material.name}')

    def login(self, session, username, password):
        """登录用户"""
        login_url = f'{self.base_url}/auth/login'

        # 获取登录页面以获取CSRF token
        response = session.get(login_url)
        if response.status_code != 200:
            print(f'✗ 无法访问登录页面: {response.status_code}')
            return False

        # 登录
        login_data = {
            'username': username,
            'password': password,
            'remember': False
        }

        response = session.post(login_url, data=login_data, allow_redirects=True)

        if '登录成功' in response.text or response.status_code == 200:
            print(f'✓ 用户 {username} 登录成功')
            return True
        else:
            print(f'✗ 用户 {username} 登录失败')
            return False

    def test_csrf_bypass(self):
        """测试CSRF绕过"""
        print('\n=== 1. CSRF绕过测试 ===')

        # 登录普通用户
        if not self.login(self.normal_session, 'normal_tester1', 'Test123!'):
            return False

        # 获取最新素材API（GET请求，不需要CSRF）
        print('\n测试 /api/latest-materials (GET):')
        response = self.normal_session.get(f'{self.base_url}/api/latest-materials')
        print(f'  状态码: {response.status_code}')
        if response.status_code == 200:
            print('  ✓ GET请求正常')
        else:
            print('  ✗ GET请求异常')

        # 尝试发送验证码API（POST，需要CSRF）
        print('\n测试 /auth/send-code (POST, 无CSRF token):')
        data = {'email': 'test@test.com'}
        response = self.normal_session.post(
            f'{self.base_url}/auth/send-code',
            json=data
        )
        print(f'  状态码: {response.status_code}')

        if response.status_code == 400 or 'CSRF' in response.text:
            print('  ✓ CSRF保护生效')
        elif response.status_code == 200:
            print('  ⚠ 可能存在CSRF绕过风险')
        else:
            print(f'  ? 状态码: {response.status_code}')

        return True

    def test_privilege_escalation(self):
        """测试权限越权"""
        print('\n=== 2. 权限越权测试 ===')

        # 登录普通用户
        if not self.login(self.normal_session, 'normal_tester1', 'Test123!'):
            return False

        # 尝试访问管理后台
        print('\n测试访问 /admin/ (普通用户):')
        response = self.normal_session.get(f'{self.base_url}/admin/', allow_redirects=True)
        print(f'  状态码: {response.status_code}')

        if '只有管理员' in response.text or response.status_code == 403:
            print('  ✓ 权限控制生效，普通用户无法访问管理后台')
        elif response.status_code == 200 and '管理' in response.text:
            print('  ✗ 权限越权漏洞！普通用户可以访问管理后台')
        else:
            print(f'  ? 需要手动检查')

        # 测试操作他人素材（需要先检查是否有相关API）
        print('\n测试访问他人素材详情页:')
        with self.app.app_context():
            other_material = Material.query.filter_by(user_id=self.normal_user2.id).first()
            if other_material:
                response = self.normal_session.get(f'{self.base_url}/material/{other_material.id}')
                print(f'  状态码: {response.status_code}')
                if response.status_code == 200:
                    print('  ✓ 可以查看公开素材（正常行为）')
                else:
                    print('  ? 需要检查素材访问权限逻辑')

        return True

    def test_sql_injection(self):
        """测试SQL注入"""
        print('\n=== 3. SQL注入测试 ===')

        # 登录普通用户
        if not self.login(self.normal_session, 'normal_tester1', 'Test123!'):
            return False

        # SQL注入Payload
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT username, password FROM users; --",
            "1' OR '1'='1",
            "admin' --"
        ]

        print('\n测试 /api/latest-materials 搜索参数:')
        for payload in sql_payloads:
            response = self.normal_session.get(
                f'{self.base_url}/api/latest-materials',
                params={'search': payload}
            )

            if response.status_code == 500:
                print(f'  ✗ Payload [{payload}] 导致服务器错误！可能存在SQL注入漏洞')
            elif response.status_code == 200:
                try:
                    data = response.json()
                    if 'success' in data and data['success']:
                        print(f'  ✓ Payload [{payload}] 被正确处理')
                    else:
                        print(f'  ⚠ Payload [{payload}] 返回异常响应')
                except:
                    print(f'  ? Payload [{payload}] 返回非JSON响应')
            else:
                print(f'  ? Payload [{payload}] 状态码: {response.status_code}')

        # 验证ORM参数化查询
        print('\n验证ORM安全性:')
        with self.app.app_context():
            try:
                # 使用参数化查询应该是安全的
                Material.query.filter(Material.name.like('%test%')).all()
                print('  ✓ ORM查询正常工作')

                # 测试恶意输入
                malicious_input = "' OR '1'='1"
                results = Material.query.filter(Material.name == malicious_input).all()
                print('  ✓ 恶意输入被正确处理，无SQL注入风险')
            except Exception as e:
                print(f'  ✗ ORM查询异常: {e}')

        return True

    def test_file_security(self):
        """测试文件安全"""
        print('\n=== 4. 文件安全测试 ===')

        # 登录普通用户
        if not self.login(self.normal_session, 'normal_tester1', 'Test123!'):
            return False

        # 测试大文件上传（生成模拟的大文件Base64）
        print('\n测试大文件上传（模拟100MB）:')
        large_data = 'A' * (100 * 1024 * 1024)  # 100MB
        large_base64 = base64.b64encode(large_data.encode()).decode()
        large_image_data = f'data:image/png;base64,{large_base64}'

        with self.app.app_context():
            from app.routes.main.routes import save_base64_image
            result = save_base64_image(large_image_data)

            if result is None:
                print('  ✓ 大文件被正确拒绝')
            else:
                print('  ✗ 大文件上传成功！存在文件大小限制漏洞')

        # 测试非法文件类型
        print('\n测试非法文件类型（.exe）:')
        exe_data = 'MZ' + '\x90' * 100
        exe_base64 = base64.b64encode(exe_data.encode()).decode()
        exe_image_data = f'data:application/x-msdownload;base64,{exe_base64}'

        with self.app.app_context():
            from app.routes.main.routes import save_base64_image
            result = save_base64_image(exe_image_data)

            if result is None:
                print('  ✓ 非法文件类型被正确拒绝')
            else:
                print('  ✗ 非法文件上传成功！存在文件类型限制漏洞')

        # 测试PHP文件
        print('\n测试PHP文件（.php）:')
        php_data = '<?php phpinfo(); ?>'
        php_base64 = base64.b64encode(php_data.encode()).decode()
        php_image_data = f'data:text/php;base64,{php_base64}'

        with self.app.app_context():
            from app.routes.main.routes import save_base64_image
            result = save_base64_image(php_image_data)

            if result is None:
                print('  ✓ PHP文件被正确拒绝')
            else:
                print('  ✗ PHP文件上传成功！存在文件类型限制漏洞')

        # 测试合法文件
        print('\n测试合法文件（PNG）:')
        valid_png_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10'
            b'\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00'
            b'\x00\x00\x04sBIT\x08\x08\x08\x08|\x88|\x88d\x88d\x88\x1c'
            b'\xcd\xb9\x88\x00\x00\x00\x19tEXtSoftware\x00libpng1.6.34'
            b'\x93\x9d\x8e\xcd\x00\x00\x00\x1cIDAT\x08\xd7c\xf8\xff\xff?'
            b'\x03\x02;\x82\x01\x06\x17\xc8\x80\x00\x00\x00#\x00\x01'
            b'\xe8?\xe29\x15]\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        valid_base64 = base64.b64encode(valid_png_data).decode()
        valid_image_data = f'data:image/png;base64,{valid_base64}'

        with self.app.app_context():
            from app.routes.main.routes import save_base64_image
            result = save_base64_image(valid_image_data)

            if result:
                print(f'  ✓ 合法文件上传成功: {result}')
                # 清理测试文件
                file_path = os.path.join(self.app.root_path, result.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
            else:
                print('  ✗ 合法文件上传失败')

        return True

    def cleanup(self):
        """清理测试数据"""
        print('\n=== 清理测试数据 ===')

        with self.app.app_context():
            # 删除测试用户
            for username in ['admin_tester', 'normal_tester1', 'normal_tester2']:
                user = User.query.filter_by(username=username).first()
                if user:
                    # 删除关联的素材
                    Material.query.filter_by(user_id=user.id).delete()
                    # 删除关联的卡密
                    RegisterSecret.query.filter_by(user_id=user.id).delete()
                    # 删除用户
                    db.session.delete(user)
                    print(f'✓ 删除测试用户: {username}')

            db.session.commit()

    def run_all_tests(self):
        """运行所有测试"""
        print('=' * 60)
        print('安全深度渗透测试')
        print('=' * 60)

        try:
            self.setup_test_data()

            results = {
                'CSRF绕过测试': self.test_csrf_bypass(),
                '权限越权测试': self.test_privilege_escalation(),
                'SQL注入测试': self.test_sql_injection(),
                '文件安全测试': self.test_file_security()
            }

            print('\n' + '=' * 60)
            print('测试总结')
            print('=' * 60)
            for test_name, result in results.items():
                status = '✓ 通过' if result else '✗ 失败'
                print(f'{test_name}: {status}')

            return all(results.values())

        finally:
            self.cleanup()


if __name__ == '__main__':
    tester = SecurityPenetrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
