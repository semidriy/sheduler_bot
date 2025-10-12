###
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton
import aiosqlite


async def get_kb_msg():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    msg = await cursor.execute('SELECT id FROM msg_kb;')
    msg = await msg.fetchall()
    await cursor.close()
    await connect.close()
    return msg

async def reply_menu():
    keyboard = InlineKeyboardBuilder()
    msgs = await get_kb_msg()
    
    for msg_tuple in msgs:
        # msg_tuple - это кортеж (1,), извлекаем первый элемент
        msg_id = msg_tuple[0]
        keyboard.add(InlineKeyboardButton(
            text=f"✏️ {msg_id}-е сообщение",
            callback_data=f"message_{msg_id}"
        ))
        
        keyboard.add(InlineKeyboardButton(
            text="⏳ Тайминг",
            callback_data=f"timer_{msg_id}"
        ))

        keyboard.add(InlineKeyboardButton(
            text="🗑️ Удалить",
            callback_data=f"delete_{msg_id}"
        ))
        
    keyboard.add(InlineKeyboardButton(
        text="➕ Добавить",
        callback_data="add_message"
    ))
    keyboard.add(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="back_to_admin"
    ))

    return keyboard.adjust(3).as_markup()

async def edit_menu(message_id):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(
        text=f"🏞️ Изменить медиа",
        callback_data=f"edit_media_{message_id}"
    ))

    keyboard.add(InlineKeyboardButton(
        text="📝 Изменить текст",
        callback_data=f"edit_text_{message_id}"
    ))

    keyboard.add(InlineKeyboardButton(
        text="📝 Изменить имя кнопки",
        callback_data=f"edit_button_name_{message_id}"
    ))

    keyboard.add(InlineKeyboardButton(
        text="📝 Изменить ссылку",
        callback_data=f"edit_url_{message_id}"
    ))

    keyboard.add(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="admin_hello_message"
    ))

    return keyboard.adjust(1).as_markup()