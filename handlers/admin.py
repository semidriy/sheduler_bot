from aiogram.filters import Command
from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
# from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards.admin_kb import admin_kb
# from functions.start_message import call_first_start
# from functions.second_start_message import call_second_start
# from functions.last_start_message import call_last_message_start
from is_admin.isadmin import IsAdmin
from keyboards.admin_kb import admin_kb

router = Router()

admin_keyboard_main = types.InlineKeyboardMarkup(inline_keyboard=admin_kb)
# first_message_edit_kb = types.InlineKeyboardMarkup(inline_keyboard=first_massage_edit_kb)
# second_message_edit_kb = types.InlineKeyboardMarkup(inline_keyboard=second_message_edit_kb)
# last_message_edit_kb = types.InlineKeyboardMarkup(inline_keyboard=last_message_edit_kb)
# hello_kb = types.InlineKeyboardMarkup(inline_keyboard=hello_kb)

router = Router()

async def delete_previous_messages(chat_id: int, message_ids: list, bot):
    """Удаляет предыдущие сообщения красиво"""
    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение {msg_id}: {e}")

# Тестовый роутер 
# @router.message(Command('mes'))
# async def message_git(message: types.Message):
#     scheduler = AsyncIOScheduler()

## Ловим команды /admin
@router.message(Command('admin'), IsAdmin())
async def admin_command(message: types.Message) -> None:
    await message.answer('Добро пожаловать в админ-панель 🙋🏼‍♂️', reply_markup=admin_keyboard_main)

# @router.callback_query(F.data == 'admin_hello_message', IsAdmin())
# async def admin_hello_message(query: types.CallbackQuery):
#     await query.message.edit_text('Какое сообщение ты хочешь отредактировать?', reply_markup=hello_kb)
 
# ## Обработка 1 сообщения
# @router.callback_query(F.data == 'first_message', IsAdmin())
# async def first_hello_message(query: types.CallbackQuery):
#     await query.message.answer('Твое сообщение выглядит следующим образом:')
#     await call_first_start(query.message)
#     await query.message.answer('Что ты хочешь отредактировать?', reply_markup=first_message_edit_kb)

# ## Обработка 2 сообщения
# @router.callback_query(F.data == 'second_message', IsAdmin())
# async def first_hello_message(query: types.CallbackQuery):
#     await query.message.answer('Твое сообщение выглядит следующим образом:')
#     await call_second_start(query.message)
#     await query.message.answer('Что ты хочешь отредактировать?', reply_markup=second_message_edit_kb)

# ## Обработка ПОСЛЕДНЕГО сообщения
# @router.callback_query(F.data == 'last_message', IsAdmin())
# async def first_hello_message(query: types.CallbackQuery):
#     await query.message.answer('Твое сообщение выглядит следующим образом:')
#     await call_last_message_start(query.message)
#     await query.message.answer('Что ты хочешь отредактировать?', reply_markup=last_message_edit_kb)

## Вернуться назад
@router.callback_query(F.data == 'back_to_admin')
async def back_admin_menu(query: types.CallbackQuery, state: FSMContext, bot):
    await state.clear()
    await query.message.edit_text('Добро пожаловать в админ-панель 🙋🏼‍♂️', reply_markup=admin_keyboard_main)


# ## Вернуться в меню редактирования приветки
# @router.callback_query(F.data == 'back_to_hello_kb')
# async def back_to_hello_kb(query: types.CallbackQuery, state: FSMContext, bot):
#     await state.clear()
#     await query.message.edit_text('Какое сообщение ты хочешь отредактировать?', reply_markup=hello_kb)
# ## Редактируем полное сообщение
# @router.callback_query(F.data == 'edit_message')
# async def edit_hello_message(query: types.CallbackQuery, state: FSMContext):
#     await query.message.answer('Введи сообщение')
#     await state.set_state(AdminState.waiting_for_full_message)
