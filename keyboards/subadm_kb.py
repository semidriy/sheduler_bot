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
btn_wallet_1 = KeyboardButton(text='Изменить TRC20 💸')
btn_wallet_2 = KeyboardButton(text='Изменить BEP20 💳')
btn_wallet_3 = KeyboardButton(text='Назад 🔙')

wallet_kb = ReplyKeyboardMarkup(
    keyboard=[[btn_wallet_1, btn_wallet_2],
              [btn_wallet_3]],
    resize_keyboard=True
)
