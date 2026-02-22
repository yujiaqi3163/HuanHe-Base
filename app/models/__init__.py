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
# 导入用户二创素材模型
from app.models.user_material import UserMaterial, UserMaterialImage
# 导入配置模型
from app.models.config import Config

# 导出模型，方便其他模块使用
__all__ = ['User', 'RegisterSecret', 'MaterialType', 'Material', 'MaterialImage', 'UserMaterial', 'UserMaterialImage', 'Config']
