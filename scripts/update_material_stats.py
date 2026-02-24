# ============================================================
# update_material_stats.py
# 
# 更新素材统计脚本
# 功能说明：
# 1. 为所有素材随机设置浏览量、收藏量、下载量
# 2. 随机区间：0 - 100000
# ============================================================

import sys
import os
import random

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import Material

def update_material_stats():
    app = create_app()
    
    with app.app_context():
        materials = Material.query.all()
        print(f'找到 {len(materials)} 个素材')
        
        for material in materials:
            material.view_count = random.randint(0, 10000)
            material.favorite_count = random.randint(0, 5000)
            material.download_count = random.randint(0, 5000)
            
            print(f'素材 #{material.id} - {material.title}: 浏览={material.view_count}, 收藏={material.favorite_count}, 下载={material.download_count}')
        
        from app import db
        db.session.commit()
        
        print(f'\n✅ 成功更新了 {len(materials)} 个素材的统计数据')
        print(f'   随机区间：0 - 5000 - 10000')

if __name__ == '__main__':
    update_material_stats()
