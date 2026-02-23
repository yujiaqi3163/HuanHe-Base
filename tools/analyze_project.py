import os
from pathlib import Path

project_root = Path(__file__).parent

print('='*80)
print('  项目文件大小分析')
print('='*80)
print()

# 检查路由文件大小
route_files = [
    'app/routes/main/routes.py',
    'app/routes/auth/routes.py',
    'app/routes/admin/routes.py',
]

print('路由文件大小：')
for f in route_files:
    full_path = project_root / f
    if full_path.exists():
        size_kb = full_path.stat().st_size / 1024
        print(f'  {f:<40} {size_kb:.2f} KB')
print()

# 检查根目录文件
print('根目录文件（需要整理）：')
root_files = list(project_root.glob('*.py')) + list(project_root.glob('*.bat')) + list(project_root.glob('*.md'))
for f in sorted(root_files):
    if f.name not in ['run.py', 'requirements.txt', 'README.md']:
        print(f'  {f.name}')
print()

# 检查是否有 tasks 目录
print('检查任务模块结构：')
tasks_path = project_root / 'app' / 'tasks.py'
tasks_dir = project_root / 'app' / 'tasks'
if tasks_path.exists():
    print(f'  app/tasks.py 存在（单文件模式）')
if tasks_dir.exists():
    print(f'  app/tasks/ 目录存在（模块化模式）')
print()

print('='*80)
