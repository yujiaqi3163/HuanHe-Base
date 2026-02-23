# ============================================================
# admin.py
# 
# 管理后台表单模块
# 功能说明：
# 1. 素材管理表单
# 2. 用户管理表单
# 3. 配置管理表单
# ============================================================

# 导入Flask-WTF表单相关模块
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
# 导入WTForms字段类型
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
# 导入WTForms验证器
from wtforms.validators import DataRequired, Length, Optional


# 素材表单类
class MaterialForm(FlaskForm):
    # 素材标题
    title = StringField(
        '素材标题',
        validators=[
            DataRequired(message='请输入素材标题'),
            Length(max=200, message='标题最多200个字符')
        ]
    )
    # 素材文案
    description = TextAreaField(
        '素材文案',
        validators=[DataRequired(message='请输入素材文案')]
    )
    # 素材类型
    material_type_id = SelectField(
        '素材类型',
        validators=[DataRequired(message='请选择素材类型')],
        coerce=int
    )
    # 是否上架
    is_published = BooleanField(
        '立即上架',
        default=True
    )
    # 提交按钮
    submit = SubmitField('保存素材')
