# ============================================================
# tasks.py
# 
# Celery 异步任务模块
# 功能说明：
# 1. async_remix_material: 素材二创异步任务
#    - AI优化文案（调用DeepSeek API）
#    - 创建用户素材记录
#    - 复制并处理图片
#    - 支持任务重试（最多3次）
# ============================================================

# Celery 异步任务模块
import os
import json
from celery_config import celery_app
from app import create_app, db
from app.models import Material, UserMaterial, UserMaterialImage, MaterialImage, UserDownload, Config
from app.utils.material_remix import optimize_copywriting, get_unique_css_recipes
from app.utils.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def async_remix_material(self, material_id, user_id):
    """
    异步处理素材二创任务
    
    Args:
        material_id: 原始素材ID
        user_id: 用户ID
    
    Returns:
        dict: 包含用户素材ID的字典
    """
    try:
        app = create_app()
        
        with app.app_context():
            # 查询原始素材
            material = Material.query.filter_by(id=material_id, is_published=True).first()
            if not material:
                raise ValueError(f'素材不存在或未上架: {material_id}')
            
            # 1. AI 优化文案
            optimized_description = optimize_copywriting(material.description)
            if not optimized_description:
                optimized_description = material.description
            
            # 2. 创建用户素材记录
            user_material = UserMaterial(
                user_id=user_id,
                original_material_id=material_id,
                title=material.title,
                description=optimized_description,
                original_description=material.description
            )
            db.session.add(user_material)
            db.session.flush()
            
            # 3. 复制并处理图片
            material_images = MaterialImage.query.filter_by(material_id=material_id).order_by(MaterialImage.sort_order).all()
            
            # 获取不重复的 CSS 配方
            recipes = get_unique_css_recipes(len(material_images))
            
            for idx, img in enumerate(material_images):
                user_img = UserMaterialImage(
                    user_material_id=user_material.id,
                    original_image_url=img.image_url,
                    image_url=img.image_url,
                    css_recipe=json.dumps(recipes[idx], ensure_ascii=False) if idx < len(recipes) else None,
                    is_cover=img.is_cover,
                    sort_order=img.sort_order
                )
                db.session.add(user_img)
            
            db.session.commit()
            
            logger.info(f'用户素材创建成功: user_material_id={user_material.id}, user_id={user_id}')
            
            return {
                'success': True,
                'user_material_id': user_material.id
            }
            
    except Exception as e:
        logger.error(f'二创任务失败: {str(e)}', exc_info=True)
        # 重试最多3次
        if self.request.retries < self.max_retries:
            self.retry(exc=e, countdown=2 ** self.request.retries)
        return {
            'success': False,
            'error': str(e)
        }
