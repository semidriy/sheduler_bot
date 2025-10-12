from aiogram import types
import aiosqlite
from config_data.config import Config, load_config
from aiogram import F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from functions.start_message import add_user, call_first_start

config: Config = load_config()
bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

async def call_first_start_sales(message: types.Message) -> None:
    ##  Добавляем пользователя в базу, если его там нет
    await add_user(message.from_user.id, message.from_user.full_name, message.from_user.username, message.text[7:], message)
    await call_first_start(message)
