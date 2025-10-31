import asyncio
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat
from aiogram.exceptions import TelegramBadRequest
from config_data.config import load_config

config = load_config()

# async def set_main_menu(bot: Bot):
#     main_menu_commands = [
#         BotCommand(command='/admin',
#                    description='Меню Администратора'),
#     ]
#     for admin_id in config.tg_bot.admin_ids:
#         await bot.set_my_commands(
#             commands=main_menu_commands,
#             scope=BotCommandScopeChat(chat_id=admin_id)  ## chat_id обязателен, чтобы делить по группам пользователей
#         )
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/admin', description='Меню Администратора'),
    ]
    
    successful_setups = 0
    for admin_id in config.tg_bot.admin_ids:
        try:
            # Пробуем отправить test-сообщение (невидимое) чтобы проверить доступ
            await bot.send_chat_action(chat_id=admin_id, action="typing")
            
            # Если дошли сюда, чат доступен - устанавливаем команды
            await bot.set_my_commands(
                commands=main_menu_commands,
                scope=BotCommandScopeChat(chat_id=admin_id)
            )
            print(f"✅ Команды установлены для администратора {admin_id}")
            successful_setups += 1
            
        except TelegramBadRequest as e:
            print(f"❌ Ошибка для администратора {admin_id}: {e}")
            print(f"   Бот не может взаимодействовать с пользователем {admin_id}")
            print(f"   Убедитесь, что пользователь начал диалог с ботом")
        except Exception as e:
            print(f"⚠️ Неожиданная ошибка для администратора {admin_id}: {e}")
        
        await asyncio.sleep(0.1)  # небольшая задержка между запросами
    
    print(f"Успешно установлено команд для {successful_setups} из {len(config.tg_bot.admin_ids)} администраторов")