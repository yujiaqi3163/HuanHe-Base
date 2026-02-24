# ============================================================
# init_announcements.py
# 
# 初始化公告表并添加测试数据
# ============================================================

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Announcement


def init_announcements():
    """初始化公告表"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表（如果不存在）
        db.create_all()
        print('✅ 数据库表检查/创建完成')
        
        # 检查是否已有公告
        existing_count = Announcement.query.count()
        if existing_count > 0:
            print(f'⚠️  公告表中已存在 {existing_count} 条数据，跳过初始化')
            return
        
        print('📢 开始初始化公告表...')
        
        # 创建测试公告数据
        announcements_data = [
            {
                'title': '🎉 全新功能上线',
                'content': '''
                    <div class="bg-gray-50 rounded-2xl p-5 mb-5">
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            亲爱的用户：
                        </p>
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            我们很高兴地宣布，作品库搜索功能已正式上线！现在您可以快速搜索自己的素材和收藏的素材，让素材管理更便捷。
                        </p>
                        <div class="bg-white rounded-xl p-4 border border-gray-200 mb-4">
                            <h4 class="font-bold text-gray-800 text-sm mb-3">✨ 新功能亮点</h4>
                            <ul class="space-y-2">
                                <li class="flex items-start gap-2 text-xs text-gray-600">
                                    <svg class="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                    </svg>
                                    支持按素材标题实时搜索
                                </li>
                                <li class="flex items-start gap-2 text-xs text-gray-600">
                                    <svg class="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                    </svg>
                                    "我的素材"和"收藏素材"分别搜索
                                </li>
                                <li class="flex items-start gap-2 text-xs text-gray-600">
                                    <svg class="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                    </svg>
                                    不区分大小写，支持模糊匹配
                                </li>
                            </ul>
                        </div>
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            我们会继续努力，为您带来更多优质的功能和体验！
                        </p>
                        <p class="text-sm text-gray-700 leading-relaxed">
                            祝您使用愉快！
                        </p>
                    </div>
                ''',
                'is_published': True,
                'sort_order': 5,
                'created_at': datetime.utcnow()
            },
            {
                'title': '⚡ 性能优化',
                'content': '''
                    <div class="bg-gray-50 rounded-2xl p-5 mb-5">
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            亲爱的用户：
                        </p>
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            我们对AI生成速度进行了全面优化！经过技术团队的不懈努力，现在素材生成速度提升了30%，让您的创作更加高效。
                        </p>
                        <div class="bg-blue-50 rounded-xl p-4 border border-blue-200 mb-4">
                            <h4 class="font-bold text-blue-800 text-sm mb-3">🚀 优化内容</h4>
                            <ul class="space-y-2">
                                <li class="flex items-start gap-2 text-xs text-blue-700">
                                    <svg class="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                    模型推理速度提升30%
                                </li>
                                <li class="flex items-start gap-2 text-xs text-blue-700">
                                    <svg class="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                                    </svg>
                                    服务器负载均衡优化
                                </li>
                                <li class="flex items-start gap-2 text-xs text-blue-700">
                                    <svg class="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    图片压缩传输优化
                                </li>
                            </ul>
                        </div>
                        <p class="text-sm text-gray-700 leading-relaxed">
                            感谢您一直以来的支持！
                        </p>
                    </div>
                ''',
                'is_published': True,
                'sort_order': 4,
                'created_at': datetime.utcnow() - timedelta(days=2)
            },
            {
                'title': '💝 会员专属',
                'content': '''
                    <div class="bg-gray-50 rounded-2xl p-5 mb-5">
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            尊敬的VIP会员：
                        </p>
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            感谢您对我们平台的支持！为了给您提供更好的体验，我们为VIP会员新增了专属素材库，包含海量高质量素材，还有更多专属功能等您体验！
                        </p>
                        <div class="bg-purple-50 rounded-xl p-4 border border-purple-200 mb-4">
                            <h4 class="font-bold text-purple-800 text-sm mb-3">👑 VIP专属特权</h4>
                            <ul class="space-y-2">
                                <li class="flex items-start gap-2 text-xs text-purple-700">
                                    <svg class="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                                    </svg>
                                    专属素材库（10万+高质量素材）
                                </li>
                                <li class="flex items-start gap-2 text-xs text-purple-700">
                                    <svg class="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                    优先生成通道
                                </li>
                                <li class="flex items-start gap-2 text-xs text-purple-700">
                                    <svg class="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.999 3.999 0 00-1.564.317z" />
                                    </svg>
                                    专属客服支持
                                </li>
                                <li class="flex items-start gap-2 text-xs text-purple-700">
                                    <svg class="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h10a2 2 0 002-2z" />
                                    </svg>
                                    无水印导出
                                </li>
                            </ul>
                        </div>
                        <p class="text-sm text-gray-700 leading-relaxed">
                            祝您创作愉快！
                        </p>
                    </div>
                ''',
                'is_published': True,
                'sort_order': 3,
                'created_at': datetime.utcnow() - timedelta(days=4)
            },
            {
                'title': '🔒 安全更新',
                'content': '''
                    <div class="bg-gray-50 rounded-2xl p-5 mb-5">
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            亲爱的用户：
                        </p>
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            您的账号安全是我们最关心的！为了更好地保护您的账号安全，我们对账号安全系统进行了升级，新增设备绑定功能。
                        </p>
                        <div class="bg-red-50 rounded-xl p-4 border border-red-200 mb-4">
                            <h4 class="font-bold text-red-800 text-sm mb-3">🛡️ 安全升级</h4>
                            <ul class="space-y-2">
                                <li class="flex items-start gap-2 text-xs text-red-700">
                                    <svg class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                    </svg>
                                    新增设备绑定功能
                                </li>
                                <li class="flex items-start gap-2 text-xs text-red-700">
                                    <svg class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                                    </svg>
                                    异常登录检测
                                </li>
                                <li class="flex items-start gap-2 text-xs text-red-700">
                                    <svg class="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                                    </svg>
                                    数据加密传输
                                </li>
                            </ul>
                        </div>
                        <p class="text-sm text-gray-700 leading-relaxed">
                            如果您发现任何异常，请立即联系客服！
                        </p>
                    </div>
                ''',
                'is_published': True,
                'sort_order': 2,
                'created_at': datetime.utcnow() - timedelta(days=6)
            },
            {
                'title': '🎁 新春活动',
                'content': '''
                    <div class="bg-gray-50 rounded-2xl p-5 mb-5">
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            亲爱的用户：
                        </p>
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            🎊 新春快乐！感谢您一直以来的支持！新春福利活动来袭，活动期间所有VIP套餐8折优惠，还有更多好礼相送！
                        </p>
                        <div class="bg-yellow-50 rounded-xl p-4 border border-yellow-200 mb-4">
                            <h4 class="font-bold text-yellow-800 text-sm mb-3">🎁 活动详情</h4>
                            <ul class="space-y-2">
                                <li class="flex items-start gap-2 text-xs text-yellow-700">
                                    <svg class="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    所有VIP套餐8折优惠
                                </li>
                                <li class="flex items-start gap-2 text-xs text-yellow-700">
                                    <svg class="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
                                    </svg>
                                    新用户首月1元体验
                                </li>
                                <li class="flex items-start gap-2 text-xs text-yellow-700">
                                    <svg class="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                                    </svg>
                                    邀请好友得奖励
                                </li>
                            </ul>
                        </div>
                        <p class="text-sm text-gray-700 leading-relaxed mb-4">
                            <strong>活动时间：</strong>即日起至2026年3月15日
                        </p>
                        <p class="text-sm text-gray-700 leading-relaxed">
                            不要错过，赶快参与吧！
                        </p>
                    </div>
                ''',
                'is_published': True,
                'sort_order': 1,
                'created_at': datetime.utcnow() - timedelta(days=9)
            }
        ]
        
        # 批量添加公告
        for data in announcements_data:
            announcement = Announcement(
                title=data['title'],
                content=data['content'],
                is_published=data['is_published'],
                sort_order=data['sort_order'],
                created_at=data['created_at']
            )
            db.session.add(announcement)
            print(f'  ✓ 添加公告: {data["title"]}')
        
        # 提交到数据库
        db.session.commit()
        
        print(f'\n✅ 公告表初始化完成！共添加 {len(announcements_data)} 条公告')


if __name__ == '__main__':
    init_announcements()
