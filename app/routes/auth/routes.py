from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from datetime import datetime
from app import db
from app.models import User, RegisterSecret
from app.forms import LoginForm, RegisterForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username_or_email.data) | 
            (User.email == form.username_or_email.data)
        ).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('登录成功！', 'success')
            return redirect(next_page if next_page else url_for('main.index'))
        
        flash('用户名/邮箱或密码错误', 'danger')
    
    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        register_secret = RegisterSecret.query.filter_by(secret=form.secret.data).first()
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        
        db.session.add(user)
        db.session.flush()
        
        register_secret.is_used = True
        register_secret.user_id = user.id
        register_secret.used_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('注册成功！请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    flash('已成功退出登录', 'info')
    return redirect(url_for('main.index'))
