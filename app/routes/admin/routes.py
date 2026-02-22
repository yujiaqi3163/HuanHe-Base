# 导入Flask相关模块
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request, jsonify
# 导入登录相关模块
from flask_login import login_required, current_user
# 导入装饰器
from app.decorators import admin_required, permission_required
# 导入数据库模块
from app import db
# 导入表单
from app.forms import MaterialForm
from app.forms.material_type import MaterialTypeForm
# 导入模型
from app.models import Material, MaterialType, MaterialImage, RegisterSecret, User, Config, UserMaterial, UserMaterialImage, Permission, UserPermission, TerminalSecret
# 导入日志模块
from app.utils.logger import get_logger
# 导入文件处理模块
import os
import re
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy.orm import joinedload  # 导入joinedload用于预加载关联数据

logger = get_logger(__name__)

# 文件上传安全配置
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    # 图片格式
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp',
    # 视频格式
    'mp4', 'webm', 'mov', 'avi', 'mkv'
}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}


def allowed_file(filename, allowed_extensions=None):
    """检查文件扩展名是否在白名单中"""
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_file(file, allowed_extensions=None):
    """
    验证文件
    
    Args:
        file: 文件对象
        allowed_extensions: 允许的扩展名集合
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file:
        return False, '文件不能为空'
    
    if not file.filename:
        return False, '文件名不能为空'
    
    # 检查扩展名
    if not allowed_file(file.filename, allowed_extensions):
        return False, f'不支持的文件格式: {file.filename}'
    
    # 检查文件大小 (先seek到末尾获取大小，再seek回0)
    file.seek(0, 2)  # 移动到文件末尾
    size = file.tell()
    file.seek(0)  # 移动回文件开头
    
    if size > MAX_FILE_SIZE:
        return False, f'文件大小超过限制 (最大 {MAX_FILE_SIZE // (1024 * 1024)}MB): {file.filename}'
    
    return True, None


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


# 创建管理后台路由蓝图
bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@login_required
@admin_required
def index():
    """管理后台首页"""
    # 统计数据
    total_materials = Material.query.count()
    unused_secrets = RegisterSecret.query.filter_by(is_used=False).count()
    total_users = User.query.count()
    
    # 最新更新的素材（前3个，按updated_at倒序）
    latest_materials = Material.query.order_by(Material.updated_at.desc()).limit(3).all()
    
    # 最新生成的卡密（前3个，按created_at倒序）
    latest_secrets = RegisterSecret.query.order_by(RegisterSecret.created_at.desc()).limit(3).all()
    
    # 获取客服微信
    customer_service_wechat = Config.get_value('customer_service_wechat', 'your_kefu_wechat')
    
    return render_template('admin/admin_index.html', 
                          total_materials=total_materials,
                          unused_secrets=unused_secrets,
                          total_users=total_users,
                          latest_materials=latest_materials,
                          latest_secrets=latest_secrets,
                          customer_service_wechat=customer_service_wechat)


@bp.route('/config/wechat', methods=['POST'])
@login_required
@admin_required
@permission_required('config_manage')
def update_wechat():
    """更新客服微信API"""
    try:
        data = request.get_json()
        wechat = data.get('wechat', '').strip()
        
        if not wechat:
            return jsonify({'success': False, 'message': '微信号不能为空'})
        
        Config.set_value('customer_service_wechat', wechat, '客服微信号')
        
        return jsonify({'success': True, 'message': '保存成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@bp.route('/materials')
@login_required
@admin_required
@permission_required('material_manage')
def materials():
    """素材库管理页面"""
    material_types = MaterialType.query.order_by(MaterialType.created_at.desc()).all()
    # 第一次只加载10个素材
    materials = Material.query.order_by(Material.created_at.desc()).limit(10).all()
    total_count = Material.query.count()
    return render_template('admin/admin_materials.html', material_types=material_types, materials=materials, total_count=total_count)


@bp.route('/api/materials')
@login_required
@admin_required
@permission_required('material_manage')
def api_get_materials():
    """分页获取素材API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取分类ID，处理空字符串的情况
    material_type_id_str = request.args.get('material_type_id', '')
    material_type_id = None
    if material_type_id_str and material_type_id_str.strip() != '':
        try:
            material_type_id = int(material_type_id_str)
        except (ValueError, TypeError):
            material_type_id = None
    
    # 获取搜索关键词
    search_keyword = request.args.get('search', '').strip()
    
    # 计算偏移量
    offset = (page - 1) * per_page
    
    # 查询素材 - 使用joinedload预加载关联数据，避免N+1查询
    query = Material.query.options(
        joinedload(Material.images),
        joinedload(Material.material_type)
    )
    if material_type_id is not None:
        query = query.filter_by(material_type_id=material_type_id)
    
    # 添加搜索条件（按标题搜索）
    if search_keyword:
        query = query.filter(Material.title.contains(search_keyword))
    
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
            'description': material.description,
            'material_type': material.material_type.name if material.material_type else '未分类',
            'view_count': material.view_count,
            'favorite_count': material.favorite_count,
            'download_count': material.download_count,
            'is_published': material.is_published,
            'cover_image_url': cover_image.image_url if cover_image else None,
            'created_at': material.created_at.strftime('%Y-%m-%d %H:%M:%S') if material.created_at else None
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


@bp.route('/materials/add', methods=['GET', 'POST'])
@login_required
@admin_required
@permission_required('material_manage')
def material_add():
    # 创建表单实例
    form = MaterialForm()
    
    # 填充素材类型选择框
    material_types = MaterialType.query.all()
    form.material_type_id.choices = [(t.id, t.name) for t in material_types]
    
    # 如果是POST请求
    if form.validate_on_submit():
        # 获取封面图
        cover_image = None
        if 'cover_image' in request.files:
            cover_file = request.files['cover_image']
            if cover_file and cover_file.filename:
                cover_image = save_image(cover_file)
        
        # 获取其他图片
        other_images = []
        if 'other_images' in request.files:
            other_files = request.files.getlist('other_images')
            for file in other_files:
                if file and file.filename:
                    saved_path = save_image(file)
                    if saved_path:
                        other_images.append(saved_path)
        
        # 检查封面图是否上传（必填）
        if not cover_image:
            flash('请上传封面图！', 'error')
            return render_template('admin/admin_material_add.html', form=form)
        
        # 创建新素材
        material = Material(
            title=form.title.data,
            description=form.description.data,
            material_type_id=form.material_type_id.data,
            is_published=form.is_published.data
        )
        
        # 保存素材到数据库
        db.session.add(material)
        db.session.flush()  # 获取素材ID
        
        # 保存封面图
        if cover_image:
            cover_img = MaterialImage(
                material_id=material.id,
                image_url=cover_image,
                is_cover=True,
                sort_order=0
            )
            db.session.add(cover_img)
        
        # 保存其他图片
        for idx, img_url in enumerate(other_images):
            other_img = MaterialImage(
                material_id=material.id,
                image_url=img_url,
                is_cover=False,
                sort_order=idx + 1
            )
            db.session.add(other_img)
        
        # 提交到数据库
        db.session.commit()
        
        # 提示成功
        flash('素材添加成功！', 'success')
        
        # 跳转到素材列表
        return redirect(url_for('admin.materials'))
    
    # GET请求或验证失败，渲染表单
    return render_template('admin/admin_material_add.html', form=form)


@bp.route('/materials/edit/<int:material_id>', methods=['GET', 'POST'])
@login_required
@admin_required
@permission_required('material_manage')
def material_edit(material_id):
    # 获取素材
    material = Material.query.get_or_404(material_id)
    
    # 创建表单实例并填充数据
    form = MaterialForm(obj=material)
    
    # 填充素材类型选择框
    material_types = MaterialType.query.all()
    form.material_type_id.choices = [(t.id, t.name) for t in material_types]
    
    # 显式查询图片以确保正确获取
    all_images = MaterialImage.query.filter_by(material_id=material_id).order_by(MaterialImage.sort_order).all()
    cover_image = next((img for img in all_images if img.is_cover), None)
    other_images = [img for img in all_images if not img.is_cover]
    
    # 如果是POST请求
    if form.validate_on_submit():
        # 更新素材基本信息
        material.title = form.title.data
        material.description = form.description.data
        material.material_type_id = form.material_type_id.data
        material.is_published = form.is_published.data
        
        # 处理封面图
        if 'cover_image' in request.files:
            cover_file = request.files['cover_image']
            if cover_file and cover_file.filename:
                # 删除旧封面图
                if cover_image:
                    old_path = os.path.join(current_app.root_path, cover_image.image_url.lstrip('/'))
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except:
                            pass
                    db.session.delete(cover_image)
                
                # 保存新封面图
                new_cover_path = save_image(cover_file)
                new_cover = MaterialImage(
                    material_id=material.id,
                    image_url=new_cover_path,
                    is_cover=True,
                    sort_order=0
                )
                db.session.add(new_cover)
        
        # 处理要删除的现有图片（通过checkbox）
        for img in other_images:
            keep_key = f'keep_image_{img.id}'
            if keep_key not in request.form:
                # 没有勾选，删除这个图片
                img_path = os.path.join(current_app.root_path, img.image_url.lstrip('/'))
                if os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                    except:
                        pass
                db.session.delete(img)
        
        # 处理新增的其他图片
        if 'other_images' in request.files:
            other_files = request.files.getlist('other_images')
            
            # 重新查询剩余的图片来获取最大排序
            remaining_images = MaterialImage.query.filter_by(material_id=material_id, is_cover=False).all()
            current_max_sort = max([img.sort_order for img in remaining_images], default=0)
            
            for idx, file in enumerate(other_files):
                if file and file.filename:
                    saved_path = save_image(file)
                    if saved_path:
                        new_img = MaterialImage(
                            material_id=material.id,
                            image_url=saved_path,
                            is_cover=False,
                            sort_order=current_max_sort + idx + 1
                        )
                        db.session.add(new_img)
        
        # 提交到数据库
        db.session.commit()
        
        # 提示成功
        flash('素材更新成功！', 'success')
        
        # 跳转到素材列表
        return redirect(url_for('admin.materials'))
    
    # GET请求，渲染表单
    return render_template('admin/admin_material_add.html', 
                           form=form, 
                           material=material, 
                           cover_image=cover_image, 
                           other_images=other_images)


@bp.route('/secrets')
@login_required
@admin_required
@permission_required('secret_manage')
def secrets():
    """卡密管理页面"""
    from datetime import datetime
    now = datetime.utcnow()
    
    # 获取卡密类型参数，默认为注册卡密
    secret_type = request.args.get('type', 'register')
    if secret_type not in ['register', 'terminal']:
        secret_type = 'register'
    
    # 获取搜索关键词和筛选状态
    search_keyword = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    # 根据卡密类型选择模型
    if secret_type == 'register':
        SecretModel = RegisterSecret
    else:
        SecretModel = TerminalSecret
    
    # 查询卡密
    query = SecretModel.query
    
    if search_keyword:
        # 搜索卡密文本 或 搜索关联用户的昵称
        query = query.outerjoin(User).filter(
            (SecretModel.secret.contains(search_keyword)) | 
            (User.username.contains(search_keyword))
        )
    
    # 状态筛选
    if status_filter == 'unused':
        # 未使用：is_used = False
        query = query.filter_by(is_used=False)
    elif status_filter == 'used':
        # 已使用：is_used = True 且 user_id 不为 None
        query = query.filter(SecretModel.is_used == True, SecretModel.user_id != None)
    elif status_filter == 'expired':
        # 已失效：已过期 或 已释放
        query = query.filter(
            ((SecretModel.is_used == True) & (SecretModel.expires_at != None) & (now > SecretModel.expires_at)) |
            ((SecretModel.is_used == True) & (SecretModel.user_id == None))
        )
    
    # 按创建时间倒序
    secrets = query.order_by(SecretModel.created_at.desc()).all()
    
    # 计算统计数据
    total_count = SecretModel.query.count()
    unused_count = SecretModel.query.filter_by(is_used=False).count()
    released_count = SecretModel.query.filter_by(is_used=True, user_id=None).count()
    
    return render_template('admin/admin_secrets.html', secrets=secrets, total_count=total_count, unused_count=unused_count, released_count=released_count, now=now, status_filter=status_filter, secret_type=secret_type)


@bp.route('/api/secrets', methods=['POST'])
@login_required
@admin_required
@permission_required('secret_manage')
def api_create_secrets():
    """批量生成卡密API"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
    
    duration_type = data.get('duration_type', 'permanent')
    count = data.get('count', 1)
    secret_type = data.get('type', 'register')
    
    if secret_type not in ['register', 'terminal']:
        secret_type = 'register'
    
    # 验证数量
    try:
        count = int(count)
        if count < 1 or count > 100:
            return jsonify({'success': False, 'message': '生成数量必须在1-100之间'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': '生成数量必须是数字'}), 400
    
    # 验证时长类型
    valid_types = ['1min', '1day', '1month', '1year', 'permanent']
    if duration_type not in valid_types:
        return jsonify({'success': False, 'message': '无效的时长类型'}), 400
    
    # 时长类型显示名称映射
    duration_names = {
        '1min': '1分钟卡',
        '1day': '日卡(1天)',
        '1month': '月卡(1个月)',
        '1year': '年卡(1年)',
        'permanent': '永久卡'
    }
    
    from datetime import datetime, timedelta
    import random
    import string
    
    secrets = []
    
    # 定义字符集：数字+大小写字母
    charset = string.digits + string.ascii_letters
    
    # 根据卡密类型选择模型和前缀
    if secret_type == 'register':
        SecretModel = RegisterSecret
        prefix = 'sk-'
        random_length = 18
    else:
        SecretModel = TerminalSecret
        prefix = 'zdsk-'
        random_length = 10
    
    for _ in range(count):
        # 生成唯一卡密
        random_part = ''.join(random.choice(charset) for _ in range(random_length))
        secret_str = f"{prefix}{random_part}"
        
        # 创建卡密（生成时不设置过期时间，使用时再计算）
        secret = SecretModel(
            secret=secret_str,
            duration_type=duration_type,
            expires_at=None
        )
        db.session.add(secret)
        secrets.append(secret_str)
    
    db.session.commit()
    
    secret_type_name = '注册' if secret_type == 'register' else '终端'
    
    return jsonify({
        'success': True,
        'message': f'成功生成 {count} 个{secret_type_name}{duration_names[duration_type]}',
        'data': {
            'secrets': secrets,
            'duration_type': duration_type,
            'duration_name': duration_names[duration_type],
            'count': count
        }
    })


@bp.route('/api/secrets/<int:secret_id>', methods=['DELETE'])
@login_required
@admin_required
@permission_required('secret_manage')
def api_delete_secret(secret_id):
    """删除卡密API"""
    secret_type = request.args.get('type', 'register')
    if secret_type not in ['register', 'terminal']:
        secret_type = 'register'
    
    if secret_type == 'register':
        SecretModel = RegisterSecret
    else:
        SecretModel = TerminalSecret
    
    secret = SecretModel.query.get_or_404(secret_id)
    
    # 已使用的卡密不能删除，除非已释放（user_id=None）
    if secret.is_used and secret.user_id is not None:
        return jsonify({'success': False, 'message': '已使用且未释放的卡密不能删除'}), 400
    
    db.session.delete(secret)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '卡密删除成功'
    })


@bp.route('/api/secrets/delete-released', methods=['POST'])
@login_required
@admin_required
@permission_required('secret_manage')
def api_delete_released_secrets():
    """批量删除已释放的卡密API"""
    secret_type = request.args.get('type', 'register')
    if secret_type not in ['register', 'terminal']:
        secret_type = 'register'
    
    if secret_type == 'register':
        SecretModel = RegisterSecret
    else:
        SecretModel = TerminalSecret
    
    from datetime import datetime
    now = datetime.utcnow()
    
    # 查询已释放的卡密（is_used=True 且 user_id=None）
    released_secrets = SecretModel.query.filter(
        SecretModel.is_used == True,
        SecretModel.user_id == None
    ).all()
    
    deleted_count = 0
    for secret in released_secrets:
        db.session.delete(secret)
        deleted_count += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'成功删除 {deleted_count} 个已释放的卡密',
        'data': {
            'deleted_count': deleted_count
        }
    })


@bp.route('/api/secrets/<int:secret_id>/release', methods=['POST'])
@login_required
@admin_required
@permission_required('secret_manage')
def api_release_secret(secret_id):
    """释放卡密API"""
    secret_type = request.args.get('type', 'register')
    if secret_type not in ['register', 'terminal']:
        secret_type = 'register'
    
    if secret_type == 'register':
        SecretModel = RegisterSecret
    else:
        SecretModel = TerminalSecret
    
    secret = SecretModel.query.get_or_404(secret_id)
    
    # 检查卡密是否已被使用且未释放
    if not secret.is_used:
        return jsonify({'success': False, 'message': '未使用的卡密不能释放'}), 400
    
    if secret.user_id is None:
        return jsonify({'success': False, 'message': '该卡密已被释放'}), 400
    
    # 释放卡密：解除与用户的关联
    secret.user_id = None
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '卡密释放成功'
    })


@bp.route('/users')
@login_required
@admin_required
@permission_required('user_manage')
def users():
    """用户列表管理页面"""
    # 获取搜索关键词
    search_keyword = request.args.get('search', '').strip()
    
    # 查询用户
    query = User.query
    
    if search_keyword:
        # 搜索用户名或邮箱
        query = query.filter(
            (User.username.contains(search_keyword)) | 
            (User.email.contains(search_keyword))
        )
    
    # 按创建时间倒序
    users = query.order_by(User.created_at.desc()).all()
    
    # 计算统计数据
    total_count = User.query.count()
    
    return render_template('admin/admin_users.html', users=users, total_count=total_count, search_keyword=search_keyword)


@bp.route('/users/<int:user_id>/permissions', methods=['GET', 'POST'])
@login_required
@admin_required
@permission_required('user_manage')
def user_permissions(user_id):
    """用户权限管理页面"""
    if not current_user.is_super_admin:
        flash('只有超级管理员才能管理权限', 'danger')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(user_id)
    
    if user.is_super_admin:
        flash('不能修改超级管理员的权限', 'danger')
        return redirect(url_for('admin.users'))
    
    # 获取所有权限
    all_permissions = Permission.query.all()
    
    # 获取用户已有权限的ID集合
    user_permission_ids = set(up.permission_id for up in user.user_permissions)
    
    if request.method == 'POST':
        # 获取选中的权限
        selected_permission_ids = request.form.getlist('permissions')
        
        # 删除用户所有权限
        UserPermission.query.filter_by(user_id=user_id).delete()
        
        # 添加新权限
        for perm_id in selected_permission_ids:
            user_perm = UserPermission(
                user_id=user_id,
                permission_id=int(perm_id)
            )
            db.session.add(user_perm)
        
        db.session.commit()
        flash('权限更新成功', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/admin_user_permissions.html', 
                           user=user, 
                           all_permissions=all_permissions,
                           user_permission_ids=user_permission_ids)


@bp.route('/api/users/<int:user_id>/set-admin', methods=['POST'])
@login_required
@admin_required
@permission_required('user_manage')
def api_set_admin(user_id):
    """设置用户为管理员"""
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': '只有超级管理员才能执行此操作'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.is_super_admin:
        return jsonify({'success': False, 'message': '不能修改超级管理员'}), 400
    
    user.is_admin = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '设置成功'
    })


@bp.route('/api/users/<int:user_id>/remove-admin', methods=['POST'])
@login_required
@admin_required
@permission_required('user_manage')
def api_remove_admin(user_id):
    """取消用户管理员身份"""
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': '只有超级管理员才能执行此操作'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.is_super_admin:
        return jsonify({'success': False, 'message': '不能修改超级管理员'}), 400
    
    user.is_admin = False
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '取消成功'
    })


@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
@permission_required('user_manage')
def api_delete_user(user_id):
    """删除用户"""
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': '只有超级管理员才能执行此操作'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.is_super_admin:
        return jsonify({'success': False, 'message': '不能删除超级管理员'}), 400
    
    if user.is_admin:
        return jsonify({'success': False, 'message': '请先取消该用户的管理员身份'}), 400
    
    # 删除用户作品库素材的图片文件
    for user_material in user.user_materials:
        for img in user_material.images:
            if img.image_url:
                file_path = os.path.join(current_app.root_path, img.image_url.lstrip('/'))
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
    
    # 删除用户（级联删除会自动删除用户的卡密、作品库素材和作品库素材图片记录）
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '删除成功'
    })


@bp.route('/api/users/<int:user_id>/unbind-device', methods=['POST'])
@login_required
@admin_required
@permission_required('user_manage')
def api_unbind_user_device(user_id):
    """解绑用户设备"""
    if not current_user.is_super_admin and not current_user.is_admin:
        return jsonify({'success': False, 'message': '只有管理员才能执行此操作'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if not user.bound_device_id:
        return jsonify({'success': False, 'message': '该用户未绑定任何设备'}), 400
    
    user.bound_device_id = None
    user.device_unbind_status = 0
    user.device_unbind_requested_at = None
    db.session.commit()
    
    logger.info(f'管理员 {current_user.username} 解绑了用户 {user.username} 的设备')
    
    return jsonify({
        'success': True,
        'message': '设备解绑成功'
    })


@bp.route('/api/users/<int:user_id>/approve-unbind', methods=['POST'])
@login_required
@admin_required
@permission_required('user_manage')
def api_approve_unbind(user_id):
    """同意用户的解绑申请"""
    if not current_user.is_super_admin and not current_user.is_admin:
        return jsonify({'success': False, 'message': '只有管理员才能执行此操作'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.device_unbind_status != 1:
        return jsonify({'success': False, 'message': '该用户没有待处理的解绑申请'}), 400
    
    # 解除设备绑定并重置申请状态
    user.bound_device_id = None
    user.device_unbind_status = 0
    user.device_unbind_requested_at = None
    db.session.commit()
    
    logger.info(f'管理员 {current_user.username} 同意了用户 {user.username} 的解绑申请')
    
    return jsonify({
        'success': True,
        'message': '解绑申请已同意，设备已解绑'
    })


@bp.route('/api/users/<int:user_id>/reject-unbind', methods=['POST'])
@login_required
@admin_required
@permission_required('user_manage')
def api_reject_unbind(user_id):
    """拒绝用户的解绑申请"""
    if not current_user.is_super_admin and not current_user.is_admin:
        return jsonify({'success': False, 'message': '只有管理员才能执行此操作'}), 403
    
    user = User.query.get_or_404(user_id)
    
    if user.device_unbind_status != 1:
        return jsonify({'success': False, 'message': '该用户没有待处理的解绑申请'}), 400
    
    # 重置申请状态
    user.device_unbind_status = 0
    user.device_unbind_requested_at = None
    db.session.commit()
    
    logger.info(f'管理员 {current_user.username} 拒绝了用户 {user.username} 的解绑申请')
    
    return jsonify({
        'success': True,
        'message': '解绑申请已拒绝'
    })


@bp.route('/material-types')
@login_required
@admin_required
@permission_required('type_manage')
def material_types():
    """分类管理页面"""
    material_types = MaterialType.query.order_by(MaterialType.created_at.desc()).all()
    return render_template('admin/admin_material_types.html', material_types=material_types)


@bp.route('/api/material-types', methods=['POST'])
@login_required
@admin_required
@permission_required('type_manage')
def api_add_material_type():
    """添加分类API"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'success': False, 'message': '分类名称不能为空'}), 400
    
    name = data['name'].strip()
    if not name:
        return jsonify({'success': False, 'message': '分类名称不能为空'}), 400
    
    # 检查分类名称是否已存在
    existing = MaterialType.query.filter_by(name=name).first()
    if existing:
        return jsonify({'success': False, 'message': '分类名称已存在'}), 400
    
    material_type = MaterialType(
        name=name,
        description=data.get('description', '').strip()
    )
    db.session.add(material_type)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '分类添加成功',
        'data': {
            'id': material_type.id,
            'name': material_type.name,
            'description': material_type.description
        }
    })


@bp.route('/api/material-types/<int:type_id>', methods=['GET'])
@login_required
@admin_required
@permission_required('type_manage')
def api_get_material_type(type_id):
    """获取单个分类API"""
    material_type = MaterialType.query.get_or_404(type_id)
    return jsonify({
        'success': True,
        'data': {
            'id': material_type.id,
            'name': material_type.name,
            'description': material_type.description
        }
    })


@bp.route('/api/material-types/<int:type_id>', methods=['PUT'])
@login_required
@admin_required
@permission_required('type_manage')
def api_update_material_type(type_id):
    """更新分类API"""
    material_type = MaterialType.query.get_or_404(type_id)
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'success': False, 'message': '分类名称不能为空'}), 400
    
    name = data['name'].strip()
    if not name:
        return jsonify({'success': False, 'message': '分类名称不能为空'}), 400
    
    # 检查分类名称是否已存在（排除当前分类）
    existing = MaterialType.query.filter(MaterialType.name == name, MaterialType.id != type_id).first()
    if existing:
        return jsonify({'success': False, 'message': '分类名称已存在'}), 400
    
    material_type.name = name
    material_type.description = data.get('description', '').strip()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '分类更新成功',
        'data': {
            'id': material_type.id,
            'name': material_type.name,
            'description': material_type.description
        }
    })


@bp.route('/api/material-types/<int:type_id>', methods=['DELETE'])
@login_required
@admin_required
@permission_required('type_manage')
def api_delete_material_type(type_id):
    """删除分类API"""
    material_type = MaterialType.query.get_or_404(type_id)
    
    # 将关联素材的分类ID设为NULL
    for material in material_type.materials:
        material.material_type_id = None
    
    db.session.delete(material_type)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '分类删除成功'
    })


@bp.route('/api/materials/<int:material_id>', methods=['DELETE'])
@login_required
@admin_required
@permission_required('material_manage')
def api_delete_material(material_id):
    """删除素材API"""
    material = Material.query.get_or_404(material_id)
    
    # 删除关联的图片文件
    for img in material.images:
        if img.image_url:
            # 构建完整文件路径
            file_path = os.path.join(current_app.root_path, img.image_url.lstrip('/'))
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
    
    # 删除素材（级联删除关联图片）
    db.session.delete(material)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '素材删除成功'
    })


@bp.route('/api/materials/batch-delete', methods=['POST'])
@login_required
@admin_required
@permission_required('material_manage')
def api_batch_delete_materials():
    """批量删除素材API"""
    try:
        data = request.get_json()
        material_ids = data.get('material_ids', [])
        
        if not material_ids or len(material_ids) == 0:
            return jsonify({'success': False, 'message': '请选择要删除的素材'}), 400
        
        # 查询要删除的素材
        materials = Material.query.filter(Material.id.in_(material_ids)).all()
        
        if not materials:
            return jsonify({'success': False, 'message': '未找到要删除的素材'}), 404
        
        # 删除关联的图片文件
        for material in materials:
            for img in material.images:
                if img.image_url:
                    file_path = os.path.join(current_app.root_path, img.image_url.lstrip('/'))
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except:
                            pass
        
        # 删除素材（级联删除关联图片）
        for material in materials:
            db.session.delete(material)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {len(materials)} 个素材'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'批量删除素材失败: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/materials/delete-all', methods=['POST'])
@login_required
@admin_required
@permission_required('material_manage')
def api_delete_all_materials():
    """全部删除素材API（清空素材库）"""
    try:
        # 查询所有素材
        materials = Material.query.all()
        
        if not materials:
            return jsonify({'success': False, 'message': '素材库已经是空的'}), 400
        
        # 删除关联的图片文件
        for material in materials:
            for img in material.images:
                if img.image_url:
                    file_path = os.path.join(current_app.root_path, img.image_url.lstrip('/'))
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except:
                            pass
        
        # 删除所有素材（级联删除关联图片）
        for material in materials:
            db.session.delete(material)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功清空素材库，共删除 {len(materials)} 个素材'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'清空素材库失败: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/materials/batch-upload', methods=['POST'])
@login_required
@admin_required
@permission_required('material_manage')
def batch_upload_material():
    """批量上传素材API（带安全验证）"""
    try:
        # 获取表单数据
        folder_name = request.form.get('folder_name')
        text_file = request.files.get('text_file')
        
        # 获取所有图片文件 - 使用更兼容的方式
        image_files = []
        for key in request.files:
            if key.startswith('images'):
                files = request.files.getlist(key)
                image_files.extend(files)
        
        # 验证图片文件
        invalid_files = []
        valid_image_files = []
        for img_file in image_files:
            if img_file and img_file.filename:
                is_valid, error_msg = validate_file(img_file, ALLOWED_IMAGE_EXTENSIONS)
                if is_valid:
                    valid_image_files.append(img_file)
                else:
                    invalid_files.append(f'{img_file.filename}: {error_msg}')
        
        # 如果有无效文件，返回错误
        if invalid_files:
            return jsonify({
                'success': False,
                'message': '部分文件验证失败',
                'invalid_files': invalid_files
            }), 400
        
        # 如果没有有效图片，返回错误
        if not valid_image_files:
            return jsonify({
                'success': False,
                'message': '没有有效的图片文件'
            }), 400
        
        # 解析文案.txt
        title = ""
        content = ""
        if text_file:
            content_str = text_file.read().decode('utf-8')
            title_match = re.search(r'title\s*[：:]\s*"(.*?)"', content_str, re.DOTALL | re.IGNORECASE)
            content_match = re.search(r'content\s*[：:]\s*"(.*?)"', content_str, re.DOTALL | re.IGNORECASE)
            if title_match:
                title = title_match.group(1)
            if content_match:
                content = content_match.group(1)
        
        # 检查标题是否为空
        if not title:
            title = folder_name or "未命名素材"
        
        # 图片按文件名排序
        valid_image_files.sort(key=lambda x: x.filename)
        
        # 获取或创建"副业"分类
        material_type = MaterialType.query.filter_by(name="副业").first()
        if not material_type:
            material_type = MaterialType(name="副业", description="批量上传的素材分类")
            db.session.add(material_type)
        
        # 创建素材记录
        material = Material(
            title=title,
            description=content,
            material_type_id=material_type.id if material_type.id else None,
            is_published=True
        )
        db.session.add(material)
        
        # 如果分类是新创建的，需要先flush获取ID
        if not material_type.id:
            db.session.flush()
            material.material_type_id = material_type.id
        
        # 再flush获取素材ID
        db.session.flush()
        
        # 保存图片
        for idx, img_file in enumerate(valid_image_files):
            img_url = save_image(img_file)
            if img_url:
                image = MaterialImage(
                    material_id=material.id,
                    image_url=img_url,
                    is_cover=(idx == 0),
                    sort_order=idx
                )
                db.session.add(image)
        
        # 提交到数据库
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'素材 "{title}" 上传成功',
            'uploaded_images': len(valid_image_files)
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'批量上传素材失败: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500
