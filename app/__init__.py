# ============================================================
# Flask 应用工厂模块
# 
# 功能说明：
# 1. 创建 Flask 应用实例（工厂模式）
# 2. 初始化数据库（SQLAlchemy）
# 3. 初始化邮件服务（Flask-Mail）
# 4. 初始化 Celery 异步任务队列
# 5. 初始化用户登录管理（Flask-Login）
# 6. 初始化 Redis 分布式限流器（Flask-Limiter）
# 7. 设备绑定验证中间件
# 8. 注册所有路由蓝图
# 
# 核心函数：
# - create_app(): Flask 应用工厂函数
# - init_celery(): 初始化 Celery 异步任务
# ============================================================

import os
from flask import Flask, session, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Mail
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取项目根目录路径
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 全局 Celery 实例
celery_app = None


class Config:
    """Flask 应用配置类"""
    
    # 密钥，用于加密 session 等
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY 环境变量未设置，请在 .env 文件中配置")
    
    # 数据库连接地址
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # 关闭数据库修改跟踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 启用CSRF保护
    WTF_CSRF_ENABLED = True
    # 记住登录状态的有效期（30天）
    REMEMBER_COOKIE_DURATION = 30 * 24 * 60 * 60
    # 最大上传文件大小 100MB（Flask 层面的限制）
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    
    # Celery 配置
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # 邮件配置（163 邮箱 SMTP）
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME') or ''


# 初始化数据库对象
db = SQLAlchemy()

# 初始化邮件对象
mail = Mail()


def init_celery(app):
    """初始化 Celery
    
    Args:
        app: Flask 应用实例
    
    Returns:
        Celery 实例
    """
    from celery import Celery
    
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery


def create_app(config_class=Config):
    """Flask 应用工厂函数
    
    Args:
        config_class: 配置类
    
    Returns:
        Flask 应用实例
    """
    # 创建 Flask 应用实例
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # 加载配置
    app.config.from_object(config_class)
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化邮件
    mail.init_app(app)
    
    # 初始化 Celery
    global celery_app
    celery_app = init_celery(app)
    
    # 初始化登录管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录以访问此页面'
    login_manager.login_message_category = 'info'
    
    # 导入用户模型并定义加载用户的回调函数
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 初始化 Redis 分布式限流器（必须在注册蓝图之前！）
    from app.utils.rate_limit import init_limiter
    init_limiter(app)
    
    # 全局设备锁验证中间件
    @app.before_request
    def check_device_lock():
        skip_paths = [
            '/auth/login',
            '/auth/register',
            '/auth/logout',
            '/auth/api/login',
            '/auth/save-device-id',
            '/static/',
            '/favicon.ico'
        ]
        
        for path in skip_paths:
            if request.path.startswith(path):
                return
        
        if current_user.is_authenticated:
            if current_user.is_super_admin:
                return
            
            session_device_id = session.get('device_id')
            if not session_device_id:
                session_device_id = request.cookies.get('device_id')
                if session_device_id:
                    session['device_id'] = session_device_id
            
            db_device_id = current_user.bound_device_id
            
            if db_device_id:
                if not session_device_id or session_device_id != db_device_id:
                    from flask_login import logout_user
                    logout_user()
                    session.pop('device_id', None)
                    
                    if request.path.startswith('/api/'):
                        return jsonify({
                            'success': False,
                            'message': '该账号已绑定其他设备，请先解绑'
                        }), 403
                    else:
                        flash('该账号已绑定其他设备，请先解绑', 'danger')
                        return redirect(url_for('auth.login'))
    
    # 导入并注册路由蓝图
    from app.routes import main_bp
    from app.routes.auth import auth_bp
    from app.routes import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # 配置日志系统
    from app.utils.logger import setup_logging
    setup_logging(app)
    
    return app
