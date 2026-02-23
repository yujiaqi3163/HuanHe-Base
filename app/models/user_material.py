# ============================================================
# user_material.py
# 
# 用户二创素材模型
# 功能说明：
# 1. UserMaterial 表：用户二创的素材记录
# 2. UserMaterialImage 表：用户二创素材的图片
# ============================================================

# 导入日期时间模块
from datetime import datetime
# 导入数据库对象
from app import db


# 用户二创素材模型类
class UserMaterial(db.Model):
    # 数据库表名
    __tablename__ = 'user_materials'

    # 二创素材ID，主键
    id = db.Column(db.Integer, primary_key=True)
    # 关联的用户ID，外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 原始素材ID，外键（可空，如果用户自己创建的素材没有原始素材）
    original_material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    # 二创标题（与原素材相同）
    title = db.Column(db.String(200), nullable=False)
    # 二创文案（DeepSeek优化后的）
    description = db.Column(db.Text, nullable=True)
    # 原始文案（备份）
    original_description = db.Column(db.Text, nullable=True)
    # 浏览次数
    view_count = db.Column(db.Integer, default=0, nullable=False)
    # 下载次数
    download_count = db.Column(db.Integer, default=0, nullable=False)
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 与二创图片的一对多关系
    images = db.relationship('UserMaterialImage', backref='user_material', lazy=True, cascade='all, delete-orphan', order_by='UserMaterialImage.sort_order')

    # 与用户的关系
    user = db.relationship('User', backref=db.backref('user_materials', lazy=True, cascade='all, delete-orphan'))

    # 与原始素材的关系
    original_material = db.relationship('Material', backref=db.backref('user_materials', lazy=True))

    # 打印时的显示格式
    def __repr__(self):
        return f'<UserMaterial {self.title}>'


# 用户二创素材图片模型类
class UserMaterialImage(db.Model):
    # 数据库表名
    __tablename__ = 'user_material_images'

    # 图片ID，主键
    id = db.Column(db.Integer, primary_key=True)
    # 关联的二创素材ID，外键
    user_material_id = db.Column(db.Integer, db.ForeignKey('user_materials.id'), nullable=False)
    # 图片URL或路径
    image_url = db.Column(db.String(500), nullable=False)
    # 图片排序，数值越小越靠前
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    # 是否为封面图，默认为否
    is_cover = db.Column(db.Boolean, default=False, nullable=False)
    # 原始图片URL（备份）
    original_image_url = db.Column(db.String(500), nullable=True)
    # CSS混合配方（记录用于复现）
    css_recipe = db.Column(db.Text, nullable=True)
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 打印时的显示格式
    def __repr__(self):
        return f'<UserMaterialImage {self.id}>'
