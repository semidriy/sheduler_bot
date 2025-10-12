from aiogram.filters import Command
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from keyboards.admin_kb import admin_kb
from is_admin.isadmin import IsAdmin
from keyboards.admin_kb import admin_kb

router = Router()

admin_keyboard_main = types.InlineKeyboardMarkup(inline_keyboard=admin_kb)

router = Router()

# async def delete_previous_messages(chat_id: int, message_ids: list, bot):
#     """Удаляет предыдущие сообщения красиво"""
#     for msg_id in message_ids:
#         try:
#             await bot.delete_message(chat_id, msg_id)
#         except Exception as e:
#             print(f"Не удалось удалить сообщение {msg_id}: {e}")

## Ловим команды /admin
@router.message(Command('admin'), IsAdmin())
async def admin_command(message: types.Message) -> None:
    await message.answer('Добро пожаловать в админ-панель 🙋🏼‍♂️', reply_markup=admin_keyboard_main)

## Вернуться назад
@router.callback_query(F.data == 'back_to_admin')
async def back_admin_menu(query: types.CallbackQuery, state: FSMContext, bot):
    await state.clear()
    await query.message.edit_text('Добро пожаловать в админ-панель 🙋🏼‍♂️', reply_markup=admin_keyboard_main)

