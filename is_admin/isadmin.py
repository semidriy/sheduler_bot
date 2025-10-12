from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from config_data.config import load_config
from functions.db_handler import get_subadmin_user_id

config = load_config()

##  id админ-пользвоателей
# admin_ids = [202606957]

class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        return obj.from_user.id in config.tg_bot.admin_ids
    
class IsSubadmin(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        users = await get_subadmin_user_id()
        return obj.from_user.id in users