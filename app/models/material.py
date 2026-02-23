# ============================================================
# material.py
# 
# 素材数据模型
# 功能说明：
# 1. Material 表：素材基本信息、描述、上架状态
# 2. MaterialType 表：素材分类
# 3. MaterialImage 表：素材图片
# ============================================================

# 导入日期时间模块
from datetime import datetime
# 导入数据库对象
from app import db


# 素材模型类
class Material(db.Model):
    # 数据库表名
    __tablename__ = 'materials'

    # 素材ID，主键
    id = db.Column(db.Integer, primary_key=True)
    # 素材标题，不能为空，添加索引
    title = db.Column(db.String(200), nullable=False, index=True)
    # 素材文案，可选
    description = db.Column(db.Text, nullable=True)
    # 素材类型ID，外键
    material_type_id = db.Column(db.Integer, db.ForeignKey('material_types.id'), nullable=True)
    # 浏览次数（热度），默认为0
    view_count = db.Column(db.Integer, default=0, nullable=False)
    # 收藏次数，默认为0
    favorite_count = db.Column(db.Integer, default=0, nullable=False)
    # 下载次数，默认为0
    download_count = db.Column(db.Integer, default=0, nullable=False)
    # 是否上架，默认为是
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    # 排序权重，数值越小越靠前
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    # 创建时间，默认为当前时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # 最后修改时间，自动更新
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 与素材图片的一对多关系
    images = db.relationship('MaterialImage', backref='material', lazy=True, cascade='all, delete-orphan', order_by='MaterialImage.sort_order')

    # 打印时的显示格式
    def __repr__(self):
        return f'<Material {self.title}>'
