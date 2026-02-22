# 导入日期时间模块
from datetime import datetime
# 导入密码加密和验证函数
from werkzeug.security import generate_password_hash, check_password_hash
# 导入数据库对象
from app import db
# 导入用户登录混入类
from flask_login import UserMixin


# 用户模型类
class User(UserMixin, db.Model):
    # 数据库表名
    __tablename__ = 'users'

    # 用户ID，主键
    id = db.Column(db.Integer, primary_key=True)
    # 用户名，唯一，不能为空，添加索引
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    # 邮箱，唯一，不能为空，添加索引
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    # 密码哈希值
    password_hash = db.Column(db.String(256), nullable=False)
    # 是否为管理员，默认为否
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    # 是否为超级管理员，默认为否
    is_super_admin = db.Column(db.Boolean, default=False, nullable=False)
    # 创建时间，默认为当前时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # 头像URL
    avatar = db.Column(db.String(500), nullable=True)
    # 个性签名
    bio = db.Column(db.String(200), nullable=True)
    # 性别：male-男，female-女，other-其他，null-未设置
    gender = db.Column(db.String(10), nullable=True)
    # 出生日期
    birthday = db.Column(db.Date, nullable=True)
    # 绑定的设备ID
    bound_device_id = db.Column(db.String(200), nullable=True)
    
    # 设备解绑状态：0-正常，1-申请中
    device_unbind_status = db.Column(db.Integer, default=0, nullable=False)
    
    # 设备解绑申请时间
    device_unbind_requested_at = db.Column(db.DateTime, nullable=True)

    # 与注册卡密的一对多关系，级联删除
    register_secrets = db.relationship('RegisterSecret', backref='user', lazy=True, cascade='all, delete-orphan')

    # 密码属性（只读）
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # 设置密码，自动加密
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 打印时的显示格式
    def __repr__(self):
        return f'<User {self.username}>'
