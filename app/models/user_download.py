# ============================================================
# user_download.py
# 
# 用户下载素材模型
# 功能说明：
# 1. UserDownload 表：用户下载的素材记录（可以是原始素材或用户二创素材）
# ============================================================

from datetime import datetime
from app import db


class UserDownload(db.Model):
    __tablename__ = 'user_downloads'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 可以是原始素材或用户二创素材，二选一即可
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    user_material_id = db.Column(db.Integer, db.ForeignKey('user_materials.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('downloads', lazy=True, cascade='all, delete-orphan'))
    material = db.relationship('Material', backref=db.backref('downloads', lazy=True))
    user_material = db.relationship('UserMaterial', backref=db.backref('downloads', lazy=True))

    def __repr__(self):
        return f'<UserDownload user={self.user_id}>'
