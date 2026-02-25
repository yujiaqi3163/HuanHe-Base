# ============================================================
# migrate_statistics_config.py
#
# 统计配置迁移脚本
# 功能说明：
# 1. 初始化统计相关配置（总创作数、总下载数）
# 2. 可以从现有数据中统计历史数据
# ============================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Config


def init_statistics_config():
    """初始化统计配置"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('初始化统计配置')
        print('=' * 60)
        
        # 确保所有表都已创建
        db.create_all()
        
        # 1. 设置总创作数（初始为0）
        print('\n1. 设置总创作数: 0')
        
        # 设置或更新总创作数
        Config.set_value(
            'total_remix_count',
            '0',
            '总创作次数（用户二创素材总数）'
        )
        print(f'   ✓ 已设置 total_remix_count = 0')
        
        # 2. 设置总下载数（初始为0）
        print('\n2. 设置总下载数: 0')
        
        # 设置或更新总下载数
        Config.set_value(
            'total_download_count',
            '0',
            '总下载次数（用户下载素材总数）'
        )
        print(f'   ✓ 已设置 total_download_count = 0')
        
        print('\n' + '=' * 60)
        print('统计配置初始化完成！')
        print('=' * 60)
        print(f'\n配置项:')
        print(f'  - total_remix_count: 0')
        print(f'  - total_download_count: 0')


if __name__ == '__main__':
    init_statistics_config()
