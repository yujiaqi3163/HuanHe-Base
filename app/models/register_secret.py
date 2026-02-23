# ============================================================
# register_secret.py
# 
# 注册密钥模型
# 功能说明：
# 1. RegisterSecret 表：注册邀请码管理
# ============================================================

# 导入日期时间模块
from datetime import datetime
# 导入数据库对象
from app import db


# 注册卡密模型类
class RegisterSecret(db.Model):
    # 数据库表名
    __tablename__ = 'register_secrets'

    # 卡密ID，主键
    id = db.Column(db.Integer, primary_key=True)
    # 卡密内容，唯一，不能为空，添加索引
    secret = db.Column(db.String(100), unique=True, nullable=False, index=True)
    # 是否已使用，默认为否
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    # 绑定的用户ID，外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    # 创建时间，默认为当前时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # 使用时间，可以为空
    used_at = db.Column(db.DateTime, nullable=True)
    # 卡密时长类型: 1min-1分钟, 1day-日卡, 1month-月卡, 1year-年卡, permanent-永久
    duration_type = db.Column(db.String(20), nullable=False, default='permanent')
    # 过期时间（可选，只有有时长的卡密才有）
    expires_at = db.Column(db.DateTime, nullable=True)

    # 打印时的显示格式
    def __repr__(self):
        return f'<RegisterSecret {self.secret}>'
