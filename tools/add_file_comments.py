# ============================================================
# 批量添加文件功能注释脚本
# 功能：给项目中所有Python文件顶部添加功能说明注释
# ============================================================

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 需要添加注释的文件及其功能说明
FILE_COMMENTS = {
    # 核心文件
    'app/__init__.py': '''Flask 应用工厂模块
功能说明：
1. 创建 Flask 应用实例（工厂模式）
2. 初始化数据库（SQLAlchemy）
3. 初始化邮件服务（Flask-Mail）
4. 初始化 Celery 异步任务队列
5. 初始化用户登录管理（Flask-Login）
6. 初始化 Redis 分布式限流器（Flask-Limiter）
7. 设备绑定验证中间件
8. 注册所有路由蓝图''',

    'app/decorators.py': '''装饰器模块
功能说明：
1. @admin_required: 管理员权限验证
2. @device_required: 设备绑定验证（从Header获取X-Device-ID）
3. @permission_required: 细粒度权限检查''',

    'app/tasks.py': '''Celery 异步任务模块
功能说明：
1. async_remix_material: 素材二创异步任务
   - AI优化文案（调用DeepSeek API）
   - 创建用户素材记录
   - 复制并处理图片
   - 支持任务重试（最多3次）''',

    'celery_config.py': '''Celery 配置文件
功能说明：
1. 创建 Celery 实例
2. 配置 Redis 作为 Broker 和 Backend
3. 配置任务序列化、时区等参数
4. 自动发现并注册任务模块''',

    'run.py': '''Flask 应用启动入口
功能说明：
1. 创建 Flask 应用实例
2. 启动开发服务器''',

    'diagnose_celery.py': '''Celery 诊断工具
功能说明：
1. 检查环境变量配置
2. 检查 Redis 连接
3. 检查 Celery 配置
4. 检查任务模块
5. 提供启动建议''',

    # Utils 模块
    'app/utils/rate_limit.py': '''Redis 分布式限流模块
功能说明：
1. 基于 Flask-Limiter 实现分布式限流
2. 使用 Redis 作为存储后端（支持多进程/多服务器）
3. 统一 429 错误处理，显示等待时间
4. 支持多种限流规则（X per minute, X per second）''',

    'app/utils/logger.py': '''日志工具模块
功能说明：
1. 配置应用日志系统
2. 支持日志分级（DEBUG/INFO/WARNING/ERROR）
3. 日志文件轮转（防止文件过大）''',

    'app/utils/material_remix.py': '''素材二创工具模块
功能说明：
1. optimize_copywriting: 调用DeepSeek API优化文案
2. get_unique_css_recipes: 获取不重复的CSS样式配方''',

    # Models 模块
    'app/models/user.py': '''用户数据模型
功能说明：
1. User 表：用户基本信息、密码、角色、设备绑定
2. 密码加密存储（使用 Werkzeug）
3. 权限检查方法（has_permission）''',

    'app/models/material.py': '''素材数据模型
功能说明：
1. Material 表：素材基本信息、描述、上架状态
2. MaterialType 表：素材分类
3. MaterialImage 表：素材图片''',

    'app/models/user_material.py': '''用户二创素材模型
功能说明：
1. UserMaterial 表：用户二创的素材记录
2. UserMaterialImage 表：用户二创素材的图片''',

    'app/models/config.py': '''系统配置模型
功能说明：
1. Config 表：存储系统全局配置（如客服微信等）''',

    'app/models/permission.py': '''权限管理模型
功能说明：
1. Permission 表：权限定义
2. UserPermission 表：用户权限分配''',

    'app/models/register_secret.py': '''注册密钥模型
功能说明：
1. RegisterSecret 表：注册邀请码管理''',

    'app/models/terminal_secret.py': '''终端密钥模型
功能说明：
1. TerminalSecret 表：终端访问密钥管理''',

    # Forms 模块
    'app/forms/auth.py': '''认证表单模块
功能说明：
1. LoginForm: 登录表单
2. RegisterForm: 注册表单''',

    'app/forms/admin.py': '''管理后台表单模块
功能说明：
1. 素材管理表单
2. 用户管理表单
3. 配置管理表单''',

    'app/forms/material_type.py': '''素材分类表单模块
功能说明：
1. 素材分类添加/编辑表单''',

    # Routes 模块
    'app/routes/main/routes.py': '''主路由模块
功能说明：
1. 首页、素材详情页、我的作品库
2. 素材二创API（异步处理 + 限流）
3. 任务状态查询API
4. 个人中心、安全中心''',

    'app/routes/auth/routes.py': '''认证路由模块
功能说明：
1. 登录/注册/登出
2. 发送验证码（限流：3 per minute）
3. 忘记密码
4. 设备绑定/解绑''',

    'app/routes/admin/routes.py': '''管理后台路由模块
功能说明：
1. 素材管理（上架/下架/编辑）
2. 用户管理（角色分配/权限管理）
3. 系统配置管理
4. 统计数据展示''',

    # Scripts 模块
    'scripts/init_database.py': '''数据库初始化脚本
功能说明：
1. 创建所有数据表
2. 初始化默认配置
3. 创建超级管理员（可选）''',

    'scripts/create_super_admin.py': '''创建超级管理员脚本
功能说明：
1. 创建超级管理员账号
2. 分配所有权限''',

    'scripts/add_permissions.py': '''添加权限脚本
功能说明：
1. 批量添加系统权限
2. 分配权限给角色''',

    'scripts/migrate_user_table.py': '''用户表迁移脚本
功能说明：
1. 迁移旧版本用户表到新结构''',

    'scripts/migrate_user_material_tables.py': '''用户素材表迁移脚本
功能说明：
1. 迁移旧版本用户素材表到新结构''',

    'scripts/migrate_device_lock.py': '''设备锁迁移脚本
功能说明：
1. 迁移设备绑定相关数据''',

    'scripts/migrate_config_table.py': '''配置表迁移脚本
功能说明：
1. 迁移系统配置数据''',

    'scripts/migrate_secrets_table.py': '''密钥表迁移脚本
功能说明：
1. 迁移注册密钥和终端密钥数据''',

    'scripts/security_penetration_test.py': '''安全渗透测试脚本
功能说明：
1. 测试各种安全漏洞
2. 验证安全防护机制''',

    'scripts/performance_concurrency_test.py': '''性能并发测试脚本
功能说明：
1. 测试并发请求处理能力
2. 验证限流功能''',

    'scripts/update_material_stats.py': '''更新素材统计脚本
功能说明：
1. 更新素材的下载量、使用量等统计数据''',
}


def add_comment_to_file(file_path, comment_text):
    """给指定文件添加顶部注释"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经有注释（检查前10行）
        lines = content.split('\n')
        already_has_comment = False
        for i, line in enumerate(lines[:10]):
            if '功能说明' in line or '功能：' in line:
                already_has_comment = True
                break
        
        if already_has_comment:
            print(f'⏭️  跳过（已有注释）: {file_path}')
            return False
        
        # 构建注释头部
        comment_header = f'# {"="*60}\n'
        comment_header += f'# {Path(file_path).name}\n'
        comment_header += '# \n'
        for line in comment_text.strip().split('\n'):
            comment_header += f'# {line}\n'
        comment_header += f'# {"="*60}\n\n'
        
        # 写入新内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(comment_header + content)
        
        print(f'✅ 添加注释: {file_path}')
        return True
        
    except Exception as e:
        print(f'❌ 处理失败 {file_path}: {e}')
        return False


def main():
    print('='*60)
    print('  批量添加文件功能注释')
    print('='*60)
    print()
    
    success_count = 0
    skip_count = 0
    
    for relative_path, comment in FILE_COMMENTS.items():
        full_path = PROJECT_ROOT / relative_path
        
        if full_path.exists():
            if add_comment_to_file(full_path, comment):
                success_count += 1
            else:
                skip_count += 1
        else:
            print(f'⚠️  文件不存在: {relative_path}')
    
    print()
    print('='*60)
    print(f'  完成！成功: {success_count}, 跳过: {skip_count}')
    print('='*60)


if __name__ == '__main__':
    main()
