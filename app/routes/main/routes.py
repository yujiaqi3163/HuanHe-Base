from flask import Blueprint, render_template, request, jsonify  # 导入Flask相关模块
from flask_login import login_required, current_user  # 导入登录相关模块
from app.models import User, RegisterSecret, Material  # 导入数据模型

bp = Blueprint('main', __name__)  # 创建主路由蓝图


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
    return render_template('main/profile.html')  # 渲染个人中心模板


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
