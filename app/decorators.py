
from functools import wraps
from flask import request, jsonify, redirect, url_for, flash
from flask_login import current_user
from app.utils.logger import get_logger

logger = get_logger(__name__)


def admin_required(f):
    """
    管理员权限装饰器 - 验证用户是否为管理员或超级管理员
    
    使用示例：
        @bp.route('/admin/some-route')
        @login_required
        @admin_required
        def admin_route():
            # 您的代码
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否已登录
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': '请先登录'
            }), 401
        
        # 检查是否为管理员或超级管理员
        if not current_user.is_admin and not current_user.is_super_admin:
            logger.warning(f'非管理员用户尝试访问管理后台: {current_user.username}')
            
            # 判断是API请求还是普通请求
            if request.path.startswith('/api/') or request.is_json:
                return jsonify({
                    'success': False,
                    'message': '只有管理员才能访问此页面'
                }), 403
            else:
                flash('只有管理员才能访问此页面', 'danger')
                if request.path.startswith('/admin'):
                    return redirect(url_for('admin.index'))
                return redirect(url_for('main.index'))
        
        # 权限验证通过
        logger.debug(f'管理员权限验证通过 - 用户: {current_user.username}')
        return f(*args, **kwargs)
    
    return decorated_function


def device_required(f):
    """
    设备锁装饰器 - 验证请求中的设备ID是否与用户绑定的设备一致
    
    从请求的 Header 中获取 device_id（X-Device-ID），并与数据库中
    该用户绑定的 bound_device_id 进行比对。如果不一致，即使 Token 正确
    也要返回 403 错误。
    
    使用示例：
        @bp.route('/api/some-protected-route', methods=['POST'])
        @login_required
        @device_required
        def some_protected_route():
            # 您的代码
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否已登录
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': '请先登录'
            }), 401
        
        # 从请求 Header 中获取 device_id
        device_id = request.headers.get('X-Device-ID')
        
        if not device_id:
            logger.warning('设备ID缺失')
            return jsonify({
                'success': False,
                'message': '设备ID缺失，请在请求Header中添加X-Device-ID'
            }), 400
        
        # 检查用户是否绑定了设备
        if not current_user.bound_device_id:
            logger.warning(f'用户 {current_user.username} 未绑定设备')
            return jsonify({
                'success': False,
                'message': '账号未绑定设备，请先登录绑定'
            }), 403
        
        # 比对设备ID
        if current_user.bound_device_id != device_id:
            logger.warning(f'设备ID不匹配 - 用户: {current_user.username}, 请求设备: {device_id}, 绑定设备: {current_user.bound_device_id}')
            return jsonify({
                'success': False,
                'message': '该账号已绑定其他设备，请先解绑'
            }), 403
        
        # 设备ID匹配，继续执行
        logger.debug(f'设备ID验证通过 - 用户: {current_user.username}, 设备: {device_id}')
        return f(*args, **kwargs)
    
    return decorated_function


def permission_required(permission_name):
    """
    权限检查装饰器 - 验证用户是否有指定权限
    
    使用示例：
        @bp.route('/admin/materials')
        @login_required
        @admin_required
        @permission_required('material_manage')
        def materials_manage():
            # 您的代码
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 检查用户是否已登录
            if not current_user.is_authenticated:
                return jsonify({
                    'success': False,
                    'message': '请先登录'
                }), 401
            
            # 超级管理员拥有所有权限
            if current_user.is_super_admin:
                return f(*args, **kwargs)
            
            # 检查用户是否有指定权限
            if not current_user.has_permission(permission_name):
                logger.warning(f'用户 {current_user.username} 尝试访问无权限的资源: {permission_name}')
                
                # 判断是API请求还是普通请求
                if request.path.startswith('/api/') or request.is_json:
                    return jsonify({
                        'success': False,
                        'message': '您没有权限访问此页面'
                    }), 403
                else:
                    flash('您没有权限访问此页面', 'danger')
                    return redirect(url_for('admin.index'))
            
            # 权限验证通过
            logger.debug(f'权限验证通过 - 用户: {current_user.username}, 权限: {permission_name}')
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

