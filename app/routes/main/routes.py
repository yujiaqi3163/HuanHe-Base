from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app  # 导入Flask相关模块
from flask_login import login_required, current_user  # 导入登录相关模块
from app.models import User, RegisterSecret, Material  # 导入数据模型
from app import db  # 导入数据库
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)  # 创建主路由蓝图


def save_image(file):
    """保存图片到本地并返回相对路径"""
    if not file:
        return None
    
    # 生成安全的文件名
    filename = secure_filename(file.filename)
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


@bp.route('/')
@login_required
def index():
    users = User.query.all()  # 查询所有用户
    register_secrets = RegisterSecret.query.all()  # 查询所有注册卡密
    
    # 查询热度最高的前5个素材（按浏览量排序）
    hot_materials = Material.query.order_by(Material.view_count.desc()).limit(5).all()
    
    # 查询最新入库的素材（按创建时间降序排序）
    latest_materials = Material.query.order_by(Material.created_at.desc()).limit(8).all()
    
    # 获取素材总数
    total_count = Material.query.count()
    
    return render_template('main/index.html', users=users, register_secrets=register_secrets, hot_materials=hot_materials, latest_materials=latest_materials, total_count=total_count)  # 渲染首页模板


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
    
    # 查询素材
    query = Material.query
    
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


@bp.route('/material/<int:material_id>')
@login_required
def material_detail(material_id):
    """素材详情页面"""
    material = Material.query.get_or_404(material_id)
    
    # 增加浏览量
    material.view_count += 1
    db.session.commit()
    
    return render_template('main/material_detail.html', material=material)
