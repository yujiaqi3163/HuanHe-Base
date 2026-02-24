# ============================================================
# user_favorite.py
# 
# 用户收藏素材模型
# 功能说明：
# 1. UserFavorite 表：用户收藏的素材记录
# ============================================================

from datetime import datetime
from app import db


class UserFavorite(db.Model):
    __tablename__ = 'user_favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('favorites', lazy=True, cascade='all, delete-orphan'))
    material = db.relationship('Material', backref=db.backref('favorites', lazy=True, cascade='all, delete-orphan'))

    __table_args__ = (db.UniqueConstraint('user_id', 'material_id', name='_user_material_favorite_uc'),)

    def __repr__(self):
        return f'<UserFavorite user={self.user_id} material={self.material_id}>'
