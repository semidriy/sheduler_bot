from aiogram import types
import aiosqlite

##  Функция обработки админов 2 группы
async def get_subadmin_user_id():
    connect = await aiosqlite.connect('bot.db')  
    cursor = await connect.cursor()
    users = await cursor.execute('SELECT user_id FROM users WHERE id_group=2')
    users = await users.fetchall()
    await cursor.close()
    await connect.close()
    users = [user[0] for user in users]
    return users

##  Функция обработки пользователей 3 группы
async def get_subusers_user_id():
    connect = await aiosqlite.connect('bot.db')  
    cursor = await connect.cursor()
    users = await cursor.execute('SELECT user_id FROM users WHERE id_group=3 AND dead=0')
    users = await users.fetchall()
    await cursor.close()
    await connect.close()
    users = [user[0] for user in users]
    return users

##  Функция блокировки пользователей для рассылки
async def update_user_dead_status(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    await cursor.execute('UPDATE users SET dead = 1 WHERE user_id=?;', (user_id,))
    await connect.commit()
    await cursor.close()
    await connect.close()

##  Функция записи реферала
async def get_referrer_user_id(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    referrer_id = await cursor.execute('SELECT referrer_id FROM users WHERE user_id=?', (user_id,))
    referrer_id = await referrer_id.fetchone()
    await cursor.close()
    await connect.close()
    return referrer_id

##  Функция проверки реквизитов
async def get_referrer_trc(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    trc_id = await cursor.execute('SELECT COALESCE(trc_id, 0) FROM users WHERE user_id=?', (user_id,))
    trc_id = await trc_id.fetchone()
    await cursor.close()
    await connect.close()
    return trc_id[0]

async def get_referrer_bep(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    bep_id = await cursor.execute('SELECT COALESCE(bep_id, 0) FROM users WHERE user_id=?', (user_id,))
    bep_id = await bep_id.fetchone()
    await cursor.close()
    await connect.close()
    return bep_id[0]

##  Функция проверки суммы реферала для выплаты
async def get_referrer_bounty_sum(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    bounty_sum = await cursor.execute('SELECT COALESCE(bounty_sum, 0) FROM users WHERE user_id=?', (user_id,))
    bounty_sum = await bounty_sum.fetchone()
    await cursor.close()
    await connect.close()
    return bounty_sum[0]

##  Функция получения username
async def get_username_for_bouynt(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    username_bounty = await cursor.execute('SELECT COALESCE(username, 0) FROM users WHERE user_id=?', (user_id,))
    username_bounty = await username_bounty.fetchone()
    await cursor.close()
    await connect.close()
    return username_bounty[0]

## Функции для получения и изменения минимальной выплаты
async def get_min_cashback():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    min_cashback = await cursor.execute('SELECT value_int FROM others WHERE key="min_cashback";')
    min_cashback = await min_cashback.fetchone()
    await cursor.close()
    await connect.close()
    return min_cashback[0]

async def get_bounty_cashback():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    bounty_cashback = await cursor.execute('SELECT value_int FROM others WHERE key="bounty_cashback";')
    bounty_cashback = await bounty_cashback.fetchone()
    await cursor.close()
    await connect.close()
    return bounty_cashback[0]

##  Функиции для редактирования саб-админов
async def get_group_id_subadmin(username):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    subadmin_group_id = await cursor.execute('SELECT id_group FROM users WHERE username= ?;', (username,))
    subadmin_group_id = await subadmin_group_id.fetchone()
    await cursor.close()
    await connect.close()
    if subadmin_group_id is None:
        return None
    return subadmin_group_id[0]

#  Повысить до уровня Саб-админа
async def put_group_id_subadmin(username):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    edit_subadmin = await cursor.execute('UPDATE users SET id_group = 2 WHERE username= ?;', (username,))
    await connect.commit()
    edit_subadmin = await edit_subadmin.fetchone()
    await cursor.close()
    await connect.close()

#  Понизить до уровня пользователя
async def del_groupid_subadmin(username):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    edit_subadmin = await cursor.execute('UPDATE users SET id_group = 3 WHERE username= ?;', (username,))
    await connect.commit()
    edit_subadmin = await edit_subadmin.fetchone()
    await cursor.close()
    await connect.close()

## Получение текущей реферальной ссылки
async def get_link_subadmin(username):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    subadmin_link = await cursor.execute('SELECT link FROM users WHERE username= ?;', (username,))
    subadmin_link = await subadmin_link.fetchone()
    await cursor.close()
    await connect.close()
    if subadmin_link is None:
        return None
    return subadmin_link[0]

##  Изменение реферальной ссылки
async def edit_link_subadmin(subadmin_link, username):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    edit_link = await cursor.execute('UPDATE users SET link = ? WHERE username= ?;', (subadmin_link, username,))
    await connect.commit()
    edit_link = await edit_link.fetchone()
    await cursor.close()
    await connect.close()

####  SUB-ADMIN  ####
##  Получение количества рефералов
async def get_count_referal(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    count_referal = await cursor.execute('SELECT count_ref FROM users WHERE user_id= ?;', (user_id,))
    count_referal = await count_referal.fetchone()
    await cursor.close()
    await connect.close()
    if count_referal is None:
        return None
    return count_referal[0]

async def get_current_cashback(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    current_cashback = await cursor.execute('SELECT bounty_sum FROM users WHERE user_id= ?;', (user_id,))
    current_cashback = await current_cashback.fetchone()
    await cursor.close()
    await connect.close()
    if current_cashback is None:
        return None
    return current_cashback[0]

##  Фиксируем сумму к выплате
async def update_bounty_sum_to_paid(bounty_sum_to_paid, user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    bounty_sum_to_paid = await cursor.execute('UPDATE users SET bounty_sum_to_paid = ? WHERE user_id=?', (bounty_sum_to_paid, user_id,))
    await connect.commit()
    bounty_sum_to_paid = await bounty_sum_to_paid.fetchone()
    await cursor.close()
    await connect.close()

##  
async def get_bounty_sum_to_paid(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    bounty_sum_to_paid = await cursor.execute('SELECT bounty_sum_to_paid FROM users WHERE user_id=?', (user_id,))
    bounty_sum_to_paid = await bounty_sum_to_paid.fetchone()
    await cursor.close()
    await connect.close()
    return bounty_sum_to_paid[0]

##  Проверяем была ли выплата за реферала
async def get_paid_value(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    paid_value = await cursor.execute('SELECT paid FROM users WHERE user_id=?', (user_id,))
    paid_value = await paid_value.fetchone()
    await cursor.close()
    await connect.close()
    return paid_value[0]

##  Изменяем статус на оплочено
async def update_paid_value(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    edit_paid_value = await cursor.execute('UPDATE users SET paid = "yes" WHERE user_id= ?;', (user_id,))
    await connect.commit()
    edit_paid_value = await edit_paid_value.fetchone()
    await cursor.close()
    await connect.close()

##  Получаем и начислаем деньги на баланс рефералу
async def get_bounty_sum(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    paid_value = await cursor.execute('SELECT bounty_sum FROM users WHERE user_id=?', (user_id,))
    paid_value = await paid_value.fetchone()
    await cursor.close()
    await connect.close()
    return paid_value[0]

async def update_bounty_sum_value(paid_sum, user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    edit_paid_sum = await cursor.execute('UPDATE users SET bounty_sum = ? WHERE user_id= ?;', (paid_sum, user_id,))
    await connect.commit()
    edit_paid_sum = await edit_paid_sum.fetchone()
    await cursor.close()
    await connect.close()

####  STATISTIC  ####
##  Получаем кортеж всех саб-админов
async def get_all_admin_count_referal():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    subadmin_users = await cursor.execute('SELECT username FROM users WHERE id_group=2;')
    subadmin_users = await subadmin_users.fetchall()
    await cursor.close()
    await connect.close()
    return subadmin_users

##  Получаем количество приглашенных 
async def get_admin_count_referal(username):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    count_referal = await cursor.execute('SELECT count_ref FROM users WHERE username= ?;', (username,))
    count_referal = await count_referal.fetchone()
    await cursor.close()
    await connect.close()
    if count_referal is None:
        return None
    return count_referal[0]

## Получаем сумму для вывода
async def get_admin_current_cashback(username):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    current_cashback = await cursor.execute('SELECT bounty_sum FROM users WHERE username= ?;', (username,))
    current_cashback = await current_cashback.fetchone()
    await cursor.close()
    await connect.close()
    if current_cashback is None:
        return None
    return current_cashback[0]

##  Просмотр и редактирование сообщений
async def call_message_edit(message_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    text_hello = await cursor.execute('SELECT text FROM msg_kb WHERE id = ?', (message_id, ))
    text_hello = await text_hello.fetchone()
    photo = await cursor.execute('SELECT photo FROM msg_kb WHERE id = ?', (message_id, ))
    photo = await photo.fetchone()
    video = await cursor.execute('SELECT video FROM msg_kb WHERE id = ?', (message_id, ))
    video = await video.fetchone()
    reply_markup_json = await cursor.execute('SELECT reply_markup FROM msg_kb WHERE id = ?', (message_id, ))
    reply_markup_json = await reply_markup_json.fetchone()
    await cursor.close()
    await connect.close()

    # Извлекаем строку из кортежа
    if isinstance(reply_markup_json, tuple):
            reply_markup_json = reply_markup_json[0]

    # Десериализуем клавиатуру из JSON
    reply_markup = None
    if reply_markup_json:
        try:
            reply_markup = types.InlineKeyboardMarkup.model_validate_json(reply_markup_json)
        except Exception as e:
            print(f"Ошибка при десериализации клавиатуры: {e}")
            # Создаем заглушку если не удалось десериализовать
            reply_markup = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="❌ Ошибка загрузки кнопок", callback_data='error')]
            ])

    text_hello = text_hello[0]
    photo = photo[0]
    video = video[0]
    return{
        'text': text_hello,
        'photo': photo,
        'video': video,
        'reply_markup': reply_markup
    }

##  Просмотр и редактирование капчи
async def call_capcha_edit(message_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    text_hello = await cursor.execute('SELECT text FROM capcha_kb WHERE id = ?', (message_id, ))
    text_hello = await text_hello.fetchone()
    photo = await cursor.execute('SELECT photo FROM capcha_kb WHERE id = ?', (message_id, ))
    photo = await photo.fetchone()
    video = await cursor.execute('SELECT video FROM capcha_kb WHERE id = ?', (message_id, ))
    video = await video.fetchone()
    reply_markup_json = await cursor.execute('SELECT button_name FROM capcha_kb WHERE id = ?', (message_id, ))
    reply_markup_json = await reply_markup_json.fetchone()

    await cursor.close()
    await connect.close()

    # Извлекаем строку из кортежа
    if isinstance(reply_markup_json, tuple):
            reply_markup_json = reply_markup_json[0]

    # Десериализуем клавиатуру из JSON
    reply_markup = None
    if reply_markup_json and reply_markup_json != 'NONE':
        try:
            reply_markup = types.ReplyKeyboardMarkup.model_validate_json(reply_markup_json)
        except Exception as e:
            print(f"Ошибка при десериализации клавиатуры: {e}")
            # Создаем заглушку если не удалось десериализовать
            reply_markup = types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text="❌ Ошибка загрузки кнопок")]
                ],
                resize_keyboard=True
            )
    else:
        # Если клавиатуры нет, создаем пустую или стандартную
        reply_markup = types.ReplyKeyboardRemove()  # или можно создать пустую клавиатуру

    text_hello = text_hello[0]
    photo = photo[0]
    video = video[0]
    return{
        'text': text_hello,
        'photo': photo,
        'video': video,
        'reply_markup': reply_markup
    }

##  Получаем время отправки капчи
async def get_capcha_timer():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    capcha_timer = await cursor.execute('SELECT timer FROM capcha_kb WHERE id= 1;')
    capcha_timer = await capcha_timer.fetchone()
    await cursor.close()
    await connect.close()
    if capcha_timer is None:
        return None
    return capcha_timer

##  Получаем время отправки приветок
async def get_privetka_timer():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    privetka_timer = await cursor.execute('SELECT timer FROM msg_kb;')
    privetka_timer = await privetka_timer.fetchall()
    await cursor.close()
    await connect.close()
    if privetka_timer is None:
        return None
    return privetka_timer

####  STATISTIC BD   ####

## Количество всех пользователей
async def get_sum_users():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    users = await cursor.execute('SELECT COUNT(*) FROM users WHERE id_group=3;')
    users = await users.fetchone()
    await cursor.close()
    await connect.close()
    if users is None:
        return None
    return users[0]

## Количество мертвых пользователей
async def get_sum_users_dead():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    dead_users = await cursor.execute('SELECT COUNT(*) FROM users WHERE id_group=3 AND dead=1;')
    dead_users = await dead_users.fetchone()
    await cursor.close()
    await connect.close()
    if dead_users is None:
        return None
    return dead_users[0]

## Количество живых пользователей
async def get_sum_users_alive():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    alive_users = await cursor.execute('SELECT COUNT(*) FROM users WHERE id_group=3 AND dead=0;')
    alive_users = await alive_users.fetchone()
    await cursor.close()
    await connect.close()
    if alive_users is None:
        return None
    return alive_users[0]

## Проставляем статус живого человека
async def update_users_alive(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    await cursor.execute('UPDATE users SET dead = 0 WHERE user_id=?;', (user_id,))
    await connect.commit()
    await cursor.close()
    await connect.close()

## Проставляем статус капча пройдена
async def update_users_capcha(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    await cursor.execute('UPDATE users SET capcha = 1 WHERE user_id=?;', (user_id,))
    await connect.commit()
    await cursor.close()
    await connect.close()

## Количество не пройденных капчу ПО САБАДМИНУ
async def get_sum_users_dead_referal(username):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    dead_users = await cursor.execute('SELECT COUNT(r.user_id) as referral_count FROM users u LEFT JOIN users r ON u.user_id = r.referrer_id AND r.capcha = 1 WHERE u.username = ? GROUP BY u.user_id, u.username;', (username, ))
    dead_users = await dead_users.fetchone()
    await cursor.close()
    await connect.close()
    if dead_users is None:
        return None
    return dead_users[0]

## Количество пройденных капчу ПО САБАДМИНУ
async def get_sum_users_alive_referal(username):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    alive_users = await cursor.execute('SELECT COUNT(r.user_id) as referral_count FROM users u LEFT JOIN users r ON u.user_id = r.referrer_id AND r.capcha = 0 WHERE u.username = ? GROUP BY u.user_id, u.username;', (username, ))
    alive_users = await alive_users.fetchone()
    await cursor.close()
    await connect.close()
    if alive_users is None:
        return None
    return alive_users[0]