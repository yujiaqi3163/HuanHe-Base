from flask import Blueprint, render_template, redirect, url_for, flash, request  # 导入Flask相关模块
from flask_login import login_user, logout_user, current_user  # 导入用户认证相关模块
from datetime import datetime  # 导入日期时间模块
from app import db  # 导入数据库实例
from app.models import User, RegisterSecret  # 导入数据模型
from app.forms import LoginForm, RegisterForm  # 导入表单类

bp = Blueprint('auth', __name__, url_prefix='/auth')  # 创建认证路由蓝图


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # 如果用户已登录
        return redirect(url_for('main.index'))  # 重定向到首页
    
    form = LoginForm()  # 创建登录表单实例
    
    if form.validate_on_submit():  # 如果表单验证通过
        user = User.query.filter(  # 根据用户名或邮箱查询用户
            (User.username == form.username_or_email.data) | 
            (User.email == form.username_or_email.data)
        ).first()
        
        if user and user.check_password(form.password.data):  # 如果用户存在且密码正确
            login_user(user, remember=form.remember.data)  # 登录用户
            next_page = request.args.get('next')  # 获取下一页地址
            flash('登录成功！', 'success')  # 显示成功消息
            return redirect(next_page if next_page else url_for('main.index'))  # 重定向
        
        flash('用户名/邮箱或密码错误', 'danger')  # 显示错误消息
    
    return render_template('auth/login.html', form=form)  # 渲染登录页面


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:  # 如果用户已登录
        return redirect(url_for('main.index'))  # 重定向到首页
    
    form = RegisterForm()  # 创建注册表单实例
    
    if form.validate_on_submit():  # 如果表单验证通过
        register_secret = RegisterSecret.query.filter_by(secret=form.secret.data).first()  # 查询注册卡密
        
        user = User(  # 创建新用户
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        
        db.session.add(user)  # 添加用户到数据库会话
        db.session.flush()  # 刷新会话获取用户ID
        
        register_secret.is_used = True  # 标记卡密已使用
        register_secret.user_id = user.id  # 关联用户ID
        register_secret.used_at = datetime.utcnow()  # 记录使用时间
        
        db.session.commit()  # 提交到数据库
        
        flash('注册成功！请登录', 'success')  # 显示成功消息
        return redirect(url_for('auth.login'))  # 重定向到登录页
    
    return render_template('auth/register.html', form=form)  # 渲染注册页面


@bp.route('/logout')
def logout():
    logout_user()  # 退出登录
    flash('已成功退出登录', 'info')  # 显示消息
    return redirect(url_for('auth.login'))  # 重定向到首页
