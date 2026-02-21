# 导入操作系统相关模块
import os
# 导入 Flask 框架
from flask import Flask
# 导入数据库扩展
from flask_sqlalchemy import SQLAlchemy
# 导入用户登录管理扩展
from flask_login import LoginManager
# 导入环境变量加载
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取项目根目录路径
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 配置类
class Config:
    # 密钥，用于加密 session 等
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # 数据库连接地址
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # 关闭数据库修改跟踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 禁用CSRF保护（临时，方便开发）
    WTF_CSRF_ENABLED = False

# 初始化数据库对象
db = SQLAlchemy()

# 创建应用的工厂函数
def create_app(config_class=Config):
    # 创建 Flask 应用实例，指定模板和静态文件目录
    app = Flask(__name__, template_folder='templates', static_folder='static')
    # 加载配置
    app.config.from_object(config_class)

    # 初始化数据库
    db.init_app(app)

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

    # 返回应用实例
    return app
