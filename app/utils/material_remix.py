# ============================================================
# material_remix.py
# 
# 素材二创工具模块
# 功能说明：
# 1. optimize_copywriting: 调用DeepSeek API优化文案
# 2. get_unique_css_recipes: 获取不重复的CSS样式配方
# ============================================================

# DeepSeek文案优化接口
import os
import openai
import random
import string
from app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_random_string(length=8):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def optimize_copywriting(original_text):
    """优化文案 - 使用DeepSeek API"""
    
    if not original_text or not original_text.strip():
        return original_text
    
    # 获取API密钥和基础URL
    api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    api_base = os.environ.get("DEEPSEEK_API_BASE") or "https://api.deepseek.com"
    
    if not api_key:
        logger.warning("未配置DeepSeek API Key，返回原文案")
        return original_text
    
    # 设置API
    openai.api_key = api_key
    openai.api_base = api_base
    
    system_prompt = """# Role
你是一位拥有10年经验的闲鱼顶尖卖家，擅长经营虚拟资料。你深谙闲鱼流量算法，能将平庸、高风险的文案转化为高原创、高合规的爆款。

# Task
请将提供的【原文案】进行深度二创。保持核心逻辑不变，但必须重构结构、替换敏感词、加入闲鱼原生表情。

# Rules
1. **合规性（严控）**：严禁出现“兼职、赚钱、工资、日入、月入、提现、回本、项目、副业”等词。
   - 替代方案：搞点碎银子、换个鸡腿、米、零花钱、改善生活、搞米路子、资料、方法。
2. **原生表情**：必须且只能在以下代码中选择植入：[火]、[给力]、[勾引]、[抱拳]、[色]、[微笑]、[大笑]、[害羞]、[机智]。严禁自行发明。
3. **结构重排**：采用“爆款标题+痛点/场景+利益点+引导”结构。严禁照抄原文句式，必须实现50%以上的文本差异。
4. **口语化**：语气要真诚，像是在转让闲置，而不是发广告。
5. **长度**：150-300字之间。

# Output
直接输出二创后的文案内容，不要任何解释。"""

    try:
        # 使用旧版API调用方式
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"请对这段文案进行二创，确保合规且吸引人：\n\n{original_text}"
                }
            ],
            temperature=0.8,  # 略微提高温度，增加二创的随机性和原创度
            top_p=0.9,
            max_tokens=1000,
            stream=False,
            timeout=30  # 添加30秒超时，防止API响应慢导致请求堆积
        )

        # 提取回复内容
        if response and 'choices' in response and len(response['choices']) > 0:
            return response.choices[0].message.content.strip()
        else:
            logger.warning("API返回格式异常，返回原文案")
            return original_text

    except Exception as e:
        logger.error(f"DeepSeek API调用失败: {str(e)}", exc_info=True)
        # 返回原文案作为备用
        return original_text


# CSS混合配方库
CSS_RECIPES = [
    {
        "gradient": "linear-gradient(45deg, #ff9a9e, #fad0c4)",
        "blend_mode": "multiply",
        "contrast": 1.15,
        "brightness": 1.0,
        "saturation": 1.2,
        "opacity": 0.25
    },
    {
        "gradient": "linear-gradient(120deg, #a1c4fd, #c2e9fb)",
        "blend_mode": "overlay",
        "contrast": 1.1,
        "brightness": 1.05,
        "saturation": 1.15,
        "opacity": 0.3
    },
    {
        "gradient": "linear-gradient(to right, #43e97b, #38f9d7)",
        "blend_mode": "soft-light",
        "contrast": 1.2,
        "brightness": 0.95,
        "saturation": 1.3,
        "opacity": 0.2
    },
    {
        "gradient": "linear-gradient(135deg, #667eea, #764ba2)",
        "blend_mode": "screen",
        "contrast": 1.12,
        "brightness": 1.02,
        "saturation": 1.25,
        "opacity": 0.28
    },
    {
        "gradient": "linear-gradient(45deg, #fa709a, #fee140)",
        "blend_mode": "color-dodge",
        "contrast": 1.08,
        "brightness": 1.1,
        "saturation": 1.2,
        "opacity": 0.22
    }
]


def get_random_css_recipe(exclude_recipes=None):
    """获取随机CSS混合配方，可排除已使用的配方"""
    if exclude_recipes is None:
        exclude_recipes = []
    
    available_recipes = [r for r in CSS_RECIPES if r not in exclude_recipes]
    
    if not available_recipes:
        available_recipes = CSS_RECIPES
    
    return random.choice(available_recipes)


def get_unique_css_recipes(count):
    """获取指定数量的不重复CSS配方"""
    selected_recipes = []
    
    for i in range(count):
        recipe = get_random_css_recipe(selected_recipes)
        selected_recipes.append(recipe)
    
    return selected_recipes


def generate_remix_html(image_url, recipe):
    """生成图片二创的HTML（用于前端渲染）"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: transparent;
        }}
        .container {{
            position: relative;
            width: 100%;
            max-width: 1024px;
            line-height: 0;
        }}
        img {{
            width: 100%;
            height: auto;
            filter: contrast({recipe['contrast']}) brightness({recipe['brightness']}) saturate({recipe['saturation']});
        }}
        .overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            mix-blend-mode: {recipe['blend_mode']};
            background: {recipe['gradient']};
            opacity: {recipe['opacity']};
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <img src="{image_url}" crossorigin="anonymous">
        <div class="overlay"></div>
    </div>
</body>
</html>
"""
    return html
