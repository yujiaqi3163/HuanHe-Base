#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型导入诊断脚本
用于检查 app.models 包的导入是否正常
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("模型导入诊断")
print("=" * 60)

# 1. 检查项目结构
print("\n1. 检查项目结构...")
models_dir = project_root / "app" / "models"
print(f"   模型目录: {models_dir}")
print(f"   目录存在: {models_dir.exists()}")

if models_dir.exists():
    model_files = list(models_dir.glob("*.py"))
    print(f"   模型文件:")
    for f in model_files:
        print(f"     - {f.name}")

# 2. 检查 __init__.py
print("\n2. 检查 app/models/__init__.py...")
init_file = models_dir / "__init__.py"
if init_file.exists():
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print("   __init__.py 内容:")
        print("-" * 60)
        print(content)
        print("-" * 60)
else:
    print("   ❌ __init__.py 不存在!")

# 3. 尝试导入各个模型
print("\n3. 尝试导入各个模型...")
test_imports = [
    "User",
    "RegisterSecret", 
    "TerminalSecret",
    "MaterialType",
    "Material",
    "MaterialImage",
    "UserMaterial",
    "UserMaterialImage",
    "UserFavorite",
    "UserDownload",
    "Config",
    "Permission",
    "UserPermission",
    "Announcement",
]

all_success = True
for model_name in test_imports:
    try:
        cmd = f"from app.models import {model_name}"
        exec(cmd)
        print(f"   ✅ {model_name} - 导入成功")
    except Exception as e:
        print(f"   ❌ {model_name} - 导入失败: {e}")
        all_success = False

# 4. 尝试完整导入
print("\n4. 尝试完整导入（与 routes.py 相同）...")
try:
    from app.models import (
        User, RegisterSecret, Material, UserMaterial, 
        UserMaterialImage, UserFavorite, UserDownload, Announcement
    )
    print("   ✅ 完整导入成功!")
except Exception as e:
    print(f"   ❌ 完整导入失败: {e}")
    import traceback
    traceback.print_exc()
    all_success = False

print("\n" + "=" * 60)
if all_success:
    print("✅ 所有模型导入正常!")
else:
    print("❌ 存在导入问题，请检查上面的错误信息")
print("=" * 60)
