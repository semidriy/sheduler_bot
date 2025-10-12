from aiogram import types
import aiosqlite
from config_data.config import Config, load_config
from aiogram import F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

config: Config = load_config()
bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

## Добавление пользователя в базу при стартовом сообщении
async def add_user(user_id, full_name, username, referrer_id, message: types.Message):
    connect = await aiosqlite.connect('bot.db')  
    cursor = await connect.cursor()
    check_user = await cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    check_user = await check_user.fetchone()
    if check_user is None:
        start_command =  str(message.text)
        referrer_id = str(start_command[7:])

        if referrer_id != "":
            if str(referrer_id) != str(message.from_user.id):
                await cursor.execute('INSERT INTO users (user_id, full_name, username, referrer_id) VALUES (?, ?, ?, ?)', (user_id, full_name, username, referrer_id))
                await connect.commit()
                # try:
                #     await bot.send_message(referrer_id, "По вашей ссылке зарегистрировались ")
                # except:
                #     pass
            else:
                await bot.send_message(message.from_user.id, '❌ Нельзя регистрироваться по своей ссылке!')
        else:
            await cursor.execute('INSERT INTO users (user_id, full_name, username) VALUES (?, ?, ?)', (user_id, full_name, username))
            await connect.commit()
    else:
        pass
        # await message.answer('Вы уже зарегистрированы')
    await cursor.close()
    await connect.close()

async def first_text_hello():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    text_hello = await cursor.execute('SELECT text FROM msg_kb WHERE id = 1')
    text_hello = await text_hello.fetchone()
    await cursor.close()
    await connect.close()
    return text_hello

async def first_photo_button():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    photo = await cursor.execute('SELECT photo FROM msg_kb WHERE id = 1')
    photo = await photo.fetchone()
    await cursor.close()
    await connect.close()
    return photo

async def first_video_button():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    video = await cursor.execute('SELECT video FROM msg_kb WHERE id = 1')
    video = await video.fetchone()
    await cursor.close()
    await connect.close()
    return video

async def first_name_button():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    name_button = await cursor.execute('SELECT reply_markup FROM msg_kb WHERE id = 1')
    name_button = await name_button.fetchone()
    await cursor.close()
    await connect.close()
    return name_button

async def first_url_button():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    url_button = await cursor.execute('SELECT url FROM msg_kb WHERE id = 1')
    url_button = await url_button.fetchone()
    await cursor.close()
    await connect.close()
    return url_button

async def call_first_start(message: types.Message) -> None:
    ##  Добавляем пользователя в базу, если его там нет
    text_hello_db = await first_text_hello()
    text_hello_db = text_hello_db[0]
    hello_photo_id = await first_photo_button()
    hello_photo_id = hello_photo_id[0]
    hello_video_id = await first_video_button()
    hello_video_id = hello_video_id[0]
    button_name = await first_name_button()
    button_name = button_name[0]
    button_url = await first_url_button()
    button_url = button_url[0]
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=button_name, url=button_url)]
    ])
    if hello_photo_id == 'NONE':
        await message.answer_video(video=hello_video_id, caption=text_hello_db, reply_markup=kb, parse_mode="MarkdownV2")
    else:
        await message.answer_photo(photo=hello_photo_id, caption=text_hello_db, reply_markup=kb, parse_mode="MarkdownV2")  ##  Проверить HTML парсинг

