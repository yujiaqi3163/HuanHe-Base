# ============================================================
# diagnose_bt.py
# 
# 宝塔服务器环境诊断脚本
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

print('=' * 80)
print('宝塔服务器环境诊断')
print('=' * 80)
print()

# 1. 检查当前目录
print('[1/6] 检查当前目录...')
current_dir = os.getcwd()
print(f'  当前目录: {current_dir}')

# 2. 检查脚本目录
print()
print('[2/6] 检查脚本位置...')
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
print(f'  脚本目录: {script_dir}')
print(f'  项目根目录: {project_root}')

# 3. 检查关键文件
print()
print('[3/6] 检查关键文件...')

check_files = [
    ('app/__init__.py', '应用初始化文件'),
    ('.env', '环境变量文件'),
    ('requirements.txt', '依赖文件'),
    ('app.db', '数据库文件')
]

all_ok = True
for file_path, desc in check_files:
    full_path = os.path.join(project_root, file_path)
    if os.path.exists(full_path):
        print(f'  ✅ {desc}: {file_path}')
    else:
        print(f'  ❌ {desc}: {file_path} (不存在)')
        all_ok = False

# 4. 检查Python环境
print()
print('[4/6] 检查Python环境...')
print(f'  Python版本: {sys.version}')
print(f'  Python路径: {sys.executable}')

# 5. 尝试导入项目模块
print()
print('[5/6] 尝试导入项目模块...')

sys.path.insert(0, project_root)

try:
    from app import create_app
    print('  ✅ 成功导入 create_app')
except Exception as e:
    print(f'  ❌ 导入失败: {e}')
    all_ok = False

try:
    from app.models import User
    print('  ✅ 成功导入 User 模型')
except Exception as e:
    print(f'  ❌ 导入失败: {e}')
    all_ok = False

# 6. 检查目录权限
print()
print('[6/6] 检查目录权限...')

check_dirs = [
    ('项目根目录', project_root),
    ('app目录', os.path.join(project_root, 'app')),
    ('脚本目录', script_dir)
]

for dir_name, dir_path in check_dirs:
    if os.path.exists(dir_path):
        readable = os.access(dir_path, os.R_OK)
        writable = os.access(dir_path, os.W_OK)
        print(f'  {dir_name}:')
        print(f'    可读: {"✅" if readable else "❌"}')
        print(f'    可写: {"✅" if writable else "❌"}')

print()
print('=' * 80)
if all_ok:
    print('✅ 环境检查完成，所有关键项正常！')
else:
    print('⚠️  环境检查完成，但发现一些问题！')
print('=' * 80)
print()
print('建议操作:')
print('  1. 确保在项目根目录下运行脚本')
print('  2. 确保已激活虚拟环境')
print('  3. 确保 .env 文件存在且配置正确')
print('  4. 确保有足够的文件读写权限')
