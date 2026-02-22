from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, current_app  # 导入Flask相关模块
from flask_login import login_user, logout_user, current_user, login_required  # 导入用户认证相关模块
from datetime import datetime, timedelta  # 导入日期时间模块
from app import db  # 导入数据库实例
from app.models import User, RegisterSecret, Config  # 导入数据模型
from app.forms import LoginForm, RegisterForm  # 导入表单类
from app.utils.rate_limit import limiter
import random  # 导入随机数模块
import smtplib
import logging
from email.mime.text import MIMEText
from email.header import Header

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/auth')  # 创建认证路由蓝图


@bp.route('/send-code', methods=['POST'])
@limiter.limit("3 per minute")
def send_code():
    """发送验证码"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'success': False, 'message': '邮箱地址不能为空'}), 400
        
        email = data['email'].strip()
        
        if not email:
            return jsonify({'success': False, 'message': '邮箱地址不能为空'}), 400
        
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            return jsonify({'success': False, 'message': '邮箱格式不正确'}), 400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'success': False, 'message': '该邮箱已被注册'}), 400
        
        code = str(random.randint(100000, 999999))
        
        session['verification_code'] = code
        session['verification_email'] = email
        session['verification_expires_at'] = (datetime.utcnow() + timedelta(minutes=5)).timestamp()
        
        logger.info(f'准备向 {email} 发送验证码')
        
        sender_email = current_app.config.get('MAIL_USERNAME', '')
        sender_password = current_app.config.get('MAIL_PASSWORD', '')
        
        if not sender_email or not sender_password:
            logger.error('邮箱配置缺失')
            return jsonify({'success': False, 'message': '邮箱配置缺失'}), 500
        
        try:
            logger.debug('正在发送邮件...')
            
            message_content = f'Your verification code is: {code}\n\nThis code will expire in 5 minutes, please use it as soon as possible.'
            
            msg = MIMEText(message_content, 'plain', 'utf-8')
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = Header('Verification Code', 'utf-8')
            
            smtp_server = smtplib.SMTP_SSL('smtp.163.com', 465, timeout=10)
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, [email], msg.as_string())
            smtp_server.quit()
            
            logger.info(f'邮件发送成功到 {email}')
        except Exception as e:
            logger.error(f'发送邮件失败: {e}', exc_info=True)
            return jsonify({'success': False, 'message': f'发送邮件失败: {str(e)}'}), 500
        
        logger.info(f'验证码已发送到 {email}')
        
        return jsonify({
            'success': True,
            'message': '验证码已发送，请查收邮件'
        })
        
    except Exception as e:
        logger.error(f'发送验证码错误: {e}', exc_info=True)
        return jsonify({'success': False, 'message': f'发送失败: {str(e)}'}), 500


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # 创建登录表单实例
    
    if form.validate_on_submit():  # 如果表单验证通过
        user = User.query.filter(  # 根据用户名或邮箱查询用户
            (User.username == form.username_or_email.data) | 
            (User.email == form.username_or_email.data)
        ).first()
        
        if user and user.check_password(form.password.data):  # 如果用户存在且密码正确
            # 获取设备ID
            device_id = request.form.get('device_id') or request.json.get('device_id') if request.is_json else request.form.get('device_id')
            
            if not device_id:
                flash('设备ID不能为空', 'danger')
                return render_template('auth/login.html', form=form)
            
            # 设备锁验证
            if user.bound_device_id:
                # 已绑定设备，验证是否一致
                if user.bound_device_id != device_id:
                    flash('该账号已绑定其他设备，请先解绑', 'danger')
                    return render_template('auth/login.html', form=form)
            else:
                # 未绑定设备，绑定当前设备
                user.bound_device_id = device_id
                db.session.commit()
                logger.info(f'用户 {user.username} 绑定设备')
            
            # 保存设备ID到 session
            session['device_id'] = device_id
            
            login_user(user, remember=form.remember.data)  # 登录用户
            next_page = request.args.get('next')  # 获取下一页地址
            
            # 构建响应
            response = redirect(next_page if next_page else url_for('main.index'))
            
            # 如果用户勾选了记住登录状态，将device_id也保存到cookie（30天有效期）
            if form.remember.data:
                response.set_cookie('device_id', device_id, max_age=30*24*60*60, httponly=True, samesite='Lax')
            
            flash('登录成功！', 'success')  # 显示成功消息
            return response
        
        flash('用户名/邮箱或密码错误', 'danger')  # 显示错误消息
    
    return render_template('auth/login.html', form=form)  # 渲染登录页面


@bp.route('/api/login', methods=['POST'])
def api_login():
    """API登录接口（用于移动端/前端API调用）"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求参数错误'}), 400
        
        username_or_email = data.get('username_or_email')
        password = data.get('password')
        device_id = data.get('device_id')
        
        if not username_or_email or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        if not device_id:
            return jsonify({'success': False, 'message': '设备ID不能为空'}), 400
        
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': '用户名/邮箱或密码错误'}), 401
        
        # 设备锁验证
        if user.bound_device_id:
            if user.bound_device_id != device_id:
                return jsonify({'success': False, 'message': '该账号已绑定其他设备，请先解绑'}), 403
        else:
            user.bound_device_id = device_id
            db.session.commit()
            logger.info(f'用户 {user.username} 绑定设备')
        
        # 保存设备ID到 session
        session['device_id'] = device_id
        
        login_user(user)
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
        
    except Exception as e:
        logger.error(f'登录API异常: {e}', exc_info=True)
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500


@bp.route('/api/unbind-device', methods=['POST'])
@login_required
def api_unbind_device():
    """解绑设备API"""
    try:
        current_user.bound_device_id = None
        db.session.commit()
        
        # 清除 session 中的设备ID
        session.pop('device_id', None)
        
        logger.info(f'用户 {current_user.username} 解绑设备')
        
        return jsonify({
            'success': True,
            'message': '设备解绑成功'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'解绑设备失败: {e}', exc_info=True)
        return jsonify({'success': False, 'message': f'解绑失败: {str(e)}'}), 500


@bp.route('/api/request-unbind', methods=['POST'])
def api_request_unbind():
    """申请设备解绑API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '请求参数错误'}), 400
        
        username_or_email = data.get('username_or_email')
        
        if not username_or_email:
            return jsonify({'success': False, 'message': '请提供用户名或邮箱'}), 400
        
        # 查询用户
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 检查是否已经有申请
        if user.device_unbind_status == 1:
            return jsonify({
                'success': False,
                'message': '您的解绑申请已在处理中，请耐心等待管理员审批'
            }), 400
        
        # 检查用户是否绑定了设备
        if not user.bound_device_id:
            return jsonify({
                'success': False,
                'message': '该账号未绑定任何设备，无需申请解绑'
            }), 400
        
        # 提交解绑申请
        from datetime import datetime
        user.device_unbind_status = 1
        user.device_unbind_requested_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f'用户 {user.username} 提交了设备解绑申请')
        
        return jsonify({
            'success': True,
            'message': '解绑申请已提交，请等待管理员审批'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'申请解绑失败: {e}', exc_info=True)
        return jsonify({'success': False, 'message': f'申请失败: {str(e)}'}), 500


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()  # 创建注册表单实例
    
    if form.validate_on_submit():  # 如果表单验证通过
        
        email = form.email.data.strip()
        code = form.code.data.strip()
        
        stored_code = session.get('verification_code')
        stored_email = session.get('verification_email')
        stored_expires_at = session.get('verification_expires_at')
        
        if not stored_code or not stored_email or not stored_expires_at:
            flash('请先获取验证码', 'danger')
            return render_template('auth/register.html', form=form, customer_service_wechat=Config.get_value('customer_service_wechat', 'your_kefu_wechat'))
        
        if stored_email != email:
            flash('邮箱地址不匹配，请重新获取验证码', 'danger')
            return render_template('auth/register.html', form=form, customer_service_wechat=Config.get_value('customer_service_wechat', 'your_kefu_wechat'))
        
        if datetime.utcnow().timestamp() > stored_expires_at:
            flash('验证码已过期，请重新获取', 'danger')
            session.pop('verification_code', None)
            session.pop('verification_email', None)
            session.pop('verification_expires_at', None)
            return render_template('auth/register.html', form=form, customer_service_wechat=Config.get_value('customer_service_wechat', 'your_kefu_wechat'))
        
        if stored_code != code:
            flash('验证码错误，请重试', 'danger')
            return render_template('auth/register.html', form=form, customer_service_wechat=Config.get_value('customer_service_wechat', 'your_kefu_wechat'))
        
        register_secret = RegisterSecret.query.filter_by(secret=form.secret.data).first()  # 查询注册卡密
        
        user = User(  # 创建新用户
            username=form.username.data,
            email=email,
            password=form.password.data
        )
        
        db.session.add(user)  # 添加用户到数据库会话
        db.session.flush()  # 刷新会话获取用户ID
        
        register_secret.is_used = True  # 标记卡密已使用
        register_secret.user_id = user.id  # 关联用户ID
        register_secret.used_at = datetime.utcnow()  # 记录使用时间
        
        # 根据卡密时长类型计算过期时间
        expires_at = None
        if register_secret.duration_type == '1min':
            expires_at = register_secret.used_at + timedelta(minutes=1)
        elif register_secret.duration_type == '1day':
            expires_at = register_secret.used_at + timedelta(days=1)
        elif register_secret.duration_type == '1month':
            expires_at = register_secret.used_at + timedelta(days=30)
        elif register_secret.duration_type == '1year':
            expires_at = register_secret.used_at + timedelta(days=365)
        register_secret.expires_at = expires_at
        
        db.session.commit()  # 提交到数据库
        
        session.pop('verification_code', None)
        session.pop('verification_email', None)
        session.pop('verification_expires_at', None)
        
        flash('注册成功！请登录', 'success')  # 显示成功消息
        return redirect(url_for('auth.login'))  # 重定向到登录页
    
    customer_service_wechat = Config.get_value('customer_service_wechat', 'your_kefu_wechat')
    return render_template('auth/register.html', form=form, customer_service_wechat=customer_service_wechat)  # 渲染注册页面


@bp.route('/logout')
def logout():
    logout_user()  # 退出登录
    flash('已成功退出登录', 'info')  # 显示消息
    # 清除device_id cookie
    response = redirect(url_for('auth.login'))
    response.delete_cookie('device_id')
    return response


@bp.route('/forgot-password', methods=['GET'])
def forgot_password():
    """忘记密码页面"""
    return render_template('auth/forgot_password.html')


@bp.route('/forgot-send-code', methods=['POST'])
@limiter.limit("3 per minute")
def forgot_send_code():
    """忘记密码发送验证码"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'success': False, 'message': '邮箱地址不能为空'}), 400
        
        email = data['email'].strip()
        
        if not email:
            return jsonify({'success': False, 'message': '邮箱地址不能为空'}), 400
        
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            return jsonify({'success': False, 'message': '邮箱格式不正确'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'message': '该邮箱未注册'}), 400
        
        code = str(random.randint(100000, 999999))
        
        session['forgot_verification_code'] = code
        session['forgot_verification_email'] = email
        session['forgot_verification_expires_at'] = (datetime.utcnow() + timedelta(minutes=5)).timestamp()
        
        logger.info(f'准备向 {email} 发送重置密码验证码')
        
        sender_email = current_app.config.get('MAIL_USERNAME', '')
        sender_password = current_app.config.get('MAIL_PASSWORD', '')
        
        if not sender_email or not sender_password:
            logger.error('邮箱配置缺失')
            return jsonify({'success': False, 'message': '邮箱配置缺失'}), 500
        
        try:
            logger.debug('正在发送邮件...')
            
            message_content = f'Your password reset verification code is: {code}\n\nThis code will expire in 5 minutes, please use it as soon as possible.'
            
            msg = MIMEText(message_content, 'plain', 'utf-8')
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = Header('Password Reset Code', 'utf-8')
            
            smtp_server = smtplib.SMTP_SSL('smtp.163.com', 465, timeout=10)
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, [email], msg.as_string())
            smtp_server.quit()
            
            logger.info(f'重置密码邮件发送成功到 {email}')
        except Exception as e:
            logger.error(f'发送邮件失败: {e}', exc_info=True)
            return jsonify({'success': False, 'message': f'发送邮件失败: {str(e)}'}), 500
        
        logger.info(f'重置密码验证码已发送到 {email}')
        
        return jsonify({
            'success': True,
            'message': '验证码已发送，请查收邮件'
        })
        
    except Exception as e:
        logger.error(f'发送重置密码验证码错误: {e}', exc_info=True)
        return jsonify({'success': False, 'message': f'发送失败: {str(e)}'}), 500


@bp.route('/forgot-reset', methods=['POST'])
def forgot_reset():
    """重置密码"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'code' not in data:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        email = data['email'].strip()
        code = data['code'].strip()
        
        stored_code = session.get('forgot_verification_code')
        stored_email = session.get('forgot_verification_email')
        stored_expires_at = session.get('forgot_verification_expires_at')
        
        if not stored_code or not stored_email or not stored_expires_at:
            return jsonify({'success': False, 'message': '请先获取验证码'}), 400
        
        if stored_email != email:
            return jsonify({'success': False, 'message': '邮箱地址不匹配'}), 400
        
        if datetime.utcnow().timestamp() > stored_expires_at:
            session.pop('forgot_verification_code', None)
            session.pop('forgot_verification_email', None)
            session.pop('forgot_verification_expires_at', None)
            return jsonify({'success': False, 'message': '验证码已过期'}), 400
        
        if stored_code != code:
            return jsonify({'success': False, 'message': '验证码错误'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 400
        
        user.password = 'aa123456'
        db.session.commit()
        
        session.pop('forgot_verification_code', None)
        session.pop('forgot_verification_email', None)
        session.pop('forgot_verification_expires_at', None)
        
        logout_user()
        
        logger.info(f'用户 {user.username} 密码重置成功')
        
        return jsonify({
            'success': True,
            'message': '密码重置成功'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'重置密码错误: {e}', exc_info=True)
        return jsonify({'success': False, 'message': f'重置失败: {str(e)}'}), 500


@bp.route('/save-device-id', methods=['POST'])
def save_device_id():
    """保存设备ID到session"""
    try:
        data = request.get_json()
        
        if not data or 'device_id' not in data:
            return jsonify({'success': False, 'message': '缺少设备ID'}), 400
        
        device_id = data['device_id'].strip()
        
        if device_id:
            session['device_id'] = device_id
        
        return jsonify({'success': True, 'message': '设备ID保存成功'})
        
    except Exception as e:
        logger.error(f'保存设备ID失败: {e}', exc_info=True)
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'}), 500
