# ============================================================
# auth.py
# 
# 认证表单模块
# 功能说明：
# 1. LoginForm: 登录表单
# 2. RegisterForm: 注册表单
# ============================================================

# 导入 Flask-WTF 表单基类
from flask_wtf import FlaskForm
# 导入表单字段类型
from wtforms import StringField, PasswordField, BooleanField, SubmitField
# 导入表单验证器
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
# 导入数据模型
from app.models import User, RegisterSecret
import re


def validate_password_strength(form, field):
    """验证密码强度"""
    password = field.data
    # 检查密码长度
    if len(password) < 8:
        raise ValidationError('密码长度至少为8位')
    
    # 检查是否包含大写字母
    if not re.search(r'[A-Z]', password):
        raise ValidationError('密码必须包含至少一个大写字母')
    
    # 检查是否包含小写字母
    if not re.search(r'[a-z]', password):
        raise ValidationError('密码必须包含至少一个小写字母')
    
    # 检查是否包含数字
    if not re.search(r'[0-9]', password):
        raise ValidationError('密码必须包含至少一个数字')
    
    # 检查是否包含特殊字符
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('密码必须包含至少一个特殊字符(!@#$%^&*(),.?":{}|<>)')


# 登录表单类
class LoginForm(FlaskForm):
    # 用户名/邮箱字段：必填，最大120字符
    username_or_email = StringField('用户名/邮箱', validators=[DataRequired(), Length(max=120)])
    # 密码字段：必填
    password = PasswordField('密码', validators=[DataRequired()])
    # 记住我复选框
    remember = BooleanField('记住我')
    # 登录按钮
    submit = SubmitField('登录')


# 注册表单类
class RegisterForm(FlaskForm):
    # 用户名字段：必填，3-80字符
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=80)])
    # 邮箱字段：必填，邮箱格式验证，最大120字符
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(max=120)])
    # 验证码字段：必填，6位数字
    code = StringField('验证码', validators=[DataRequired(), Length(min=6, max=6)])
    # 密码字段：必填，强度验证
    password = PasswordField('密码', validators=[
        DataRequired(),
        Length(min=8),
        validate_password_strength
    ])
    # 确认密码字段：必填，必须与密码一致
    password2 = PasswordField('确认密码', validators=[
        DataRequired(),
        EqualTo('password', message='两次密码输入不一致')
    ])
    # 注册密钥字段：必填，最大100字符
    secret = StringField('注册密钥', validators=[DataRequired(), Length(max=100)])
    # 注册按钮
    submit = SubmitField('注册')

    # 自定义用户名验证：检查用户名是否已存在
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名')

    # 自定义邮箱验证：检查邮箱是否已注册
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱')

    # 自定义卡密验证：检查卡密是否有效且未使用
    def validate_secret(self, secret):
        register_secret = RegisterSecret.query.filter_by(secret=secret.data).first()
        if not register_secret:
            raise ValidationError('注册密钥无效，请检查后重试')
        if register_secret.is_used:
            raise ValidationError('该注册密钥已被使用')


# 忘记密码表单类
class ForgotPasswordForm(FlaskForm):
    # 邮箱字段：必填，邮箱格式验证
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(max=120)])
    # 验证码字段：必填，6位数字
    code = StringField('验证码', validators=[DataRequired(), Length(min=6, max=6)])
    # 提交按钮
    submit = SubmitField('重置密码')


# 修改密码表单类
class ChangePasswordForm(FlaskForm):
    # 原密码字段：必填
    old_password = PasswordField('原密码', validators=[DataRequired()])
    # 新密码字段：必填，强度验证
    new_password = PasswordField('新密码', validators=[
        DataRequired(),
        Length(min=8),
        validate_password_strength
    ])
    # 确认密码字段：必填，必须与新密码一致
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(),
        EqualTo('new_password', message='两次密码输入不一致')
    ])
    # 提交按钮
    submit = SubmitField('修改密码')
