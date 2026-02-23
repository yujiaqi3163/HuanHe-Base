# ============================================================
# material_type.py
# 
# 素材分类表单模块
# 功能说明：
# 1. 素材分类添加/编辑表单
# ============================================================

# 导入Flask-WTF表单模块
from flask_wtf import FlaskForm
# 导入WTForms字段类型
from wtforms import StringField, SubmitField
# 导入WTForms验证器
from wtforms.validators import DataRequired, Length, Optional


# 素材类型表单类
class MaterialTypeForm(FlaskForm):
    # 类型名称
    name = StringField(
        '分类名称',
        validators=[
            DataRequired(message='请输入分类名称'),
            Length(max=50, message='分类名称最多50个字符')
        ]
    )
    # 类型描述
    description = StringField(
        '分类描述',
        validators=[
            Optional(),
            Length(max=200, message='分类描述最多200个字符')
        ]
    )
    # 提交按钮
    submit = SubmitField('保存')
