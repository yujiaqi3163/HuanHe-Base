# ============================================================
# announcement.py
# 
# 公告数据模型
# 功能说明：
# 1. Announcement 表：公告信息（标题、内容、发布时间）
# ============================================================

# 导入日期时间模块
from datetime import datetime
# 导入数据库对象
from app import db


# 公告模型类
class Announcement(db.Model):
    # 数据库表名
    __tablename__ = 'announcements'

    # 公告ID，主键
    id = db.Column(db.Integer, primary_key=True)
    # 公告标题，不能为空，添加索引
    title = db.Column(db.String(200), nullable=False, index=True)
    # 公告内容，支持长文本
    content = db.Column(db.Text, nullable=False)
    # 是否发布，默认为True
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    # 排序权重，数值越大越靠前
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    # 创建时间，默认为当前时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # 最后修改时间，自动更新
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 打印时的显示格式
    def __repr__(self):
        return f'<Announcement {self.title}>'
