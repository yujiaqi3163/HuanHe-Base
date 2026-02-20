# 导入日期时间模块
from datetime import datetime
# 导入数据库对象
from app import db


# 素材图片模型类
class MaterialImage(db.Model):
    # 数据库表名
    __tablename__ = 'material_images'

    # 图片ID，主键
    id = db.Column(db.Integer, primary_key=True)
    # 关联的素材ID，外键
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    # 图片URL或路径
    image_url = db.Column(db.String(500), nullable=False)
    # 图片排序，数值越小越靠前
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    # 是否为封面图，默认为否
    is_cover = db.Column(db.Boolean, default=False, nullable=False)
    # 创建时间，默认为当前时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 打印时的显示格式
    def __repr__(self):
        return f'<MaterialImage {self.id}>'
