import asyncio
from aiogram import Bot, Dispatcher
from aiogram import F
from handlers import admin, admin_edit_menu, mailing_list, start, mailing_list_users, referrer, cashback, admin_statistic, builder, capcha
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.message_scheduler import message_scheduler
from menu_tg.tg_button_menu import set_main_menu
from aiogram.enums import ParseMode
from config_data.config import Config, load_config

# Создаем планировщик глобально
scheduler = AsyncIOScheduler()

async def main():
    dp = Dispatcher()
    config: Config = load_config()

    # ЗАПУСКАЕМ ПЛАНИРОВЩИК - ЭТО ВАЖНО!
    scheduler.start()

    ## Регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(mailing_list.router)
    dp.include_router(mailing_list_users.router)
    dp.include_router(referrer.router)
    dp.include_router(cashback.router)
    dp.include_router(admin_edit_menu.router)
    dp.include_router(admin_statistic.router)
    dp.include_router(builder.router)
    dp.include_router(capcha.router)

    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Настраиваем планировщик сообщений
    message_scheduler.setup(bot, scheduler)

    await set_main_menu(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())