from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app  # 导入Flask相关模块
from flask_login import login_required, current_user  # 导入登录相关模块
from app.models import User, RegisterSecret, Material, UserMaterial, UserMaterialImage  # 导入数据模型
from app import db  # 导入数据库
from app.decorators import device_required  # 导入设备锁装饰器
from app.utils.logger import get_logger  # 导入日志模块
from sqlalchemy.orm import joinedload  # 导入joinedload用于预加载关联数据
import os
import random
import base64
import re
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from io import BytesIO

logger = get_logger(__name__)

bp = Blueprint('main', __name__)  # 创建主路由蓝图


def save_image(file):
    """保存图片到本地并返回相对路径"""
    if not file:
        return None
    
    # 验证文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if file_ext not in allowed_extensions:
        logger.error(f'不支持的文件格式: {file_ext}')
        return None
    
    # 检查文件大小（限制10MB）
    file.stream.seek(0, 2)
    file_size = file.stream.tell()
    file.stream.seek(0)
    
    if file_size > 10 * 1024 * 1024:
        logger.error(f'文件大小超过10MB限制: {file_size / (1024 * 1024):.2f}MB')
        return None
    
    # 添加时间戳避免重名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
    filename = timestamp + filename
    
    # 构建保存路径
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # 保存文件
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # 返回相对路径（用于数据库存储）
    return f'/static/uploads/{filename}'


def save_base64_image(base64_data):
    """保存Base64编码的图片到本地并返回相对路径"""
    if not base64_data:
        return None
    
    # 验证数据格式
    if not base64_data.startswith('data:image/'):
        logger.error('无效的图片数据格式')
        return None
    
    # 提取图片格式和数据
    try:
        header, data = base64_data.split(',', 1)
        file_ext = header.split(';')[0].split('/')[1].lower()
    except (IndexError, ValueError) as e:
        logger.error(f'解析Base64数据失败: {e}')
        return None
    
    # 验证文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if file_ext not in allowed_extensions:
        logger.error(f'不支持的图片格式: {file_ext}')
        return None
    
    try:
        # 解码Base64
        image_data = base64.b64decode(data)
        
        # 检查文件大小（限制10MB）
        if len(image_data) > 10 * 1024 * 1024:
            logger.error(f'图片大小超过10MB限制: {len(image_data) / (1024 * 1024):.2f}MB')
            return None
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_str = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        filename = f'{timestamp}_{random_str}.{file_ext}'
        
        # 构建保存路径
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # 保存文件
        file_path = os.path.join(upload_folder, filename)
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        # 返回相对路径
        return f'/static/uploads/{filename}'
        
    except Exception as e:
        logger.error(f'保存Base64图片失败: {e}', exc_info=True)
        return None


@bp.route('/api/test', methods=['GET', 'POST'])
def api_test():
    """测试API路由"""
    return jsonify({'success': True, 'message': 'API正常工作'})


@bp.route('/')
@login_required
def index():
    from datetime import datetime
    from app.models import Config
    
    users = User.query.all()  # 查询所有用户
    register_secrets = RegisterSecret.query.all()  # 查询所有注册卡密
    
    # 查询热度最高的前5个素材（按浏览量排序，只显示已上架）
    hot_materials = Material.query.filter_by(is_published=True).order_by(Material.view_count.desc()).limit(5).all()
    
    # 查询最新入库的素材（按创建时间降序排序，只显示已上架）
    latest_materials = Material.query.filter_by(is_published=True).order_by(Material.created_at.desc()).limit(8).all()
    
    # 获取素材总数（只统计已上架素材）
    total_count = Material.query.filter_by(is_published=True).count()
    
    # 验证用户卡密有效性
    is_membership_valid = False
    now = datetime.utcnow()
    
    try:
        # 获取用户卡密
        secrets_list = list(current_user.register_secrets)
        if not secrets_list:
            secrets_list = RegisterSecret.query.filter_by(user_id=current_user.id).all()
        
        if secrets_list and len(secrets_list) > 0:
            # 找到最新的一个
            user_secret = sorted(secrets_list, key=lambda s: s.used_at or s.created_at, reverse=True)[0]
            if user_secret.is_used:
                if user_secret.duration_type == 'permanent':
                    is_membership_valid = True
                elif user_secret.expires_at and now <= user_secret.expires_at:
                    is_membership_valid = True
    except:
        pass
    
    # 获取客服微信
    customer_service_wechat = Config.get_value('customer_service_wechat', 'your_kefu_wechat')
    
    return render_template('main/index.html', 
                           users=users, 
                           register_secrets=register_secrets, 
                           hot_materials=hot_materials, 
                           latest_materials=latest_materials, 
                           total_count=total_count,
                           is_membership_valid=is_membership_valid,
                           customer_service_wechat=customer_service_wechat)  # 渲染首页模板


@bp.route('/profile')
@login_required
def profile():
    from datetime import datetime
    now = datetime.utcnow()
    
    # 简单的卡密获取，先确保页面能打开
    user_secret = None
    secrets_list = None
    
    try:
        # 先尝试从关系获取
        secrets_list = list(current_user.register_secrets)
    except:
        pass
    
    # 如果关系获取失败，直接查询
    if not secrets_list:
        from app.models import RegisterSecret
        try:
            secrets_list = RegisterSecret.query.filter_by(user_id=current_user.id).all()
        except:
            secrets_list = []
    
    # 找到最新的一个
    if secrets_list and len(secrets_list) > 0:
        user_secret = secrets_list[0]
        # 尝试排序
        try:
            user_secret = sorted(secrets_list, key=lambda s: s.used_at or s.created_at, reverse=True)[0]
        except:
            pass
    
    # 判断会员状态 - 如果没有找到卡密，或者卡密被释放，都显示为已失效
    membership_status = '已失效'
    status_text = '已失效，请联系管理购买'
    status_color = 'text-red-500'
    status_badge = 'bg-red-50'
    is_expired = True
    
    if user_secret:
        try:
            if user_secret.is_used:
                if user_secret.duration_type == 'permanent':
                    membership_status = '永久会员'
                    status_text = '♾️ 永久会员'
                    status_color = 'text-yellow-600'
                    status_badge = 'bg-yellow-50'
                    is_expired = False
                elif user_secret.expires_at:
                    if now > user_secret.expires_at:
                        membership_status = '已失效'
                        status_text = '已失效，请联系管理购买'
                        status_color = 'text-red-500'
                        status_badge = 'bg-red-50'
                        is_expired = True
                    else:
                        membership_status = '会员有效期内'
                        status_text = f'至 {user_secret.expires_at.strftime("%Y-%m-%d")}'
                        status_color = 'text-green-500'
                        status_badge = 'bg-green-50'
                        is_expired = False
        except:
            pass
    
    return render_template('main/profile.html', 
                           user_secret=user_secret, 
                           membership_status=membership_status,
                           status_text=status_text,
                           status_color=status_color,
                           status_badge=status_badge,
                           is_expired=is_expired)  # 渲染个人中心模板


@bp.route('/security-center')
@login_required
def security_center():
    """安全中心页面"""
    return render_template('main/security_center.html')


@bp.route('/security-secret')
@login_required
def security_secret():
    """卡密信息页面"""
    from datetime import datetime
    now = datetime.utcnow()
    
    # 获取用户卡密信息
    user_secret = None
    secrets_list = None
    
    try:
        secrets_list = list(current_user.register_secrets)
    except:
        pass
    
    if not secrets_list:
        from app.models import RegisterSecret
        try:
            secrets_list = RegisterSecret.query.filter_by(user_id=current_user.id).all()
        except:
            secrets_list = []
    
    if secrets_list and len(secrets_list) > 0:
        user_secret = secrets_list[0]
        try:
            user_secret = sorted(secrets_list, key=lambda s: s.used_at or s.created_at, reverse=True)[0]
        except:
            pass
    
    is_expired = True
    if user_secret:
        try:
            if user_secret.is_used:
                if user_secret.duration_type == 'permanent':
                    is_expired = False
                elif user_secret.expires_at and now <= user_secret.expires_at:
                    is_expired = False
        except:
            pass
    
    return render_template('main/security_secret.html', 
                           user_secret=user_secret, 
                           is_expired=is_expired)


@bp.route('/terminal-secret')
@login_required
def terminal_secret():
    """终端卡密信息页面"""
    from datetime import datetime
    now = datetime.utcnow()
    
    # 获取用户终端卡密信息
    user_secret = None
    secrets_list = None
    
    try:
        secrets_list = list(current_user.terminal_secrets)
    except:
        pass
    
    if not secrets_list:
        from app.models import TerminalSecret
        try:
            secrets_list = TerminalSecret.query.filter_by(user_id=current_user.id).all()
        except:
            secrets_list = []
    
    if secrets_list and len(secrets_list) > 0:
        user_secret = secrets_list[0]
        try:
            user_secret = sorted(secrets_list, key=lambda s: s.used_at or s.created_at, reverse=True)[0]
        except:
            pass
    
    is_expired = True
    if user_secret:
        try:
            if user_secret.is_used:
                if user_secret.duration_type == 'permanent':
                    is_expired = False
                elif user_secret.expires_at and now <= user_secret.expires_at:
                    is_expired = False
        except:
            pass
    
    return render_template('main/terminal_secret.html', 
                           user_secret=user_secret, 
                           is_expired=is_expired)


@bp.route('/api/renew-terminal-secret', methods=['POST'])
@login_required
def api_renew_terminal_secret():
    """续费终端卡密API"""
    from datetime import datetime, timedelta
    from app.models import TerminalSecret
    
    data = request.get_json()
    
    if not data or 'new_secret' not in data:
        return jsonify({'success': False, 'message': '请输入新卡密'}), 400
    
    new_secret_str = data['new_secret'].strip()
    if not new_secret_str:
        return jsonify({'success': False, 'message': '请输入新卡密'}), 400
    
    # 查询新卡密
    new_secret = TerminalSecret.query.filter_by(secret=new_secret_str).first()
    if not new_secret:
        return jsonify({'success': False, 'message': '卡密不存在'}), 400
    
    if new_secret.is_used:
        return jsonify({'success': False, 'message': '该卡密已被使用'}), 400
    
    # 释放用户的旧卡密（已过期的）
    now = datetime.utcnow()
    
    # 查询用户当前的所有终端卡密
    old_secrets = TerminalSecret.query.filter_by(user_id=current_user.id).all()
    
    for old_secret in old_secrets:
        # 只有已过期的卡密才释放
        if old_secret.is_used and old_secret.expires_at and now > old_secret.expires_at:
            # 解除与用户的关联，但保留历史记录
            old_secret.user_id = None
            # 注意：不重置 is_used，保留使用记录用于追踪
    
    # 标记新卡密为已使用
    new_secret.is_used = True
    new_secret.user_id = current_user.id
    new_secret.used_at = datetime.utcnow()
    
    # 根据新卡密时长计算过期时间
    expires_at = None
    if new_secret.duration_type == '1min':
        expires_at = new_secret.used_at + timedelta(minutes=1)
    elif new_secret.duration_type == '1day':
        expires_at = new_secret.used_at + timedelta(days=1)
    elif new_secret.duration_type == '1month':
        expires_at = new_secret.used_at + timedelta(days=30)
    elif new_secret.duration_type == '1year':
        expires_at = new_secret.used_at + timedelta(days=365)
    new_secret.expires_at = expires_at
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '续费成功',
        'data': {
            'secret': new_secret_str,
            'duration_type': new_secret.duration_type,
            'expires_at': expires_at.strftime('%Y-%m-%d %H:%M') if expires_at else None
        }
    })


@bp.route('/security-device')
@login_required
def security_device():
    """设备绑定页面"""
    return render_template('main/security_device.html')


@bp.route('/security-password')
@login_required
def security_password():
    """修改密码页面"""
    return render_template('main/security_password.html')


@bp.route('/text-encrypt')
@login_required
def text_encrypt():
    """文本加密终端页面"""
    from datetime import datetime
    from app.models import TerminalSecret
    
    now = datetime.utcnow()
    
    # 检查用户是否有有效的终端卡密
    has_valid_secret = False
    secrets_list = None
    
    try:
        secrets_list = list(current_user.terminal_secrets)
    except:
        pass
    
    if not secrets_list:
        secrets_list = TerminalSecret.query.filter_by(user_id=current_user.id).all()
    
    if secrets_list and len(secrets_list) > 0:
        user_secret = sorted(secrets_list, key=lambda s: s.used_at or s.created_at, reverse=True)[0]
        if user_secret.is_used:
            if user_secret.duration_type == 'permanent':
                has_valid_secret = True
            elif user_secret.expires_at and now <= user_secret.expires_at:
                has_valid_secret = True
    
    if not has_valid_secret:
        flash('请先在我的-安全中心-终端卡密激活终端卡密', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('main/text_encrypt.html')


def validate_password_strength(password):
    """验证密码强度"""
    # 检查密码长度
    if len(password) < 8:
        return '密码长度至少为8位'
    
    # 检查是否包含大写字母
    if not re.search(r'[A-Z]', password):
        return '密码必须包含至少一个大写字母'
    
    # 检查是否包含小写字母
    if not re.search(r'[a-z]', password):
        return '密码必须包含至少一个小写字母'
    
    # 检查是否包含数字
    if not re.search(r'[0-9]', password):
        return '密码必须包含至少一个数字'
    
    # 检查是否包含特殊字符
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return '密码必须包含至少一个特殊字符(!@#$%^&*(),.?":{}|<>)'
    
    return None


@bp.route('/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    """修改密码API"""
    try:
        data = request.get_json()
        
        if not data or 'old_password' not in data or 'new_password' not in data:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        old_password = data['old_password'].strip()
        new_password = data['new_password'].strip()
        
        if not old_password:
            return jsonify({'success': False, 'message': '请输入原密码'}), 400
        
        if not new_password:
            return jsonify({'success': False, 'message': '请输入新密码'}), 400
        
        # 验证密码强度
        strength_error = validate_password_strength(new_password)
        if strength_error:
            return jsonify({'success': False, 'message': strength_error}), 400
        
        if old_password == new_password:
            return jsonify({'success': False, 'message': '新密码不能与原密码相同'}), 400
        
        if not current_user.check_password(old_password):
            return jsonify({'success': False, 'message': '原密码错误'}), 400
        
        current_user.password = new_password
        db.session.commit()
        
        logger.info(f'用户 {current_user.username} 修改密码成功')
        
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'修改密码失败: {e}', exc_info=True)
        return jsonify({'success': False, 'message': f'修改失败: {str(e)}'}), 500


@bp.route('/api/renew-secret', methods=['POST'])
@login_required
def api_renew_secret():
    """续费卡密API"""
    data = request.get_json()
    
    if not data or 'new_secret' not in data:
        return jsonify({'success': False, 'message': '请输入新卡密'}), 400
    
    new_secret_str = data['new_secret'].strip()
    if not new_secret_str:
        return jsonify({'success': False, 'message': '请输入新卡密'}), 400
    
    # 查询新卡密
    new_secret = RegisterSecret.query.filter_by(secret=new_secret_str).first()
    if not new_secret:
        return jsonify({'success': False, 'message': '卡密不存在'}), 400
    
    if new_secret.is_used:
        return jsonify({'success': False, 'message': '该卡密已被使用'}), 400
    
    # 释放用户的旧卡密（已过期的）
    from datetime import datetime
    now = datetime.utcnow()
    
    # 查询用户当前的所有卡密
    old_secrets = RegisterSecret.query.filter_by(user_id=current_user.id).all()
    
    for old_secret in old_secrets:
        # 只有已过期的卡密才释放
        if old_secret.is_used and old_secret.expires_at and now > old_secret.expires_at:
            # 解除与用户的关联，但保留历史记录
            old_secret.user_id = None
            # 注意：不重置 is_used，保留使用记录用于追踪
    
    # 标记新卡密为已使用
    new_secret.is_used = True
    new_secret.user_id = current_user.id
    new_secret.used_at = datetime.utcnow()
    
    # 根据新卡密时长计算过期时间
    expires_at = None
    if new_secret.duration_type == '1min':
        expires_at = new_secret.used_at + timedelta(minutes=1)
    elif new_secret.duration_type == '1day':
        expires_at = new_secret.used_at + timedelta(days=1)
    elif new_secret.duration_type == '1month':
        expires_at = new_secret.used_at + timedelta(days=30)
    elif new_secret.duration_type == '1year':
        expires_at = new_secret.used_at + timedelta(days=365)
    new_secret.expires_at = expires_at
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '续费成功',
        'data': {
            'secret': new_secret_str,
            'duration_type': new_secret.duration_type,
            'expires_at': expires_at.strftime('%Y-%m-%d %H:%M') if expires_at else None
        }
    })


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    if request.method == 'POST':
        # 获取表单数据
        username = request.form.get('username', '').strip()
        bio = request.form.get('bio', '').strip()
        gender = request.form.get('gender', '').strip() or None
        birthday_str = request.form.get('birthday', '').strip()
        
        # 处理出生日期
        birthday = None
        if birthday_str:
            try:
                from datetime import datetime
                birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
            except:
                pass
        
        # 检查用户名是否已被其他用户使用
        if username and username != current_user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('用户名已被使用', 'danger')
                return redirect(url_for('main.profile_edit'))
        
        # 更新用户信息
        if username:
            current_user.username = username
        current_user.bio = bio
        current_user.gender = gender
        current_user.birthday = birthday
        
        # 处理头像上传
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename:
            avatar_url = save_image(avatar_file)
            if avatar_url:
                current_user.avatar = avatar_url
        
        # 保存到数据库
        db.session.commit()
        
        flash('个人资料更新成功', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('main/profile_edit.html')  # 渲染个人资料编辑模板


@bp.route('/api/latest-materials')
@login_required
def api_get_latest_materials():
    """分页获取最新入库素材API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 8, type=int)
    sort_by = request.args.get('sort', 'created_at')
    search_keyword = request.args.get('search', '').strip()
    
    # 计算偏移量
    offset = (page - 1) * per_page
    
    # 查询素材 - 使用joinedload预加载关联数据，避免N+1查询，只显示已上架
    query = Material.query.options(
        joinedload(Material.images),
        joinedload(Material.material_type)
    ).filter_by(is_published=True)
    
    # 添加搜索条件（按标题搜索）
    if search_keyword:
        query = query.filter(Material.title.contains(search_keyword))
    
    # 根据排序参数排序
    if sort_by == 'view':
        materials = query.order_by(Material.view_count.desc()).offset(offset).limit(per_page).all()
    elif sort_by == 'favorite':
        materials = query.order_by(Material.favorite_count.desc()).offset(offset).limit(per_page).all()
    elif sort_by == 'download':
        materials = query.order_by(Material.download_count.desc()).offset(offset).limit(per_page).all()
    else:
        materials = query.order_by(Material.created_at.desc()).offset(offset).limit(per_page).all()
    
    total_count = query.count()
    
    # 构建返回数据
    material_list = []
    for material in materials:
        # 获取封面图
        cover_image = next((img for img in material.images if img.is_cover), None)
        
        material_list.append({
            'id': material.id,
            'title': material.title,
            'material_type': material.material_type.name if material.material_type else '未分类',
            'view_count': material.view_count,
            'favorite_count': material.favorite_count,
            'download_count': material.download_count,
            'cover_image_url': cover_image.image_url if cover_image else None
        })
    
    return jsonify({
        'success': True,
        'data': material_list,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total_count,
            'has_more': (page * per_page) < total_count
        }
    })


@bp.route('/my-materials')
@login_required
def my_materials():
    """我的作品库页面"""
    # 查询用户的二创素材，按创建时间倒序
    user_materials = UserMaterial.query.filter_by(
        user_id=current_user.id
    ).order_by(UserMaterial.created_at.desc()).all()
    
    return render_template('main/my_materials.html', user_materials=user_materials)


@bp.route('/my-material/<int:user_material_id>')
@login_required
def my_material_detail(user_material_id):
    """我的素材详情页"""
    from sqlalchemy.orm import joinedload
    
    user_material = UserMaterial.query.options(
        joinedload(UserMaterial.images)
    ).filter_by(
        id=user_material_id,
        user_id=current_user.id
    ).first_or_404()
    
    logger.debug(f'用户素材详情页 - 素材ID: {user_material_id}, 标题: {user_material.title}, 图片数量: {len(user_material.images)}')
    
    # 增加浏览量
    user_material.view_count += 1
    db.session.commit()
    
    return render_template('main/my_material_detail.html', user_material=user_material)


@bp.route('/api/user-material/<int:user_material_id>/download', methods=['POST'])
@login_required
@device_required
def api_download_user_material(user_material_id):
    """下载用户素材API - 增加下载计数"""
    user_material = UserMaterial.query.filter_by(
        id=user_material_id,
        user_id=current_user.id
    ).first_or_404()
    
    # 增加下载计数
    user_material.download_count += 1
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '下载计数更新成功',
        'data': {
            'download_count': user_material.download_count
        }
    })


@bp.route('/api/user-material/<int:user_material_id>/delete', methods=['POST'])
@login_required
def api_delete_user_material(user_material_id):
    """删除用户素材API"""
    try:
        from app.models import UserMaterial
        
        user_material = UserMaterial.query.filter_by(
            id=user_material_id,
            user_id=current_user.id
        ).first_or_404()
        
        logger.info(f'删除用户素材，素材ID: {user_material_id}，标题: {user_material.title}')
        
        # 删除素材（级联删除会自动删除关联的图片）
        db.session.delete(user_material)
        db.session.commit()
        
        logger.info(f'用户素材删除成功，素材ID: {user_material_id}')
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'删除用户素材失败: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 500


@bp.route('/api/upload-image', methods=['POST'])
@login_required
@device_required
def api_upload_image():
    """上传处理后的图片API"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'success': False, 'message': '缺少图片数据'}), 400
        
        logger.debug('开始上传处理后的图片')
        
        # 保存Base64图片
        image_url = save_base64_image(data['image'])
        
        if not image_url:
            return jsonify({'success': False, 'message': '图片保存失败'}), 500
        
        logger.info(f'图片保存成功: {image_url}')
        
        return jsonify({
            'success': True,
            'message': '上传成功',
            'data': {
                'image_url': image_url
            }
        })
        
    except Exception as e:
        logger.error(f'上传图片失败: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': f'上传失败: {str(e)}'
        }), 500


@bp.route('/material/<int:material_id>')
@login_required
def material_detail(material_id):
    """素材详情页面"""
    from datetime import datetime
    from app.models import Config
    
    material = Material.query.filter_by(id=material_id, is_published=True).first_or_404()
    
    # 验证用户卡密有效性
    is_membership_valid = False
    now = datetime.utcnow()
    
    try:
        # 获取用户卡密
        secrets_list = list(current_user.register_secrets)
        if not secrets_list:
            secrets_list = RegisterSecret.query.filter_by(user_id=current_user.id).all()
        
        if secrets_list and len(secrets_list) > 0:
            # 找到最新的一个
            user_secret = sorted(secrets_list, key=lambda s: s.used_at or s.created_at, reverse=True)[0]
            if user_secret.is_used:
                if user_secret.duration_type == 'permanent':
                    is_membership_valid = True
                elif user_secret.expires_at and now <= user_secret.expires_at:
                    is_membership_valid = True
    except:
        pass
    
    # 获取客服微信
    customer_service_wechat = Config.get_value('customer_service_wechat', 'your_kefu_wechat')
    
    # 增加浏览量
    material.view_count += 1
    db.session.commit()
    
    return render_template('main/material_detail.html', 
                           material=material,
                           is_membership_valid=is_membership_valid,
                           customer_service_wechat=customer_service_wechat)


@bp.route('/api/material/<int:material_id>/remix', methods=['POST'])
@login_required
@device_required
def api_remix_material(material_id):
    """素材二创API"""
    logger.info(f'开始处理素材二创请求，素材ID: {material_id}')
    
    try:
        from app.models import Material, UserMaterial, UserMaterialImage
        from app.utils.material_remix import optimize_copywriting, get_unique_css_recipes
        import json
        
        # 获取原始素材（只允许二创已上架的素材）
        original_material = Material.query.filter_by(id=material_id, is_published=True).first_or_404()
        logger.debug(f'找到原始素材: {original_material.title}')
        
        # 1. 文案二创（使用DeepSeek）
        original_description = original_material.description or ''
        logger.debug(f'原文案长度: {len(original_description)}')
        remix_description = optimize_copywriting(original_description)
        logger.debug(f'二创文案长度: {len(remix_description)}')
        
        # 2. 创建用户二创素材
        user_material = UserMaterial(
            user_id=current_user.id,
            original_material_id=material_id,
            title=original_material.title,
            description=remix_description,
            original_description=original_description
        )
        
        db.session.add(user_material)
        db.session.flush()
        logger.info(f'创建用户素材成功，ID: {user_material.id}')
        
        # 3. 处理图片 - 确保每张图片使用不同的CSS配方
        images_data = []
        # 先获取所有不重复的CSS配方
        recipes = get_unique_css_recipes(len(original_material.images))
        
        for idx, img in enumerate(original_material.images):
            # 使用不重复的CSS配方
            recipe = recipes[idx]
            
            # 创建二创图片记录
            remix_img = UserMaterialImage(
                user_material_id=user_material.id,
                original_image_url=img.image_url,
                image_url=img.image_url,
                sort_order=idx,
                is_cover=img.is_cover,
                css_recipe=json.dumps(recipe, ensure_ascii=False)
            )
            db.session.add(remix_img)
            images_data.append({
                'original_url': img.image_url,
                'css_recipe': recipe
            })
        
        logger.debug(f'图片处理完成，使用了 {len(recipes)} 个不重复的CSS配方')
        
        # 4. 提交数据库
        db.session.commit()
        logger.debug('数据库提交成功')
        
        # 5. 返回结果
        result = {
            'success': True,
            'message': '素材二创成功',
            'data': {
                'user_material_id': user_material.id,
                'title': user_material.title,
                'description': user_material.description,
                'original_description': user_material.original_description,
                'images': images_data
            }
        }
        logger.debug(f'返回结果: {result}')
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'素材二创异常: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': f'素材二创失败: {str(e)}'
        }), 500


@bp.route('/api/user-material/<int:user_material_id>/update-image', methods=['POST'])
@login_required
def api_update_user_material_image(user_material_id):
    """更新用户二创素材图片（保存处理后的图片）"""
    from app.models import UserMaterial, UserMaterialImage
    from werkzeug.utils import secure_filename
    import base64
    from io import BytesIO
    
    user_material = UserMaterial.query.filter_by(
        id=user_material_id,
        user_id=current_user.id
    ).first_or_404()
    
    try:
        data = request.get_json()
        
        if not data or 'images' not in data:
            return jsonify({'success': False, 'message': '参数错误'}), 400
        
        # 更新图片
        for idx, img_data in enumerate(data['images']):
            remix_img = UserMaterialImage.query.filter_by(
                user_material_id=user_material_id,
                sort_order=idx
            ).first()
            
            if remix_img and 'image_url' in img_data:
                remix_img.image_url = img_data['image_url']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '图片更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500
