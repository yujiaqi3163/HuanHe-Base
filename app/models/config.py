# ============================================================
# config.py
# 
# 系统配置模型
# 功能说明：
# 1. Config 表：存储系统全局配置（如客服微信等）
# ============================================================

# 配置模型
from app import db
from datetime import datetime


class Config(db.Model):
    """系统配置表"""
    __tablename__ = 'configs'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @staticmethod
    def get_value(key, default=None):
        """获取配置值"""
        config = Config.query.filter_by(key=key).first()
        return config.value if config else default
    
    @staticmethod
    def set_value(key, value, description=None):
        """设置配置值"""
        config = Config.query.filter_by(key=key).first()
        if config:
            config.value = value
            if description:
                config.description = description
        else:
            config = Config(
                key=key,
                value=value,
                description=description
            )
            db.session.add(config)
        db.session.commit()
        return config
