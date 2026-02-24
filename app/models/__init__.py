# 导入用户模型
from app.models.user import User
# 导入注册卡密模型
from app.models.register_secret import RegisterSecret
# 导入终端卡密模型
from app.models.terminal_secret import TerminalSecret
# 导入素材类型模型
from app.models.material_type import MaterialType
# 导入素材模型
from app.models.material import Material
# 导入素材图片模型
from app.models.material_image import MaterialImage
# 导入用户二创素材模型
from app.models.user_material import UserMaterial, UserMaterialImage
# 导入用户收藏素材模型
from app.models.user_favorite import UserFavorite
# 导入用户下载素材模型
from app.models.user_download import UserDownload
# 导入配置模型
from app.models.config import Config
# 导入权限模型
from app.models.permission import Permission, UserPermission, init_permissions
# 导入公告模型
from app.models.announcement import Announcement

# 导出模型，方便其他模块使用
__all__ = ['User', 'RegisterSecret', 'TerminalSecret', 'MaterialType', 'Material', 'MaterialImage', 'UserMaterial', 'UserMaterialImage', 'UserFavorite', 'UserDownload', 'Config', 'Permission', 'UserPermission', 'init_permissions', 'Announcement']
