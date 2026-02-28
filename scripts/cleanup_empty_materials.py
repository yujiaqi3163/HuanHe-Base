#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import argparse
from sqlalchemy import or_, func

# 将项目根目录加入 PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Material, MaterialImage


def find_empty_copy_materials(limit=None):
    """查询文案为空的素材"""
    query = Material.query.filter(
        or_(
            Material.description.is_(None),
            func.trim(Material.description) == ''
        )
    ).order_by(Material.id.asc())
    if limit:
        query = query.limit(limit)
    return query.all()


def main():
    parser = argparse.ArgumentParser(description="清理文案为空的素材（含其图片，级联删除）")
    parser.add_argument('--dry-run', action='store_true', help='仅预览将被删除的数据，不实际删除')
    parser.add_argument('-y', '--yes', action='store_true', help='无需确认，直接删除')
    parser.add_argument('--limit', type=int, default=None, help='限制处理的素材数量（默认全部）')
    args = parser.parse_args()

    app = create_app()

    with app.app_context():
        print('=' * 80)
        print('清理文案为空的素材')
        print('=' * 80)

        materials = find_empty_copy_materials(limit=args.limit)
        count = len(materials)

        if count == 0:
            print('✅ 没有找到文案为空的素材，数据库干净整洁')
            return

        print(f'共找到 {count} 条素材（文案为空/全空白）:')
        print('-' * 80)
        for m in materials:
            img_count = len(m.images) if hasattr(m, 'images') else 0
            print(f'  - ID={m.id:<5} 标题="{m.title}" 图片数={img_count}')
        print('-' * 80)

        if args.dry_run:
            print('🔎 预览模式（dry-run）：未进行删除操作')
            return

        if not args.yes:
            confirm = input('⚠️ 确认删除以上素材吗？此操作不可恢复！（y/N）：').strip().lower()
            if confirm not in ('y', 'yes'):
                print('已取消')
                return

        deleted_images = 0
        for m in materials:
            # 统计将被删除的图片数量（级联删除）
            deleted_images += len(m.images) if hasattr(m, 'images') else 0
            db.session.delete(m)

        db.session.commit()
        print(f'🧹 已删除 {count} 条素材，级联删除图片 {deleted_images} 张')
        print('完成！')


if __name__ == '__main__':
    main()

