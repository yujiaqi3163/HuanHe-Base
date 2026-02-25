# 📚 AI 咸鱼素材库 - 完整项目文档

> 本文档整合了项目的所有说明文档，提供完整的项目介绍、功能说明、开发指南、部署流程等内容。

---

## 🔍 快速导航（搜索关键词）

| 关键词 | 跳转链接 | 说明 |
|--------|----------|------|
| `项目概述` | [项目概述](#项目概述) | 了解项目整体情况 |
| `技术栈` | [技术栈](#技术栈) | 查看使用的技术 |
| `项目结构` | [项目结构](#项目结构) | 了解代码组织结构 |
| `快速启动` | [快速启动](#快速启动) | 本地启动项目 |
| `启动指南` | [完整启动指南](#完整启动指南) | 详细启动步骤 |
| `功能说明` | [项目功能完整说明](#项目功能完整说明) | 所有功能详解 |
| `数据模型` | [数据模型详解](#数据模型详解) | 数据库表结构 |
| `路由模块` | [路由模块详解](#路由模块详解) | API接口说明 |
| `开发文档` | [项目开发文档](#项目开发文档) | 开发者指南 |
| `部署指南` | [项目部署指南](#项目部署指南) | 服务器部署 |
| `宝塔部署` | [宝塔部署说明](#宝塔部署说明) | 宝塔面板部署 |
| `网站上线` | [网站上线部署手册](#网站上线部署手册) | 完整上线流程 |
| `常见问题` | [常见问题](#常见问题) | 问题排查 |

---

## 项目概述

本项目是一个基于 Flask + Tailwind CSS 的移动端 AI 素材库 Web 应用，包含用户认证、素材管理、卡密管理、用户管理等功能。核心特色是 AI 素材二创功能，使用 DeepSeek API 智能优化文案。

---

## 技术栈

- **后端框架**：Flask 3.1.3
- **数据库**：SQLite + Flask-SQLAlchemy 3.1.1
- **前端样式**：Tailwind CSS 3.4.0
- **表单验证**：Flask-WTF 1.2.2
- **用户认证**：Flask-Login 0.6.3
- **异步任务**：Celery + Redis
- **架构模式**：工厂模式 + Blueprint
- **设计风格**：移动端适配

---

## 项目结构

```
my_flask_app/
├── app/                          # 核心应用目录
│   ├── __init__.py               # 应用初始化文件（Flask 工厂函数）
│   ├── decorators.py             # 装饰器（权限验证、设备锁等）
│   ├── forms/                    # 表单定义（WTForms）
│   │   ├── __init__.py
│   │   ├── admin.py              # 管理后台表单
│   │   ├── auth.py               # 认证相关表单（登录、注册等）
│   │   └── material_type.py      # 素材分类表单
│   ├── models/                   # 数据模型（数据库表定义）
│   │   ├── __init__.py
│   │   ├── user.py               # 用户模型
│   │   ├── material.py           # 素材模型
│   │   ├── material_image.py     # 素材图片模型
│   │   ├── material_type.py      # 素材分类模型
│   │   ├── user_material.py      # 用户二创素材模型
│   │   ├── user_favorite.py      # 用户收藏模型
│   │   ├── user_download.py      # 用户下载模型
│   │   ├── register_secret.py    # 注册卡密模型
│   │   ├── terminal_secret.py    # 终端卡密模型
│   │   ├── permission.py         # 权限模型
│   │   ├── announcement.py       # 公告模型
│   │   └── config.py             # 配置模型
│   ├── routes/                   # 路由（URL 接口）
│   │   ├── __init__.py
│   │   ├── auth/                 # 认证相关路由
│   │   │   ├── __init__.py
│   │   │   └── routes.py         # 登录、注册、找回密码等
│   │   ├── admin/                # 管理后台路由
│   │   │   ├── __init__.py
│   │   │   └── routes.py         # 素材管理、用户管理等
│   │   └── main/                 # 主页面路由
│   │       ├── __init__.py
│   │       └── routes.py         # 首页、素材详情、我的素材等
│   ├── static/                   # 静态文件
│   │   ├── css/
│   │   │   └── output.css        # 编译后的 Tailwind CSS
│   │   └── src/
│   │       └── input.css         # Tailwind 源文件
│   ├── templates/                # HTML 模板
│   │   ├── base.html             # 基础模板（所有页面继承）
│   │   ├── auth/                 # 认证页面
│   │   ├── admin/                # 管理后台页面
│   │   └── main/                 # 用户页面
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   ├── logger.py             # 日志工具
│   │   ├── rate_limit.py         # API 限流工具
│   │   └── material_remix.py     # 素材二创工具（调用 DeepSeek API）
│   └── tasks.py                  # Celery 异步任务
├── scripts/                      # 脚本工具
│   ├── init_database.py          # 初始化数据库
│   ├── create_admin.py           # 创建超级管理员（通用版）
│   ├── create_admin_bt.py        # 创建超级管理员（宝塔版）
│   ├── add_permissions.py        # 添加权限
│   ├── diagnose_imports.py       # 模型导入诊断
│   ├── migrate_*.py              # 数据库迁移脚本
│   ├── security_penetration_test.py  # 安全渗透测试
│   └── performance_concurrency_test.py # 性能压力测试
├── celery_config.py              # Celery 配置（异步任务）
├── requirements.txt              # Python 依赖包
├── .env.example                  # 环境变量示例
├── .gitignore                    # Git 忽略文件
├── run.py                        # 项目启动文件
└── tailwind.config.js            # Tailwind CSS 配置
```

---

## 快速启动

### 前置条件

确保已安装：
- Python 3.8+
- Redis（或 Memurai for Windows）
- 项目依赖（`pip install -r requirements.txt`）

### 开发环境快速启动

```bash
# 1. 复制环境变量
cp .env.example .env
# 然后编辑 .env，填入你的配置

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库
python scripts/init_database.py
python scripts/create_admin.py

# 4. 启动项目（需要3个终端）

# 终端 1 - 启动 Redis
redis-server.exe

# 终端 2 - 启动 Celery Worker
python -m celery -A celery_config worker --loglevel=info --pool=solo

# 终端 3 - 启动 Flask 应用
python run.py
```

### 访问地址

- 前台：http://localhost:5000
- 后台：http://localhost:5000/admin

---

## 完整启动指南

### 前置条件

确保已安装：
- Python 3.8+
- Redis（或 Memurai for Windows）
- 项目依赖（`pip install -r requirements.txt`）

### 快速启动（3 个终端）

#### 终端 1 - 启动 Redis

**Windows 用户：**
```cmd
# 如果使用 Memurai
memurai.exe

# 或者如果安装了 Redis
redis-server.exe
```

**或者使用 Docker（推荐）：**
```bash
docker run -d -p 6379:6379 --name my-redis redis:alpine
```

#### 终端 2 - 启动 Celery Worker

**Windows 用户（双击运行）：**
```
start_worker.bat
```

**或者手动运行：**
```bash
celery -A celery_config worker --loglevel=info --pool=solo
```

**Linux/Mac 用户：**
```bash
celery -A celery_config worker --loglevel=info
```

#### 终端 3 - 启动 Flask 应用

```bash
python run.py
```

### 验证启动成功

#### 检查 Redis
```bash
redis-cli ping
# 应该返回: PONG
```

#### 检查 Celery Worker
在 Worker 终端应该看到：
```
[INFO] Connected to redis://localhost:6379/0
[INFO] celery@... ready.
```

#### 检查 Flask
访问：http://127.0.0.1:5000

### 环境变量配置

确保 `.env` 文件包含：
```env
SECRET_KEY=your_strong_secret_key

DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_API_BASE=https://api.deepseek.com

MAIL_USERNAME=your_email@163.com
MAIL_PASSWORD=your_email_password

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0
```

### 项目架构

```
Flask 应用 (端口 5000)
    ↓
Redis (端口 6379) ← 任务队列 + 限流存储
    ↓
Celery Worker ← 处理异步任务
```

### 常见问题

#### 问题 1：Redis 未启动
**错误：** `Error 10061 connecting to localhost:6379`

**解决：** 启动 Redis 或 Memurai

#### 问题 2：任务一直"等待中"
**原因：** Celery Worker 未启动

**解决：** 确保运行了 `start_worker.bat` 或 `celery -A celery_config worker...`

#### 问题 3：`No module named 'celery'`
**解决：** 安装依赖
```bash
pip install -r requirements.txt
```

---

## 项目功能完整说明

### 用户认证与安全功能

#### 登录功能
**文件位置：**
- `app/routes/auth/routes.py` - 后端接口
- `app/forms/auth.py` - 登录表单验证
- `app/templates/auth/login.html` - 前端页面

**功能说明：**
- 用户输入邮箱和密码登录
- 密码使用 `werkzeug.security` 加密存储（bcrypt 算法）
- 登录成功后保存 session，30 天内免登录
- 支持记住密码功能

**安全特性：**
- ✅ 密码加盐哈希存储（防明文存储）
- ✅ 登录失败次数限制（防暴力破解）
- ✅ CSRF 防护（Flask-WTF）

#### 注册功能
**文件位置：**
- `app/routes/auth/routes.py`
- `app/forms/auth.py`
- `app/templates/auth/register.html`

**功能说明：**
- 需要输入注册卡密才能注册
- 卡密验证通过后才能创建账号
- 邮箱格式验证
- 密码强度验证（长度、复杂度）

**安全特性：**
- ✅ 卡密验证（防止随意注册）
- ✅ 邮箱格式和可送达性验证
- ✅ 密码确认（两次输入一致）

#### 找回密码功能
**文件位置：**
- `app/routes/auth/routes.py`
- `app/templates/auth/forgot_password.html`

**功能说明：**
- 通过邮箱验证码重置密码
- 发送验证码到注册邮箱
- 验证码有效期限制

**安全特性：**
- ✅ 邮箱验证码验证
- ✅ 验证码过期机制

#### 设备锁功能
**文件位置：**
- `app/decorators.py` - `@device_required` 装饰器
- `app/routes/auth/routes.py` - 设备绑定接口
- `app/models/user.py` - 设备 ID 字段

**功能说明：**
- 账号首次登录时绑定当前设备
- 后续登录必须使用同一设备
- 超级管理员不受设备锁限制
- 支持申请解绑设备

**工作原理：**
1. 用户登录时，前端生成唯一的设备 ID（存储在 Cookie 中）
2. 如果是首次登录，将设备 ID 保存到数据库
3. 后续登录时，验证 Cookie 中的设备 ID 是否与数据库一致
4. 不一致则强制退出

**安全特性：**
- ✅ 防止账号多设备同时登录
- ✅ 设备 ID 加密存储
- ✅ 超级管理员豁免（方便管理）

### 用户个人中心功能

#### 个人资料管理
**文件位置：**
- `app/routes/main/routes.py`
- `app/templates/main/profile_edit.html`

**功能说明：**
- 修改用户名
- 修改性别
- 查看和编辑个人信息

#### 安全中心
**文件位置：**
- `app/routes/main/routes.py`
- `app/templates/main/security_center.html`

**功能模块：**
1. **修改密码** (`security_password.html`)
   - 验证旧密码
   - 设置新密码

2. **设备管理** (`security_device.html`)
   - 查看当前绑定设备
   - 申请解绑设备

3. **卡密管理** (`security_secret.html`)
   - 查看注册卡密信息

### 素材管理功能

#### 素材浏览
**文件位置：**
- `app/routes/main/routes.py` - 首页路由
- `app/templates/main/index.html` - 首页

**功能说明：**
- 查看所有已上架的素材
- 支持分类筛选
- 素材卡片展示（封面图、标题、描述）

#### 素材详情
**文件位置：**
- `app/routes/main/routes.py` - 详情页路由
- `app/templates/main/material_detail.html` - 详情页

**功能说明：**
- 查看素材完整内容
- 查看所有图片（轮播展示）
- 点击"二创"按钮进行素材二次创作

#### 素材二创（核心功能！）
**文件位置：**
- `app/routes/main/routes.py` - `/api/material/<id>/remix` 接口
- `app/tasks.py` - `async_remix_material` 异步任务
- `app/utils/material_remix.py` - DeepSeek API 调用
- `app/templates/main/material_detail.html` - 前端二创按钮

**功能说明：**
1. 用户点击"二创"按钮
2. 后端立即返回 task_id（不阻塞）
3. Celery 异步任务在后台处理：
   - 调用 DeepSeek API 优化文案
   - 生成不重复的 CSS 混合配方
   - 创建用户二创素材记录
   - 复制并处理图片
4. 前端每 2 秒轮询任务状态
5. 任务完成后自动刷新页面

**技术亮点：**
- ⚡ **异步处理**：使用 Celery + Redis，不阻塞用户操作
- 🤖 **AI 优化**：调用 DeepSeek API 智能改写文案
- 🎨 **CSS 混合**：自动生成图片处理配方

#### 我的素材
**文件位置：**
- `app/routes/main/routes.py`
- `app/templates/main/my_materials.html`

**功能说明：**
- 查看自己二创的所有素材
- 点击进入详情页
- 查看素材浏览和下载次数

### 管理后台功能

#### 素材管理
**文件位置：**
- `app/routes/admin/routes.py`
- `app/templates/admin/admin_materials.html`

**功能列表：**
1. **素材列表**
   - 查看所有素材
   - 显示素材总数

2. **批量删除**
   - 勾选多个素材删除
   - 删除同时删除图片文件

3. **全部删除**
   - 一键清空素材库（慎重！）

4. **添加素材**
   - 单个素材添加
   - **批量上传**（文件夹批量导入）

#### 批量上传素材
**文件位置：**
- `app/routes/admin/routes.py` - `/batch-upload-material` 接口
- `app/templates/admin/admin_material_add.html` - 上传页面

**功能说明：**
- 支持选择整个文件夹上传
- 自动识别文件夹内的 `文案.txt`（格式：`title："..." content："..."`）
- 自动识别图片文件（jpg、png、gif、webp、bmp）
- **逐个文件上传**（防止请求过大）
- 文件大小限制：单个文件最大 50MB
- 文件类型白名单验证

**安全特性：**
- ✅ 文件大小限制（防超大文件攻击）
- ✅ 文件类型白名单（防恶意文件上传）
- ✅ 文件名安全处理（`secure_filename`）
- ✅ 逐个上传容错（某个失败不影响其他）

#### 素材分类管理
**文件位置：**
- `app/routes/admin/routes.py`
- `app/templates/admin/admin_material_types.html`

**功能说明：**
- 添加素材分类
- 编辑分类名称
- 删除分类

#### 用户管理
**文件位置：**
- `app/routes/admin/routes.py`
- `app/templates/admin/admin_users.html`

**功能说明：**
- 查看所有用户
- 编辑用户信息
- 禁用/启用用户
- 查看用户绑定的设备

#### 权限管理
**文件位置：**
- `app/routes/admin/routes.py`
- `app/templates/admin/admin_user_permissions.html`
- `app/models/permission.py` - 权限模型
- `app/decorators.py` - `@permission_required` 装饰器

**功能说明：**
- 基于角色的权限控制（RBAC）
- 为用户分配权限
- 权限装饰器验证

**示例权限：**
- `material_manage` - 素材管理权限
- `user_manage` - 用户管理权限

#### 卡密管理
**文件位置：**
- `app/routes/admin/routes.py`
- `app/templates/admin/admin_secrets.html`

**功能说明：**
- 生成注册卡密
- 生成终端卡密
- 查看卡密使用情况
- 禁用/启用卡密

### 安全防护功能

#### SQL 注入防护
**实现方式：**
- 使用 **Flask-SQLAlchemy** ORM（对象关系映射）
- 不直接拼接 SQL 语句
- 使用参数化查询

#### CSRF 跨站请求伪造防护
**实现方式：**
- 使用 **Flask-WTF** 扩展
- 所有表单自动包含 CSRF token
- AJAX 请求也需要验证 CSRF token

#### XSS 跨站脚本攻击防护
**实现方式：**
- 使用 **Jinja2** 模板引擎自动转义 HTML
- 所有用户输入在渲染时自动转义

#### API 限流（防刷接口）
**文件位置：**
- `app/utils/rate_limit.py` - `@rate_limit` 装饰器

**功能说明：**
- 限制单个 IP 在指定时间内的请求次数
- 防止恶意刷接口

#### 密码安全
**实现方式：**
- 使用 **werkzeug.security** 的 `generate_password_hash` 和 `check_password_hash`
- 自动加盐哈希（bcrypt 算法）

#### 文件上传安全
**实现方式：**
- 文件大小限制（100MB Flask 层面，50MB 业务层面）
- 文件类型白名单（仅允许图片格式）
- 文件名安全处理（`secure_filename`）
- 文件存储在非 web 可访问目录（或验证访问权限）

#### 环境变量保护
**实现方式：**
- 敏感信息（SECRET_KEY、数据库密码、API Key）存储在 `.env` 文件
- `.env` 文件加入 `.gitignore`，不提交到 Git
- 使用 `python-dotenv` 加载环境变量

### 异步处理功能

#### Celery + Redis 异步任务
**文件位置：**
- `celery_config.py` - Celery 配置
- `app/tasks.py` - 异步任务定义
- `app/__init__.py` - Celery 初始化

**功能说明：**
- 使用 **Redis** 作为消息队列（Broker）和结果存储（Backend）
- **Celery Worker** 在后台处理耗时任务
- 不阻塞 Flask 主进程，提升用户体验

**当前异步任务：**
1. **素材二创** (`async_remix_material`)
   - 调用 DeepSeek API（可能耗时几秒到几十秒）
   - 失败自动重试（最多 3 次）
   - 任务超时限制（300 秒）

### 日志功能

#### 应用日志
**文件位置：**
- `app/utils/logger.py` - 日志配置

**功能说明：**
- 使用 Python 标准 `logging` 模块
- 日志按大小滚动（`RotatingFileHandler`）
- 同时输出到文件和控制台
- 不同级别日志（DEBUG、INFO、WARNING、ERROR）

**日志内容：**
- 用户登录/登出
- 素材操作（添加、删除、二创）
- API 请求
- 错误异常

---

## 数据模型详解

### User（用户模型）

**文件位置**：`app/models/user.py`

**字段说明：**
- `id`: Integer (主键)
- `username`: String(80) (用户名，唯一，索引)
- `email`: String(120) (邮箱，唯一，索引)
- `password_hash`: String(256) (密码哈希，使用 werkzeug.security 加密)
- `is_admin`: Boolean (是否管理员，默认False)
- `is_super_admin`: Boolean (是否超级管理员，默认False)
- `avatar`: String(500) (头像URL，可空)
- `bio`: String(200) (个性签名，可空)
- `gender`: String(10) (性别：male/female/other，可空)
- `birthday`: Date (出生日期，可空)
- `bound_device_id`: String(200) (绑定的设备ID，可空)
- `device_unbind_status`: Integer (设备解绑状态：0-正常，1-申请中，默认0)
- `device_unbind_requested_at`: DateTime (设备解绑申请时间，可空)
- `created_at`: DateTime (创建时间)

**方法：**
- `@property password`: 密码属性（只读，访问会抛出错误）
- `@password.setter password`: 设置密码，自动加密
- `check_password(password)`: 验证密码

### Config（系统配置模型）

**文件位置**：`app/models/config.py`

**字段说明：**
- `id`: Integer (主键)
- `key`: String(100) (配置键，唯一，索引)
- `value`: Text (配置值，可空)
- `description`: String(200) (配置描述，可空)
- `created_at`: DateTime (创建时间)
- `updated_at`: DateTime (最后修改时间，自动更新)

**方法：**
- `get_value(key, default=None)`: 静态方法，获取配置值
- `set_value(key, value, description=None)`: 静态方法，设置配置值

### MaterialType（素材类型/分类模型）

**文件位置**：`app/models/material_type.py`

**字段说明：**
- `id`: Integer (主键)
- `name`: String(50) (分类名称，唯一，索引)
- `description`: String(200) (分类描述，可空)
- `sort_order`: Integer (排序，默认0)
- `is_active`: Boolean (是否启用，默认True)
- `created_at`: DateTime (创建时间)

### Material（素材模型）

**文件位置**：`app/models/material.py`

**字段说明：**
- `id`: Integer (主键)
- `title`: String(200) (标题，索引，非空)
- `description`: Text (文案，可空)
- `material_type_id`: Integer (分类ID，外键，可空)
- `view_count`: Integer (浏览次数，默认0)
- `favorite_count`: Integer (收藏次数，默认0)
- `download_count`: Integer (下载次数，默认0)
- `is_published`: Boolean (是否上架，默认True)
- `sort_order`: Integer (排序权重，默认0)
- `created_at`: DateTime (创建时间)
- `updated_at`: DateTime (最后修改时间，自动更新)

### MaterialImage（素材图片模型）

**文件位置**：`app/models/material_image.py`

**字段说明：**
- `id`: Integer (主键)
- `material_id`: Integer (素材ID，外键，非空)
- `image_url`: String(500) (图片URL或路径，非空)
- `sort_order`: Integer (排序，默认0)
- `is_cover`: Boolean (是否封面图，默认False)
- `created_at`: DateTime (创建时间)

### RegisterSecret（注册卡密模型）

**文件位置**：`app/models/register_secret.py`

**字段说明：**
- `id`: Integer (主键)
- `secret`: String(100) (卡密，唯一，索引，非空)
- `is_used`: Boolean (是否已使用，默认False)
- `user_id`: Integer (用户ID，外键，可空)
- `created_at`: DateTime (创建时间)
- `used_at`: DateTime (使用时间，可空)
- `duration_type`: String(20) (卡密类型：1min/1day/1month/1year/permanent，默认permanent)
- `expires_at`: DateTime (过期时间，可空)

### UserMaterial（用户二创素材模型）

**文件位置**：`app/models/user_material.py`

**字段说明：**
- `id`: Integer (主键)
- `user_id`: Integer (用户ID，外键，非空)
- `original_material_id`: Integer (原始素材ID，外键，可空)
- `title`: String(200) (二创标题，非空)
- `description`: Text (二创文案，可空)
- `original_description`: Text (原始文案备份，可空)
- `view_count`: Integer (浏览次数，默认0)
- `download_count`: Integer (下载次数，默认0)
- `created_at`: DateTime (创建时间)

### UserMaterialImage（用户二创素材图片模型）

**文件位置**：`app/models/user_material.py`（与UserMaterial同文件）

**字段说明：**
- `id`: Integer (主键)
- `user_material_id`: Integer (二创素材ID，外键，非空)
- `image_url`: String(500) (图片URL，非空)
- `sort_order`: Integer (排序，默认0)
- `is_cover`: Boolean (是否封面图，默认False)
- `original_image_url`: String(500) (原始图片URL备份，可空)
- `css_recipe`: Text (CSS混合配方，记录用于复现，可空)
- `created_at`: DateTime (创建时间)

### UserFavorite（用户收藏模型）

**文件位置**：`app/models/user_favorite.py`

**字段说明：**
- `id`: Integer (主键)
- `user_id`: Integer (用户ID，外键，非空)
- `material_id`: Integer (素材ID，外键，非空)
- `created_at`: DateTime (创建时间)

### UserDownload（用户下载模型）

**文件位置**：`app/models/user_download.py`

**字段说明：**
- `id`: Integer (主键)
- `user_id`: Integer (用户ID，外键，非空)
- `material_id`: Integer (素材ID，外键，可空)
- `user_material_id`: Integer (用户素材ID，外键，可空)
- `created_at`: DateTime (创建时间)

---

## 路由模块详解

### 应用配置（app/__init__.py）

**核心功能：**
- 工厂模式创建 Flask 应用
- 初始化数据库（SQLAlchemy）
- 初始化登录管理器（Flask-Login）
- 注册三个 Blueprint：
  - `main_bp`: 主路由（首页、个人中心、素材详情）
  - `auth_bp`: 认证路由（登录、注册、登出），前缀 `/auth`
  - `admin_bp`: 管理后台路由，前缀 `/admin`

**配置项：**
- `SECRET_KEY`: 会话密钥，从环境变量获取
- `SQLALCHEMY_DATABASE_URI`: 数据库连接地址（SQLite）
- `SQLALCHEMY_TRACK_MODIFICATIONS`: False（关闭修改跟踪）
- `WTF_CSRF_ENABLED`: True（已启用CSRF保护）

### 主路由（app/routes/main/routes.py）

**路由列表：**

| 路由 | 方法 | 功能 | 登录要求 |
|------|------|------|---------|
| `/` | GET | 首页（轮播图 + 素材列表） | ✅ |
| `/profile` | GET | 个人中心 | ✅ |
| `/profile/edit` | GET/POST | 个人资料编辑 | ✅ |
| `/material/<material_id>` | GET | 素材详情页（增加浏览量） | ✅ |
| `/api/renew-secret` | POST | 卡密续费API | ✅ |
| `/api/latest-materials` | GET | 分页获取最新素材API | ✅ |
| `/my-materials` | GET | 我的作品库 | ✅ |
| `/my-material/<user_material_id>` | GET | 我的素材详情 | ✅ |
| `/security-center` | GET | 安全中心 | ✅ |
| `/security-password` | GET | 修改密码 | ✅ |
| `/security-secret` | GET | 卡密信息 | ✅ |
| `/security-device` | GET | 设备绑定 | ✅ |
| `/api/change-password` | POST | 修改密码API | ✅ |
| `/api/material/<material_id>/remix` | POST | 素材二创API | ✅ |
| `/api/user-material/<user_material_id>/download` | POST | 下载计数API | ✅ |
| `/api/user-material/<user_material_id>/delete` | POST | 删除素材API | ✅ |
| `/api/task/<task_id>/status` | GET | 查询任务状态API | ✅ |

**核心功能：**
- **首页**：显示热度最高的前5个素材轮播图，最新入库素材列表（无限滚动加载）
- **个人中心**：显示用户信息、卡密状态（永久/有效期内/已失效）
- **个人资料编辑**：头像上传、昵称修改、性别选择、出生日期设置、个性签名编辑
- **素材详情**：1:1图片轮播、信息展示、下载按钮
- **卡密续费**：用户使用新卡密时，自动释放旧的过期卡密
- **分页API**：支持搜索、排序（最新/浏览/收藏/下载）
- **素材二创**：使用DeepSeek优化文案，CSS混合配方生成二创图片

### 认证路由（app/routes/auth/routes.py）

**路由列表：**

| 路由 | 方法 | 功能 | 登录要求 |
|------|------|------|---------|
| `/auth/login` | GET/POST | 登录页面 | ❌ |
| `/auth/register` | GET/POST | 注册页面（需要卡密） | ❌ |
| `/auth/logout` | GET | 退出登录 | ✅ |
| `/auth/send-code` | POST | 发送验证码API | ❌ |
| `/auth/forgot-password` | GET/POST | 忘记密码 | ❌ |
| `/auth/forgot-send-code` | POST | 忘记密码发送验证码 | ❌ |
| `/auth/forgot-reset` | POST | 重置密码 | ❌ |

**核心功能：**
- **登录**：支持用户名或邮箱登录，记住我功能
- **注册**：需要卡密验证，注册时标记卡密已使用，计算过期时间
- **登出**：清除用户会话
- **邮箱验证码**：通过163邮箱SMTP服务发送6位数字验证码，5分钟有效期
- **忘记密码**：验证邮箱验证码后重置密码
- **设备锁**：首次登录自动绑定设备，后续登录验证设备一致性

### 管理后台路由（app/routes/admin/routes.py）

**主要功能：**
- **数据统计**：总素材数、创作素材数、未使用卡密数、用户总数、最新素材、最新卡密、用户增长趋势图、数据分布饼图
- **素材管理**：
  - 素材列表（无限滚动、分类筛选、搜索）
  - 添加素材（标题、文案、分类、封面图、细节图）
  - 编辑素材（支持删除/新增细节图）
  - 删除素材（级联删除图片记录和文件）
- **分类管理**：AJAX增删改查，无需页面跳转
- **卡密管理**：
  - 卡密生成（选择时长、数量）
  - 卡密列表（状态筛选、搜索）
  - 一键删除已释放卡密
  - 手动释放未到期卡密
  - 复制卡密功能
- **用户管理**：
  - 用户列表（搜索）
  - 设置/取消管理员
  - 删除用户（级联删除关联卡密、二创素材、图片文件）
  - 设备解绑审批

---

## 项目开发文档

### 核心功能实现逻辑

#### 卡密系统

##### 卡密生成
- **卡密格式**：`sk-` + 18位随机数字+英文大小写
- **时长类型**：
  - `1min`: 1分钟（测试用）
  - `1day`: 1天（日卡）
  - `1month`: 30天（月卡）
  - `1year`: 365天（年卡）
  - `permanent`: 永久
- **过期时间**：用户使用时才开始计算，而非生成时

##### 卡密续费逻辑
1. 用户在个人中心点击卡密，打开详情弹窗
2. 过期卡密显示续费表单
3. 用户输入新卡密，调用 `/api/renew-secret` API
4. 系统验证新卡密有效性
5. 释放用户旧的过期卡密（解除与用户关联，保留历史记录）
6. 标记新卡密为已使用，计算过期时间
7. 返回成功信息

##### 卡密状态显示
- **永久会员**：显示 "♾️ 永久会员"，黄色高亮
- **有效期内**：显示 "至 YYYY-MM-DD"，绿色显示
- **已失效**：显示 "已失效，请联系管理购买"，红色显示

#### 素材详情页轮播图

**实现特点：**
- **1:1比例**：图片保持正方形展示
- **触摸滑动**：支持手势滑动切换
- **自动播放**：4秒自动切换
- **无限循环**：双向无感循环（左右无限滑动）
- **轮播指示器**：底部显示当前位置

**技术实现：**
- 克隆首尾图片实现无限循环
- 使用 `touchstart`、`touchmove`、`touchend` 事件处理触摸滑动
- 使用 `transform: translateX()` 实现平滑过渡

#### 无限滚动加载

**实现逻辑：**
1. 监听页面滚动事件
2. 检查是否滚动到底部
3. 如果有更多数据，调用API获取下一页
4. 追加渲染新数据到列表
5. 更新是否有更多数据标志

**支持功能：**
- 分页获取
- 搜索（按标题）
- 排序（最新/浏览/收藏/下载）

#### 设备锁系统

**实现逻辑：**
- 首次登录自动生成并绑定设备ID到用户
- 设备ID存储在 Cookie 中（HttpOnly + SameSite）
- 后续登录验证设备一致性
- 设备不匹配时强制退出登录
- 用户可申请解绑，管理员审批后新设备可登录

#### 素材二创系统

**实现逻辑：**
- 使用 DeepSeek API 优化文案（30秒超时）
- 生成唯一的 CSS 混合配方（blend_mode + gradient_angle）
- 保存二创素材到 UserMaterial 表
- 保存图片信息到 UserMaterialImage 表
- API 调用失败时使用原文案降级

### 页面路由汇总

#### 前台页面
| 页面 | 地址 | 描述 |
|------|------|------|
| 首页 | `/` | 轮播图 + 素材列表 |
| 个人中心 | `/profile` | 用户信息 + 卡密状态 |
| 个人资料编辑 | `/profile/edit` | 编辑个人信息 |
| 素材详情 | `/material/<id>` | 查看素材详情 |
| 我的作品库 | `/my-materials` | 用户二创素材列表 |
| 我的素材详情 | `/my-material/<id>` | 查看二创素材详情 |
| 安全中心 | `/security-center` | 安全功能入口 |
| 修改密码 | `/security-password` | 修改密码 |
| 卡密信息 | `/security-secret` | 查看卡密信息 |
| 设备绑定 | `/security-device` | 设备绑定管理 |

#### 认证页面
| 页面 | 地址 | 描述 |
|------|------|------|
| 登录 | `/auth/login` | 用户登录 |
| 注册 | `/auth/register` | 用户注册（需卡密） |
| 忘记密码 | `/auth/forgot-password` | 重置密码 |
| 登出 | `/auth/logout` | 退出登录 |

#### 管理后台
| 页面 | 地址 | 描述 |
|------|------|------|
| 管理后台首页 | `/admin/` | 数据统计 |
| 素材库管理 | `/admin/materials` | 素材列表管理 |
| 添加素材 | `/admin/materials/add` | 新增素材 |
| 编辑素材 | `/admin/materials/edit/<id>` | 编辑素材 |
| 分类管理 | `/admin/material-types` | 素材分类管理 |
| 卡密管理 | `/admin/secrets` | 卡密列表管理 |
| 用户管理 | `/admin/users` | 用户列表管理 |

### 已完成功能清单

- ✅ 用户注册（卡密验证）
- ✅ 用户登录（支持用户名/邮箱）
- ✅ 用户退出登录
- ✅ 个人中心页面（显示用户信息、角色标签）
- ✅ 个人资料编辑（头像、昵称、邮箱、性别、生日、签名）
- ✅ 邮箱只读保护
- ✅ 卡密管理功能（生成、列表、搜索、释放、删除）
- ✅ 用户管理功能（列表、搜索、设置/取消管理员、删除）
- ✅ 管理后台数据统计实时渲染
- ✅ 素材分类管理（AJAX增删改查）
- ✅ 素材添加功能（标题、文案、分类、图片）
- ✅ 素材编辑功能
- ✅ 素材删除功能
- ✅ 素材列表无限滚动加载
- ✅ 素材分类筛选
- ✅ 素材搜索功能
- ✅ 首页轮播图（真实数据，热度排行）
- ✅ 素材详情详情
- ✅ 卡密详情弹窗与续费功能
- ✅ 旧卡密释放逻辑
- ✅ 用户级联删除
- ✅ 邮箱验证码功能
- ✅ 忘记密码功能
- ✅ 修改密码功能
- ✅ 安全中心（卡密信息、设备绑定、修改密码）
- ✅ 设备绑定/解绑功能
- ✅ 卡密验证（在主页和素材详情页）
- ✅ 设备锁验证
- ✅ 记住登录状态功能
- ✅ 密码可见/隐藏按钮
- ✅ 我的作品库（用户二创）
- ✅ 素材二创功能
- ✅ 删除用户时级联删除二创素材和图片
- ✅ CSRF 保护已启用
- ✅ SECRET_KEY 从环境变量获取
- ✅ 日志系统已集成
- ✅ API 限流（验证码发送）
- ✅ Cookie HttpOnly + SameSite
- ✅ 密码强度验证
- ✅ N+1查询优化（使用joinedload）
- ✅ DeepSeek API 30秒超时
- ✅ SMTP 邮件发送 10秒超时

### 项目特点

1. **模块化设计**：采用 Blueprint + 工厂模式，代码结构清晰
2. **移动端优先**：使用 Tailwind CSS 实现响应式布局，完美适配移动端
3. **数据库优化**：合理使用索引，查询效率高
4. **用户体验**：无限滚动、AJAX操作、平滑动画
5. **安全性**：密码加密、CSRF保护、登录验证、设备锁
6. **可扩展性**：预留了多个字段和接口，方便后续功能扩展

### 已完成的安全优化

#### 高优先级
1. **启用 CSRF 保护**
   - 位置: `app/__init__.py:31`
   - 修改: `WTF_CSRF_ENABLED = True`

2. **改进 SECRET_KEY 配置**
   - 位置: `app/__init__.py:23-25`
   - 修改: 强制从环境变量获取
   - 新增: `.env` 和 `.env.example` 文件

3. **创建日志系统**
   - 新增: `app/utils/logger.py`
   - 功能: 日志文件轮询、分级记录、异常堆栈跟踪

#### 中优先级
4. **优化 device_id cookie 安全**
   - 位置: `app/routes/auth/routes.py:129`
   - 修改: 添加 `httponly=True` 和 `samesite='Lax'`

5. **创建 API 限流装饰器**
   - 新增: `app/utils/rate_limit.py`
   - 应用: 验证码发送接口 (3次/60秒)

6. **增加密码强度验证**
   - 位置: `app/forms/auth.py:12-32`
   - 要求: 8位+、大小写字母、数字、特殊字符

#### 低优先级
7. **完善表单定义**
   - 新增: `ForgotPasswordForm`、`ChangePasswordForm`

8. **替换所有 print 语句**
   - 涉及文件: 4个文件，约36处 print 替换为 logger

9. **清理临时文件**
   - 删除: `deepseek_api.py`、`CSS混合MD5.html`、`代码大全.txt`

10. **更新 .gitignore**
    - 添加: 日志目录、上传文件、IDE 配置等

### 已完成的性能优化

#### N+1 查询优化
- **位置**: `app/routes/main/routes.py:513-517` 和 `app/routes/admin/routes.py:134-138`
- **优化**: 使用 `joinedload` 预加载关联数据
- **效果**: 查询次数从 21次 降至 1-2次

#### DeepSeek API 超时
- **位置**: `app/utils/material_remix.py`
- **优化**: 添加 30 秒超时参数

#### SMTP 超时
- **位置**: `app/routes/auth/routes.py`
- **优化**: 添加 10 秒超时参数

---

## 项目部署指南

### 文件分类说明

#### ✅ 可提交到 Git 的文件（源代码和配置）

| 目录/文件 | 说明 |
|------------|------|
| `app/` | 应用核心代码 |
| `scripts/init_database.py` | 数据库初始化脚本 |
| `scripts/migrate_*.py` | 数据库迁移脚本（可选保留） |
| `templates/` | HTML 模板文件 |
| `static/css/` | 静态资源（CSS、JS） |
| `static/src/` | Tailwind 源文件 |
| `requirements.txt` | Python 依赖列表 |
| `run.py` | 应用启动文件 |
| `.env.example` | 环境变量示例文件 |
| `.gitignore` | Git 忽略配置 |
| `package.json` | Node 依赖配置 |
| `tailwind.config.js` | Tailwind 配置 |
| `*.md` | 项目文档 |

#### ❌ 不可提交到 Git 的文件（敏感/临时/缓存）

| 目录/文件 | 说明 | 原因 |
|------------|------|------|
| `venv/` | 虚拟环境 | 本地依赖，服务器重新安装 |
| `node_modules/` | Node 模块 | 本地依赖，服务器重新安装 |
| `.env` | 环境变量 | 包含密钥、密码等敏感信息 |
| `app.db` | SQLite 数据库 | 用户数据，不应该提交 |
| `*.db` | 数据库文件 | 用户数据 |
| `logs/` | 日志目录 | 运行日志，临时文件 |
| `*.log` | 日志文件 | 运行日志，临时文件 |
| `app/static/uploads/` | 上传文件 | 用户上传内容 |
| `static/uploads/` | 上传文件 | 用户上传内容 |
| `.vscode/` | VS Code 配置 | 个人 IDE 配置 |
| `.idea/` | PyCharm 配置 | 个人 IDE 配置 |
| `__pycache__/` | Python 缓存 | 自动生成 |
| `*.pyc` | Python 编译文件 | 自动生成 |
| `.DS_Store` | macOS 系统文件 | 系统自动生成 |
| `Thumbs.db` | Windows 缩略图 | 系统自动生成 |

### Git 提交最佳实践

#### 提交前检查清单

- [ ] 确保 `.env` 文件不在暂存区
- [ ] 确保 `app.db` 不在暂存区
- [ ] 确保 `logs/` 目录不在暂存区
- [ ] 确保上传文件目录不在暂存区
- [ ] 检查代码中没有硬编码的密钥
- [ ] 更新 `requirements.txt`（如有新增依赖）

### 服务器部署步骤

#### 环境要求

- Python 3.8+
- pip
- Git（可选，用于拉取代码）

#### 部署步骤

##### 步骤 1: 拉取代码

```bash
# 如果使用 Git
git clone <repository_url>
cd my_flask_app

# 或者直接上传文件
```

##### 步骤 2: 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

##### 步骤 3: 安装依赖

```bash
pip install -r requirements.txt
```

##### 步骤 4: 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入实际配置
# 设置 SECRET_KEY、邮箱配置、API Key 等
```

**重要**: 服务器上必须设置以下环境变量：

```env
# .env 文件内容示例
SECRET_KEY=your-secret-key-here-change-this-in-production
MAIL_SERVER=smtp.163.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=your-email@163.com
MAIL_PASSWORD=your-email-password
DEEPSEEK_API_KEY=your-deepseek-api-key
```

##### 步骤 5: 初始化数据库

```bash
# 仅初始化数据库
python scripts/init_database.py

# 或者初始化并创建示例数据
python scripts/init_database.py --sample
```

##### 步骤 6: 运行应用（开发环境）

```bash
python run.py
```

##### 步骤 7: 生产环境部署（使用 Gunicorn）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动应用
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 数据库初始化

#### 使用整合后的初始化脚本

```bash
# 方式 1: 仅初始化数据库结构
python scripts/init_database.py

# 方式 2: 交互式初始化
python scripts/init_database.py
# 然后按提示输入 y

# 方式 3: 初始化并创建示例数据
python scripts/init_database.py --sample
```

#### 初始化脚本功能

1. **创建所有数据库表**
2. **迁移用户表（添加 avatar、bio、gender、birthday）**
3. **迁移设备锁字段**
4. **迁移解绑申请字段**
5. **迁移卡密表**
6. **迁移用户素材表**
7. **初始化配置表**

#### 示例数据（使用 --sample 参数）

创建以下示例数据：

- **1 个素材分类**: 副业
- **卡密**: 保持空状态，需要手动添加

### 超级管理员初始化

#### 特性说明

超级管理员账号具有以下特性：

- ✅ **跳过设备锁验证**: 可以在任意设备上登录，无需绑定设备
- ✅ **完整管理员权限**: 可访问管理后台所有功能

#### 初始化超级管理员

运行以下命令创建或更新超级管理员：

```bash
# 通用版（交互式）
python scripts/create_admin.py

# 或宝塔专用版（自动检测路径）
python scripts/create_admin_bt.py
```

#### 登录信息

| 账号 | 邮箱 | 密码 | 用途 |
|------|------|------|------|
| **pc_yujiaqi** | 2798479668@qq.com | **Yun803163** | 电脑端 |
| **pe_yujiaqi** | aa13178775196@163.com | **Yun803163** | 手机端 |

### 常见问题

#### Q: 数据库迁移失败怎么办？

**A**: 如果数据库已存在部分表，初始化脚本会跳过已存在的列，不会报错。

#### Q: 如何重置数据库？

**A**: 删除 `app.db` 文件，重新运行初始化脚本。

```bash
# 删除数据库文件
rm app.db

# 重新初始化
python scripts/init_database.py --sample
```

#### Q: 服务器上如何更新代码？

**A**:

```bash
# 拉取最新代码
git pull

# 激活虚拟环境
source venv/bin/activate

# 安装新依赖（如有）
pip install -r requirements.txt

# 运行数据库迁移（如有）
python scripts/init_database.py

# 重启应用
```

#### Q: 上传文件目录权限问题？

**A**: 确保上传目录有写入权限：

```bash
# Linux/Mac
chmod 755 app/static/uploads
chown -R www-data:www-data app/static/uploads
```

#### Q: 日志文件过大？

**A**: 日志系统已配置轮转，会自动清理旧日志。

---

## 宝塔部署说明

### 前置检查

在开始之前，请确保您已上传以下文件到宝塔服务器：

```
/www/wwwroot/AI-XianYu-Sucai-app/
├── scripts/
│   ├── create_admin_bt.py    # 宝塔专用创建脚本 ⭐
│   ├── diagnose_bt.py        # 环境诊断脚本
│   └── create_admin.py       # 通用脚本
├── app/
├── .env
└── ...
```

### 操作步骤

#### 第一步：进入项目目录

```bash
cd /www/wwwroot/AI-XianYu-Sucai-app
```

#### 第二步：运行环境诊断（可选，推荐）

```bash
/www/wwwroot/AI-XianYu-Sucai-app/0d2605aebbb8df54ac91fdc0ff7e2a95_venv/bin/python3 scripts/diagnose_bt.py
```

**查看诊断结果，确保：**
- ✅ .env 文件存在
- ✅ app 目录存在
- ✅ 可以导入项目模块

#### 第三步：运行创建管理员脚本

```bash
/www/wwwroot/AI-XianYu-Sucai-app/0d2605aebbb8df54ac91fdc0ff7e2a95_venv/bin/python3 scripts/create_admin_bt.py
```

### 账号信息

| 账号 | 邮箱 | 密码 | 用途 |
|------|------|------|------|
| **pc_yujiaqi** | 2798479668@qq.com | **Yun803163** | 电脑端 |
| **pe_yujiaqi** | aa13178775196@163.com | **Yun803163** | 手机端 |

### 常见问题

#### 问题1：提示 "No module named 'app'"

**原因**：Python 路径不正确

**解决**：确保在项目根目录下运行脚本

```bash
cd /www/wwwroot/AI-XianYu-Sucai-app
```

#### 问题2：提示 ".env 文件不存在"

**原因**：.env 文件未上传或路径不对

**解决**：检查 .env 文件是否在项目根目录

#### 问题3：数据库错误

**原因**：数据库路径或权限问题

**解决**：
```bash
# 检查数据库文件权限
chmod 644 /www/wwwroot/AI-XianYu-Sucai-app/app.db
# 检查目录权限
chmod 755 /www/wwwroot/AI-XianYu-Sucai-app
```

#### 问题4：虚拟环境问题

**如果虚拟环境路径不同，请修改为您的实际路径**，例如：

```bash
# 查看虚拟环境位置
ls -la /www/wwwroot/AI-XianYu-Sucai-app/

# 使用正确的虚拟环境 Python
/path/to/your/venv/bin/python3 scripts/create_admin_bt.py
```

### 脚本说明

| 脚本 | 说明 |
|------|------|
| `create_admin_bt.py` | ⭐ 宝塔专用，推荐使用，自动检测路径 |
| `create_admin.py` | 通用版本，需要交互式确认 |
| `diagnose_bt.py` | 环境诊断，帮助排查问题 |

### 提示

- ✅ 脚本不会清除任何现有数据
- ✅ 如果账号已存在，会自动更新邮箱和权限
- ✅ 操作前建议先备份数据库

---

## 网站上线部署手册

### 核心环境档案

* **服务器 IP**：`122.152.232.182`
* **操作系统**：OpenCloudOS 9 (CentOS 兼容版)
* **管理面板**：宝塔面板 (端口 8888)
* **项目路径**：`/www/wwwroot/AI-XianYu-Sucai-app`
* **技术栈细节**：
* **Python**: 3.11.4
* **Web 服务器**: Gunicorn (工作进程管理)
* **反向代理**: Nginx (处理 80 端口转发)
* **数据库**: SQLite 3 (文件名为 `app.db`)

### 第一阶段：GitHub 代码仓库深度清理

在部署前，必须确保仓库中不含垃圾文件，否则会导致服务器依赖冲突。

#### 修正 `.gitignore`

确保本地项目根目录下的 `.gitignore` 包含以下内容：

```text
venv/
__pycache__/
*.pyc
instance/
.env
node_modules/
app.db
```

#### 强制同步仓库（解决忽略文件不起作用的问题）

在本地终端执行，将已上传的垃圾文件从 GitHub 索引中剔除：

```bash
git rm -r --cached .      # 清空 Git 对当前目录所有文件的追踪索引
git add .                 # 重新按 .gitignore 规则读取文件
git commit -m "chore: 彻底清理 node_modules 和缓存"
git push origin main
```

### 第二阶段：服务器"纯净级"部署流程

#### 彻底清空旧环境

进入宝塔【文件】，在 `/www/wwwroot/AI-XianYu-Sucai-app` 目录下打开终端：

```bash
rm -rf .* * # 强制删除包括隐藏文件在内的所有内容，确保 clone 目录为空
```

#### 拉取代码

```bash
git clone https://github.com/yujiaqi3163/AI-XianYu-Sucai-app.git .
```

#### Python 项目管理器设置

* **添加项目**：
* **路径**：`/www/wwwroot/AI-XianYu-Sucai-app`
* **启动方式**：`gunicorn`（**严禁**直接用 python 启动，gunicorn 更稳定）
* **启动文件**：`run.py` | **端口**：`5000`
* **勾选**：安装模块依赖

* **补全缺失模块**：
点击【模块】，手动安装 `email-validator`。注册功能报错 `Internal Server Error` 通常是因为漏掉这个包。

#### 权限与所有者（最易出错点）

由于 Gunicorn 以 `www` 用户运行，必须保证它对数据库有写权限：

* **操作**：在宝塔【文件】中对项目文件夹右键 -> 【权限】。
* **设置**：所有者选择 **`www`**，权限 **755**，务必勾选 **"应用到子目录"**。

### 第三阶段：后续更新与同步 SOP

当你在本地修改了代码（例如修改了 HTML 或增加了新路由），请执行此标准流程：

#### 步骤 1：本地推送

```bash
git add .
git commit -m "update: 描述你的修改内容"
git push origin main
```

#### 步骤 2：服务器同步

1. 登录宝塔，进入项目目录终端。
2. 执行 `git pull`。
3. **核心动作**：回到【Python 项目管理器】，点击 **【重启】**。

#### 步骤 3：数据库变更处理（高能预警）

* **如果是 UI/逻辑修改**：只需重启。
* **如果是修改了数据库表结构**：
1. **备份**：先把服务器上的 `app.db` 下载到本地。
2. **更新**：在本地完成数据库迁移（Migration）后，将新的 `app.db` 上传覆盖（注意：这会覆盖掉服务器上的新注册用户数据，建议在正式运营后改用 `Flask-Migrate` 进行增量更新）。

### 故障应急排查清单

| 现象 | 可能原因 | 解决方案 |
| --- | --- | --- |
| **网页显示 502 Bad Gateway** | Gunicorn 进程挂了 | 在管理器中点击重启；检查日志看是否有代码语法错误。 |
| **注册/提交显示 500 Error** | 权限不足 / 缺少模块 | 1. 确认 `app.db` 所有者是 `www`；2. 检查日志是否有 `ModuleNotFoundError`。 |
| **修改了代码但网页没变** | 缓存 / 未重启 | 1. 必须在管理器点"重启"；2. 浏览器开启无痕模式访问。 |
| **数据库尝试写入只读文件** | 文件夹权限被重置 | 再次执行"应用到子目录"的所有者权限修改（www/755）。 |

### 进阶安全建议

1. **安全组**：腾讯云后台只需开放 `80`, `443`, `8888`, `22`。`5000` 端口在开启 Nginx 映射后可以关闭，增加安全性。
2. **备份任务**：在宝塔【计划任务】添加一个"备份目录"，每天凌晨 3 点执行，备份 `/www/wwwroot/AI-XianYu-Sucai-app`。

---

## 常见问题

### 本地开发常见问题

#### Q: Redis 未启动怎么办？

**A**: 启动 Redis 或 Memurai

```bash
# Windows
redis-server.exe
# 或
memurai.exe

# Docker
docker run -d -p 6379:6379 --name my-redis redis:alpine
```

#### Q: 任务一直"等待中"？

**A**: 确保 Celery Worker 已启动

```bash
# Windows
python -m celery -A celery_config worker --loglevel=info --pool=solo

# Linux/Mac
celery -A celery_config worker --loglevel=info
```

#### Q: `No module named 'celery'`？

**A**: 安装依赖

```bash
pip install -r requirements.txt
```

### 服务器部署常见问题

#### Q: 502 Bad Gateway？

**A**: Gunicorn 进程挂了，在宝塔 Python 项目管理器中点击重启，检查日志看是否有代码语法错误。

#### Q: 500 Internal Server Error？

**A**: 
1. 确认 `app.db` 所有者是 `www`
2. 检查日志是否有 `ModuleNotFoundError`，可能缺少 `email-validator` 等模块

#### Q: 修改了代码但网页没变？

**A**:
1. 必须在宝塔 Python 项目管理器点"重启"
2. 浏览器开启无痕模式访问

#### Q: 数据库尝试写入只读文件？

**A**: 再次执行"应用到子目录"的所有者权限修改（www/755）

### 模型导入问题

#### Q: `ImportError: cannot import name 'UserFavorite'`？

**A**: 检查以下几点：
1. 确保 `app/models/user_favorite.py` 文件存在
2. 确保 `app/models/__init__.py` 包含 `from app.models.user_favorite import UserFavorite`
3. 确保 `app/models/__init__.py` 的 `__all__` 列表包含 `'UserFavorite'`
4. 在服务器上运行 `scripts/diagnose_imports.py` 诊断具体问题

---

## 项目总结

这是一个功能完整、安全可靠的 Flask 素材管理系统，包含：

| 功能类别 | 主要功能 |
|---------|---------|
| **用户认证** | 登录、注册、找回密码、设备锁 |
| **个人中心** | 资料修改、安全中心、密码修改 |
| **素材功能** | 浏览、详情、二创（AI 优化）、我的素材 |
| **管理后台** | 素材管理、批量上传、用户管理、权限管理、卡密管理 |
| **安全防护** | SQL 注入防护、CSRF 防护、XSS 防护、API 限流、密码加密 |
| **异步处理** | Celery + Redis 异步任务、DeepSeek API 调用 |
| **日志系统** | 操作日志、错误日志、日志滚动 |

---

**文档版本**: v3.1
**最后更新**: 2026-02-25
