# ============================================================
# permission.py
# 
# 权限管理模型
# 功能说明：
# 1. Permission 表：权限定义
# 2. UserPermission 表：用户权限分配
# ============================================================

from datetime import datetime
from app import db


class Permission(db.Model):
    """权限模型"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user_permissions = db.relationship('UserPermission', backref='permission', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Permission {self.code}>'


class UserPermission(db.Model):
    """用户权限关联模型"""
    __tablename__ = 'user_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'permission_id', name='_user_permission_uc'),
    )
    
    def __repr__(self):
        return f'<UserPermission user_id={self.user_id} permission_id={self.permission_id}>'


def init_permissions():
    """初始化默认权限"""
    permissions_data = [
        ('material_manage', '素材管理', '管理素材的增删改查'),
        ('secret_manage', '卡密管理', '管理注册卡密'),
        ('user_manage', '用户管理', '管理用户账号'),
        ('type_manage', '分类管理', '管理素材分类'),
        ('config_manage', '设置客服微信', '修改客服微信号设置'),
    ]
    
    for code, name, description in permissions_data:
        if not Permission.query.filter_by(code=code).first():
            permission = Permission(
                code=code,
                name=name,
                description=description
            )
            db.session.add(permission)
    
    db.session.commit()
