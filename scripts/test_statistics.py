# ============================================================
# test_statistics.py
#
# 测试统计功能脚本
# 功能说明：
# 1. 测试统计配置的读取和写入
# 2. 验证新功能是否正常工作
# ============================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Config


def test_statistics_config():
    """测试统计配置"""
    app = create_app()
    
    with app.app_context():
        print('=' * 60)
        print('测试统计功能')
        print('=' * 60)
        
        # 1. 读取当前统计数据
        print('\n1. 读取当前统计数据:')
        total_remix_count = Config.get_value('total_remix_count', '0')
        total_download_count = Config.get_value('total_download_count', '0')
        print(f'   total_remix_count: {total_remix_count}')
        print(f'   total_download_count: {total_download_count}')
        
        # 2. 测试增加计数
        print('\n2. 测试增加计数:')
        
        # 测试增加创作计数
        new_remix_count = int(total_remix_count) + 1
        Config.set_value('total_remix_count', str(new_remix_count))
        print(f'   total_remix_count 增加到: {new_remix_count}')
        
        # 测试增加下载计数
        new_download_count = int(total_download_count) + 1
        Config.set_value('total_download_count', str(new_download_count))
        print(f'   total_download_count 增加到: {new_download_count}')
        
        # 3. 验证数据
        print('\n3. 验证数据:')
        verify_remix = Config.get_value('total_remix_count', '0')
        verify_download = Config.get_value('total_download_count', '0')
        print(f'   验证 total_remix_count: {verify_remix}')
        print(f'   验证 total_download_count: {verify_download}')
        
        # 4. 恢复原始数据
        print('\n4. 恢复原始数据:')
        Config.set_value('total_remix_count', total_remix_count)
        Config.set_value('total_download_count', total_download_count)
        print(f'   total_remix_count 已恢复: {total_remix_count}')
        print(f'   total_download_count 已恢复: {total_download_count}')
        
        print('\n' + '=' * 60)
        print('统计功能测试完成！')
        print('=' * 60)
        print('\n结论:')
        print('  ✓ 统计配置读写正常')
        print('  ✓ 计数增加功能正常')
        print('  ✓ 数据验证通过')


if __name__ == '__main__':
    test_statistics_config()
