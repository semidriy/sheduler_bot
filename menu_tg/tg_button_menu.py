from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from config_data.config import load_config

config = load_config()

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/admin',
                   description='Меню Администратора'),
    ]
    for admin_id in config.tg_bot.admin_ids:
        await bot.set_my_commands(
            commands=main_menu_commands,
            scope=BotCommandScopeChat(chat_id=admin_id)  ## chat_id обязателен, чтобы делить по группам пользователей
        )