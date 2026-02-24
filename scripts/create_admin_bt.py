# ============================================================
# create_admin_bt.py
# 
# 宝塔服务器专用 - 创建超级管理员
# 功能说明：
# 1. 自动检测项目路径
# 2. 更好的错误处理
# 3. 详细的日志输出
# ============================================================

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
宝塔服务器专用 - 创建超级管理员账号
"""

import sys
import os

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录（脚本所在目录的上一级）
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

print('=' * 80)
print('宝塔服务器 - 创建超级管理员')
print('=' * 80)
print()
print(f'脚本目录: {SCRIPT_DIR}')
print(f'项目根目录: {PROJECT_ROOT}')
print()

# 添加项目根目录到Python路径
sys.path.insert(0, PROJECT_ROOT)

# 检查是否存在 .env 文件
env_path = os.path.join(PROJECT_ROOT, '.env')
if not os.path.exists(env_path):
    print('⚠️  警告: .env 文件不存在，请检查！')
    print(f'期望路径: {env_path}')
    print()

# 检查是否存在 app 目录
app_path = os.path.join(PROJECT_ROOT, 'app')
if not os.path.exists(app_path):
    print('❌ 错误: app 目录不存在！')
    print(f'期望路径: {app_path}')
    print()
    print('请确保在正确的项目目录下运行此脚本！')
    sys.exit(1)

try:
    from app import create_app, db
    from app.models import User
except ImportError as e:
    print(f'❌ 导入模块失败: {e}')
    print()
    print('请确保：')
    print('1. 已激活虚拟环境')
    print('2. 已安装所有依赖 (pip install -r requirements.txt)')
    print('3. 在正确的项目目录下运行')
    sys.exit(1)


def create_super_admins():
    """创建超级管理员账号"""
    print('正在初始化应用...')
    
    try:
        app = create_app()
    except Exception as e:
        print(f'❌ 创建应用失败: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    with app.app_context():
        print('应用初始化成功！')
        print()
        print('=' * 80)
        print('创建超级管理员账号')
        print('=' * 80)
        print()
        
        # 定义要创建的超级管理员列表
        super_admins = [
            {
                'username': 'pc_yujiaqi',
                'email': '2798479668@qq.com',
                'password': 'Yun803163'
            },
            {
                'username': 'pe_yujiaqi',
                'email': 'aa13178775196@163.com',
                'password': 'Yun803163'
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for admin_info in super_admins:
            username = admin_info['username']
            
            # 检查账号是否已存在
            existing_user = User.query.filter_by(username=username).first()
            
            if existing_user:
                print(f'  ℹ️ 账号 "{username}" 已存在')
                
                # 检查邮箱是否正确
                if existing_user.email != admin_info['email']:
                    print(f'     → 更新邮箱: {existing_user.email} → {admin_info["email"]}')
                    existing_user.email = admin_info['email']
                
                # 确保是超级管理员
                if not existing_user.is_super_admin:
                    print(f'     → 升级为超级管理员')
                    existing_user.is_super_admin = True
                    existing_user.is_admin = True
                
                skipped_count += 1
                continue
            
            # 创建新账号
            admin = User(
                username=username,
                email=admin_info['email'],
                is_admin=True,
                is_super_admin=True
            )
            admin.password = admin_info['password']
            db.session.add(admin)
            
            print(f'  ✅ 创建超级管理员: {username}')
            created_count += 1
        
        # 提交更改
        try:
            if created_count > 0 or skipped_count > 0:
                db.session.commit()
                print()
                print('数据库提交成功！')
        except Exception as e:
            db.session.rollback()
            print(f'❌ 数据库提交失败: {e}')
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        print()
        print('=' * 80)
        print('账号信息:')
        print('=' * 80)
        
        for admin_info in super_admins:
            print(f'  账号: {admin_info["username"]}')
            print(f'  邮箱: {admin_info["email"]}')
            print(f'  密码: {admin_info["password"]}')
            print()
        
        print('=' * 80)
        if created_count > 0:
            print(f'🎉 完成！共创建 {created_count} 个新账号')
        if skipped_count > 0:
            print(f'  更新/跳过 {skipped_count} 个已存在的账号')
        print('=' * 80)
        
        return True


if __name__ == '__main__':
    print()
    print('⚠️  注意：此脚本不会清除任何现有数据！')
    print()
    
    # 在宝塔服务器上，直接执行，不需要交互确认
    try:
        success = create_super_admins()
        if success:
            print()
            print('✅ 脚本执行成功！')
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print()
        print(f'❌ 出错: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
