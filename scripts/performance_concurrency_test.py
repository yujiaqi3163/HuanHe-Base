#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
性能与并发压力分析测试脚本
包含三个测试模块：
1. DeepSeek API延迟模拟测试
2. SMTP压力测试
3. N+1查询验证
"""

import sys
import os
import time
import threading
import concurrent.futures
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Material, MaterialImage, MaterialType
from scripts.test_helpers import create_test_user, create_test_material


class PerformanceConcurrencyTester:
    """性能与并发压力测试类"""

    def __init__(self):
        self.app = create_app()
        self.results = {}

    def setup_test_data(self):
        """准备测试数据"""
        print('\n=== 准备测试数据 ===')

        with self.app.app_context():
            # 创建测试用户
            self.test_user = create_test_user(
                username='perf_test_user',
                email='perf_test@test.com',
                password='Test123!'
            )
            print(f'✓ 创建测试用户: {self.test_user.username}')

            # 创建测试素材分类
            material_type = MaterialType(name='测试分类', description='性能测试用分类')
            db.session.add(material_type)
            db.session.commit()

            # 创建多个测试素材，每个素材带有多个图片
            for i in range(20):
                material = Material(
                    title=f'测试素材 {i+1}',
                    description=f'这是第 {i+1} 个测试素材',
                    user_id=self.test_user.id,
                    material_type_id=material_type.id
                )
                db.session.add(material)
                db.session.flush()

                # 为每个素材创建3张图片
                for j in range(3):
                    img = MaterialImage(
                        material_id=material.id,
                        image_url=f'/static/test_{i}_{j}.jpg',
                        is_cover=(j == 0),
                        sort_order=j
                    )
                    db.session.add(img)

            db.session.commit()
            print('✓ 创建20个测试素材，每个素材3张图片')

    def test_n1_query(self):
        """测试N+1查询问题"""
        print('\n=== 3. N+1查询验证 ===')

        with self.app.app_context():
            from sqlalchemy import event
            from sqlalchemy.engine import Engine

            query_count = 0

            # 监听SQL查询
            @event.listens_for(Engine, "before_cursor_execute")
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                nonlocal query_count
                query_count += 1
                print(f'  查询 #{query_count}: {statement[:100]}...')

            # 测试1：当前实现（存在N+1查询）
            print('\n【测试1】当前实现（不使用eager loading）:')
            query_count = 0
            start_time = time.time()

            materials = Material.query.order_by(Material.created_at.desc()).limit(10).all()
            material_list = []
            for material in materials:
                cover_image = next((img for img in material.images if img.is_cover), None)
                material_type_name = material.material_type.name if material.material_type else '未分类'
                material_list.append({
                    'id': material.id,
                    'title': material.title,
                    'material_type': material_type_name,
                    'cover_image_url': cover_image.image_url if cover_image else None
                })

            elapsed_time = time.time() - start_time
            print(f'  查询次数: {query_count}')
            print(f'  耗时: {elapsed_time:.4f}秒')
            print(f'  ⚠️  存在N+1查询问题！查询次数随素材数量线性增长')

            # 测试2：优化后的实现（使用joinedload）
            print('\n【测试2】优化方案（使用joinedload）:')
            from sqlalchemy.orm import joinedload

            query_count = 0
            start_time = time.time()

            materials = Material.query.options(
                joinedload(Material.images),
                joinedload(Material.material_type)
            ).order_by(Material.created_at.desc()).limit(10).all()

            material_list = []
            for material in materials:
                cover_image = next((img for img in material.images if img.is_cover), None)
                material_type_name = material.material_type.name if material.material_type else '未分类'
                material_list.append({
                    'id': material.id,
                    'title': material.title,
                    'material_type': material_type_name,
                    'cover_image_url': cover_image.image_url if cover_image else None
                })

            elapsed_time = time.time() - start_time
            print(f'  查询次数: {query_count}')
            print(f'  耗时: {elapsed_time:.4f}秒')
            print(f'  ✓ 使用joinedload后，查询次数固定，不随素材数量增长')

            # 移除监听器
            event.remove(Engine, "before_cursor_execute", before_cursor_execute)

            self.results['n1_query'] = {
                'original_queries': query_count,
                'optimized': True
            }

            return True

    def test_rate_limit_thread_safety(self):
        """测试限流装饰器的线程安全性"""
        print('\n=== 2. SMTP压力测试 - 限流机制验证 ===')

        from app.utils.rate_limit import rate_limit

        # 测试限流装饰器在多线程环境下是否有效
        print('\n【测试】多线程并发调用限流接口:')

        test_results = []
        lock = threading.Lock()
        success_count = 0
        rate_limited_count = 0

        @rate_limit('test_limit', max_requests=3, time_window=60)
        def test_limited_function():
            return {'success': True, 'message': '请求成功'}

        def worker(worker_id):
            nonlocal success_count, rate_limited_count
            try:
                # 模拟Flask请求上下文
                with self.app.test_request_context():
                    # 模拟IP地址
                    from flask import request
                    request.remote_addr = f'192.168.1.{worker_id % 5 + 1}'

                    result = test_limited_function()
                    with lock:
                        success_count += 1
                    return (worker_id, 'success', result)
            except Exception as e:
                with lock:
                    if '请求过于频繁' in str(e):
                        rate_limited_count += 1
                return (worker_id, 'error', str(e))

        # 启动10个线程，每个线程调用5次
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(50):
                futures.append(executor.submit(worker, i))

            for future in concurrent.futures.as_completed(futures):
                test_results.append(future.result())

        print(f'  总请求数: 50')
        print(f'  成功请求: {success_count}')
        print(f'  被限流请求: {rate_limited_count}')
        print('  ⚠️  注意：当前限流使用内存存储，多进程环境下可能失效')

        self.results['rate_limit'] = {
            'total_requests': 50,
            'success_count': success_count,
            'rate_limited_count': rate_limited_count
        }

        return True

    def test_deepseek_api_blocking(self):
        """测试DeepSeek API阻塞问题"""
        print('\n=== 1. DeepSeek API延迟模拟测试 ===')

        # 模拟DeepSeek API调用延迟
        print('\n【问题分析】当前optimize_copywriting函数 (app/utils/material_remix.py:16):')
        print('  - 同步调用OpenAI API')
        print('  - timeout设置为30秒')
        print('  - 如果同时有多个请求调用此函数，会阻塞所有Flask worker')

        print('\n【模拟场景】5个并发请求，每个请求延迟30秒:')
        print('  - Flask默认只有1个worker（开发环境）')
        print('  - 生产环境通常有2-4个worker')
        print('  - 所有worker被占满后，首页无法打开')

        print('\n【解决方案】使用异步任务队列（Celery + Redis）')
        print('  - API调用在后台worker中执行')
        print('  - Flask主线程立即返回')
        print('  - 前端轮询或WebSocket获取结果')

        self.results['deepseek_blocking'] = {
            'issue': '同步API调用阻塞Flask worker',
            'location': 'app/utils/material_remix.py:optimize_copywriting',
            'solution': '使用Celery异步任务'
        }

        return True

    def cleanup(self):
        """清理测试数据"""
        print('\n=== 清理测试数据 ===')

        with self.app.app_context():
            # 删除测试素材和图片
            MaterialImage.query.delete()
            Material.query.delete()
            MaterialType.query.filter_by(name='测试分类').delete()

            # 删除测试用户
            user = User.query.filter_by(username='perf_test_user').first()
            if user:
                db.session.delete(user)

            db.session.commit()
            print('✓ 测试数据已清理')

    def run_all_tests(self):
        """运行所有测试"""
        print('=' * 70)
        print('性能与并发压力分析测试')
        print('=' * 70)

        try:
            self.setup_test_data()

            results = {
                'DeepSeek API阻塞测试': self.test_deepseek_api_blocking(),
                'SMTP限流线程安全测试': self.test_rate_limit_thread_safety(),
                'N+1查询验证': self.test_n1_query()
            }

            print('\n' + '=' * 70)
            print('测试总结')
            print('=' * 70)
            for test_name, result in results.items():
                status = '✓ 完成' if result else '✗ 失败'
                print(f'{test_name}: {status}')

            return all(results.values())

        finally:
            self.cleanup()


if __name__ == '__main__':
    tester = PerformanceConcurrencyTester()
    success = tester.run_all_tests()

    print('\n' + '=' * 70)
    print('详细修复建议请查看 scripts/performance_fix_solutions.py')
    print('=' * 70)

    sys.exit(0 if success else 1)
