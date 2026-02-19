from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User, RegisterSecret


class LoginForm(FlaskForm):
    username_or_email = StringField('用户名/邮箱', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password', message='两次密码输入不一致')])
    secret = StringField('注册密钥', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱')

    def validate_secret(self, secret):
        register_secret = RegisterSecret.query.filter_by(secret=secret.data).first()
        if not register_secret:
            raise ValidationError('注册密钥无效，请检查后重试')
        if register_secret.is_used:
            raise ValidationError('该注册密钥已被使用')
