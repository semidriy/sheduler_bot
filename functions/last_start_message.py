from aiogram import types
import aiosqlite
from config_data.config import Config, load_config
from aiogram import F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from functions.db_handler import get_bounty_cashback, get_bounty_sum, get_min_cashback, get_paid_value, get_referrer_user_id, update_bounty_sum_value, update_paid_value

config: Config = load_config()
bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

async def last_photo_button():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    photo = await cursor.execute('SELECT photo FROM hello_message WHERE m_number = "last"')
    photo = await photo.fetchone()
    await cursor.close()
    await connect.close()
    return photo

async def second_video_button():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    video = await cursor.execute('SELECT video FROM hello_message WHERE m_number = "last"')
    video = await video.fetchone()
    await cursor.close()
    await connect.close()
    return video

async def last_text_hello():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    text_hello = await cursor.execute('SELECT text FROM hello_message WHERE m_number = "last"')
    text_hello = await text_hello.fetchone()
    await cursor.close()
    await connect.close()
    return text_hello

## todo: сделать одной функцией
async def last_name_button():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    name_button = await cursor.execute('SELECT button FROM hello_message WHERE m_number = "last"')
    name_button = await name_button.fetchone()
    await cursor.close()
    await connect.close()
    return name_button

async def url_button():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    hello_buttom = await cursor.execute('SELECT url FROM hello_message WHERE m_number = "last"')
    hello_buttom = await hello_buttom.fetchone()
    await cursor.close()
    await connect.close()
    return hello_buttom

##  
# Вытащить ссылку по рефералу
async def url_button_referrer(referrer_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    hello_buttom = await cursor.execute('SELECT link FROM users WHERE user_id = ?', (referrer_id,))
    hello_buttom = await hello_buttom.fetchone()
    await cursor.close()
    await connect.close()
    return hello_buttom

# Узнать своего реферала
async def get_my_referrer(user_id):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    referr_id = await cursor.execute('SELECT referrer_id FROM users WHERE user_id = ?', (user_id,))
    referr_id = await referr_id.fetchone()
    await cursor.close()
    await connect.close()
    return referr_id[0]

##

async def call_last_message_start(message: types.Message) -> None:
    text_hello_db = await last_text_hello()
    text_hello_db = text_hello_db[0]
    hello_photo_id = await last_photo_button()
    hello_photo_id = hello_photo_id[0]
    hello_video_id = await second_video_button()
    hello_video_id = hello_video_id[0]
    button_name = await last_name_button()
    button_name = button_name[0]
    # button_url = await url_button()
    referrer_id = await get_my_referrer(message.chat.id)
    print('Прожатие после второй кнопки')
    print(f'Юзер айди - {message.from_user.id}\n'
          f'message.chat.id - {message.chat.id}'
          f'реферер айди - {referrer_id}')
    button_url = await url_button_referrer(referrer_id)
    ##
    button_url = button_url[0]
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=button_name, url=button_url, callback_data='button_clicked')]
    ])
    if hello_photo_id == "NONE":
        await message.answer_video(video=hello_video_id, caption=text_hello_db, reply_markup=kb, parse_mode="MarkdownV2")
    else:
        await message.answer_photo(photo=hello_photo_id, caption=text_hello_db, reply_markup=kb, parse_mode="MarkdownV2")  ##  Проверить HTML парсинг

async def bounty_referr(message: types.Message):
    referrer_id = await get_referrer_user_id(message.chat.id)
    referrer_id = referrer_id[0]
    min_cashback = await get_min_cashback()
    if referrer_id != 0:
        paid_value = await get_paid_value(message.chat.id)
        if paid_value == "no":
            # обновление поля оплаты
            await update_paid_value(message.chat.id)
            # уведомляем реферала
            await bot.send_message(referrer_id, '💰<b>Дзынь</b>💰\n\n'
                                f'<b>+{min_cashback}₽</b> на ваш баланс 💵', parse_mode="HTML")
            # выплачиваем реферафу
            bounty_cashback = await get_bounty_cashback()
            paid_value = await get_bounty_sum(referrer_id)
            paid_value = int(paid_value) + int(bounty_cashback)
            await update_bounty_sum_value(paid_value, referrer_id)
        else:
            pass
    else:
        pass