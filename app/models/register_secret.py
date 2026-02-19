from datetime import datetime
from app import db


class RegisterSecret(db.Model):
    __tablename__ = 'register_secrets'

    id = db.Column(db.Integer, primary_key=True) #卡密ID
    secret = db.Column(db.String(100), unique=True, nullable=False, index=True) #卡密
    is_used = db.Column(db.Boolean, default=False, nullable=False) #是否使用
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) #卡密绑定的用户ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) #创建时间
    used_at = db.Column(db.DateTime, nullable=True) #使用时间

    def __repr__(self):
        return f'<RegisterSecret {self.secret}>'
