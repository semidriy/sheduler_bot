from aiogram import types
from config_data.config import Config, load_config

config: Config = load_config()
admin_link=config.tg_bot.admin_link

##  Клавиатура Админ меню
admin_kb = [
    [
        types.InlineKeyboardButton(text='🙋🏼‍♂️ Приветствие', callback_data='admin_hello_message')
    ],
    [
        types.InlineKeyboardButton(text='📮 Рассылка', callback_data='news'),
        types.InlineKeyboardButton(text='📊 Статистика', callback_data='admin_stat')
    ],
    [
        types.InlineKeyboardButton(text='💰 Выплата', callback_data='cashback'),
        types.InlineKeyboardButton(text='👤 Админы', callback_data='admin_edit')
    ]
]

subadmin_kb = [
    # [types.InlineKeyboardButton(text='👤 Список админов', callback_data='admin_list')],
    [
        types.InlineKeyboardButton(text='➕ Выдать права', callback_data='grant_subadmin_profile'),
        types.InlineKeyboardButton(text='➖ Удалить админа', callback_data='grant_down_subadmin_profile')
    ],
    [types.InlineKeyboardButton(text='🔗 Изменить ссылку', callback_data='edit_bounty_link')],
    [types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_admin')],
]

## Клавиатура меню рассылки
mailing_menu = [
        [types.InlineKeyboardButton(text='📩Рассылка админам', callback_data='admin_news')],
        [types.InlineKeyboardButton(text='📬Рассылка пользователям', callback_data='user_news')],
        [types.InlineKeyboardButton(text='📝 Мои отложенные админам', callback_data='list_scheduled_admins')],
        [types.InlineKeyboardButton(text='📝 Мои отложенные юзерам', callback_data='list_scheduled_users')],
        [types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_admin')]
    ]

mailing_admin_menu = [
        [types.InlineKeyboardButton(text='📩 Отложенная рассылка', callback_data='create_waiting_first')],
        [types.InlineKeyboardButton(text='📬 Отправить сейчас', callback_data='send_admin_now')],
        [types.InlineKeyboardButton(text='🔙 Назад', callback_data='news')]
    ]

mailing_user_menu = [
        [types.InlineKeyboardButton(text='📩 Отложенная рассылка', callback_data='create_waiting_user_first')],
        [types.InlineKeyboardButton(text='📬 Отправить сейчас', callback_data='send_users_now')],
        [types.InlineKeyboardButton(text='🔙 Назад', callback_data='news')]
    ]

## Клавиатуры для возращений назад в меню редактирования сообщений
button_back_to_privetka = [
    [types.InlineKeyboardButton(text='🔙 Назад', callback_data='admin_hello_message')]
]

button_back_subadmin = [
    [types.InlineKeyboardButton(text='🔙 Назад', callback_data='admin_edit')]
]

button_back_to_admin = [
    [types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_admin')]
]

##  Клавиатура для вывода
cash_out_kb = [
    [types.InlineKeyboardButton(text='📩 Написать', url=f"{admin_link}")]
]

##  Клавиатура для меню выплат
edit_cashback = [
    [types.InlineKeyboardButton(text='💲 Изменить мин. выплату', callback_data='edit_min_cashback')],
    [types.InlineKeyboardButton(text='💸 Изменить ОЗР', callback_data='edit_bounty_cashback')],
    [types.InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_admin')]
]
