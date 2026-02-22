# 导入操作系统相关模块
import os
# 导入 Flask 框架
from flask import Flask, session, request, redirect, url_for, flash, jsonify
# 导入数据库扩展
from flask_sqlalchemy import SQLAlchemy
# 导入用户登录管理扩展
from flask_login import LoginManager, current_user
# 导入邮件扩展
from flask_mail import Mail
# 导入环境变量加载
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取项目根目录路径
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 全局 Celery 实例
celery_app = None

# 配置类
class Config:
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
    """初始化 Celery"""
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

# 创建应用的工厂函数
def create_app(config_class=Config):
    # 创建 Flask 应用实例，指定模板和静态文件目录
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
    # 设置登录页面路由
    login_manager.login_view = 'auth.login'
    # 设置未登录提示消息
    login_manager.login_message = '请先登录以访问此页面'
    # 设置提示消息分类
    login_manager.login_message_category = 'info'

    # 导入用户模型
    from app.models.user import User
    # 定义加载用户的回调函数
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 全局设备锁验证
    @app.before_request
    def check_device_lock():
        # 跳过不需要验证的路径
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
        
        # 如果用户已登录
        if current_user.is_authenticated:
            # 超级管理员跳过设备锁验证
            if current_user.is_super_admin:
                return
            
            # 优先从session获取device_id，如果没有则从cookie获取
            session_device_id = session.get('device_id')
            if not session_device_id:
                session_device_id = request.cookies.get('device_id')
                # 如果从cookie获取到了，保存到session
                if session_device_id:
                    session['device_id'] = session_device_id
            
            db_device_id = current_user.bound_device_id
            
            # 如果数据库中有绑定的设备ID
            if db_device_id:
                # 检查设备ID是否匹配
                if not session_device_id or session_device_id != db_device_id:
                    # 设备不匹配，强制退出
                    from flask_login import logout_user
                    logout_user()
                    session.pop('device_id', None)
                    
                    # 判断是API请求还是普通请求
                    if request.path.startswith('/api/'):
                        return jsonify({
                            'success': False,
                            'message': '该账号已绑定其他设备，请先解绑'
                        }), 403
                    else:
                        flash('该账号已绑定其他设备，请先解绑', 'danger')
                        return redirect(url_for('auth.login'))

    # 导入主路由蓝图
    from app.routes import main_bp
    # 导入认证路由蓝图
    from app.routes.auth import auth_bp
    # 导入管理后台路由蓝图
    from app.routes import admin_bp
    # 注册主路由蓝图
    app.register_blueprint(main_bp)
    # 注册认证路由蓝图，前缀为 /auth
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # 注册管理后台路由蓝图，前缀为 /admin
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 配置日志系统
    from app.utils.logger import setup_logging
    setup_logging(app)
    
    # 初始化 Redis 分布式限流器
    from app.utils.rate_limit import init_limiter
    init_limiter(app)
    
    # 返回应用实例
    return app
