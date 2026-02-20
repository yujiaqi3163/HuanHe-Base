# 导入日期时间模块
from datetime import datetime
# 导入数据库对象
from app import db


# 素材类型模型类
class MaterialType(db.Model):
    # 数据库表名
    __tablename__ = 'material_types'

    # 类型ID，主键
    id = db.Column(db.Integer, primary_key=True)
    # 类型名称，唯一，不能为空，添加索引
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    # 类型描述，可选
    description = db.Column(db.String(200), nullable=True)
    # 排序权重，数值越小越靠前
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    # 是否启用，默认为是
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # 创建时间，默认为当前时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 与素材的一对多关系
    materials = db.relationship('Material', backref='material_type', lazy=True)

    # 打印时的显示格式
    def __repr__(self):
        return f'<MaterialType {self.name}>'
