from aiogram.filters import Command
from aiogram import Bot, types, Router, F
from services.message_scheduler import message_scheduler

from functions.get_messages import call_first_start_sales

router = Router()

## Ловим команды /start
@router.message(Command('start'))
async def admin_command(message: types.Message) -> None:
    await call_first_start_sales(message)
    await message_scheduler.schedule_welcome_messages(message.from_user.id)

@router.message(Command('delmenu'))
async def del_main_menu(message: types.Message, bot: Bot):
    await bot.delete_my_commands()
    await message.answer(text='Кнопка "Menu" удалена')