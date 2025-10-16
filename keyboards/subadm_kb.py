from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import aiosqlite

btn_subadmin_menu_1 = KeyboardButton(text='Статистика 📈')
btn_subadmin_menu_2 = KeyboardButton(text='Реф. ссылка 🔗')
btn_subadmin_menu_3 = KeyboardButton(text='Вывод денег 💰')
btn_subadmin_menu_4 = KeyboardButton(text='Мои реквизиты 📌')

subadmin_menu = ReplyKeyboardMarkup(
    keyboard=[[btn_subadmin_menu_1, btn_subadmin_menu_2],
              [btn_subadmin_menu_3, btn_subadmin_menu_4]],
    resize_keyboard=True
    # one_time_keyboard=True
)
btn_wallet_1 = KeyboardButton(text='Изменить ✏️')
btn_wallet_2 = KeyboardButton(text='Назад 🔙')

wallet_kb = ReplyKeyboardMarkup(
    keyboard=[[btn_wallet_1, btn_wallet_2]],
    resize_keyboard=True
)

# async def get_id_capcha():
#     connect = await aiosqlite.connect('bot.db')
#     cursor = await connect.cursor()
#     msg = await cursor.execute('SELECT id FROM capcha_kb;')
#     msg = await msg.fetchall()
#     await cursor.close()
#     await connect.close()
#     return msg

# async def get_simple_keyboard():
#     keyboard = ReplyKeyboardBuilder()
#     msgs = await get_id_capcha()
    
#     for msg_tuple in msgs:
#         msg_id = msg_tuple[0]
#     ##  Блок для показа имени кнопки
#         connect = await aiosqlite.connect('bot.db')
#         cursor = await connect.cursor()
#         button_name = await cursor.execute('SELECT button_name FROM capcha_kb WHERE id=?', (msg_id, ))
#         await connect.commit()
#         button_name = await button_name.fetchone()
#         await cursor.close()
#         await connect.close()

#     keyboard.add(KeyboardButton(
#         text=f"{button_name}"
#         ))
    
#     return keyboard.as_markup(resize_keyboard=True)