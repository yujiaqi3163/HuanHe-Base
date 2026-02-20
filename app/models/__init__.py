# 导入用户模型
from app.models.user import User
# 导入注册卡密模型
from app.models.register_secret import RegisterSecret
# 导入素材类型模型
from app.models.material_type import MaterialType
# 导入素材模型
from app.models.material import Material
# 导入素材图片模型
from app.models.material_image import MaterialImage

# 导出模型，方便其他模块使用
__all__ = ['User', 'RegisterSecret', 'MaterialType', 'Material', 'MaterialImage']
