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
    text_hello = await cursor.execute('SELECT text FROM capcha_kb WHERE id = 1')
    text_hello = await text_hello.fetchone()
    await cursor.close()
    await connect.close()
    return text_hello

async def first_photo_button():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    photo = await cursor.execute('SELECT photo FROM capcha_kb WHERE id = 1')
    photo = await photo.fetchone()
    await cursor.close()
    await connect.close()
    return photo

async def first_video_button():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    video = await cursor.execute('SELECT video FROM capcha_kb WHERE id = 1')
    video = await video.fetchone()
    await cursor.close()
    await connect.close()
    return video

async def first_name_button():
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    name_button = await cursor.execute('SELECT button_name FROM capcha_kb WHERE id = 1')
    name_button = await name_button.fetchone()
    await cursor.close()
    await connect.close()
    return name_button

async def call_first_start(message: types.Message) -> None:
    text_hello_db = await first_text_hello()
    text_hello_db = text_hello_db[0]
    hello_photo_id = await first_photo_button()
    hello_photo_id = hello_photo_id[0]
    hello_video_id = await first_video_button()
    hello_video_id = hello_video_id[0]
    button_name = await first_name_button()
    button_name = button_name[0]

    # Преобразуем JSON строку в объект клавиатуры
    import json
    try:
        keyboard_dict = json.loads(button_name)
        
        # Создаем клавиатуру вручную из словаря
        keyboard = keyboard_dict.get("keyboard", [])
        keyboard_buttons = []
        
        for row in keyboard:
            button_row = []
            for button_data in row:
                # Создаем кнопку с текстом
                button = types.KeyboardButton(text=button_data.get("text", ""))
                button_row.append(button)
            keyboard_buttons.append(button_row)
        
        # Создаем объект клавиатуры с параметрами из JSON
        reply_markup = types.ReplyKeyboardMarkup(
            keyboard=keyboard_buttons,
            resize_keyboard=keyboard_dict.get("resize_keyboard", True),
            one_time_keyboard=keyboard_dict.get("one_time_keyboard", True),
            is_persistent=keyboard_dict.get("is_persistent"),
            input_field_placeholder=keyboard_dict.get("input_field_placeholder"),
            selective=keyboard_dict.get("selective")
        )
        
    except json.JSONDecodeError as e:
        # Если возникла ошибка парсинга JSON, создаем клавиатуру по умолчанию
        print(f"Ошибка парсинга JSON: {e}")
        reply_markup = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Shabbat")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    has_photo = hello_photo_id and hello_photo_id != 'NONE'
    has_video = hello_video_id and hello_video_id != 'NONE'
    
    if has_photo:
        await message.answer_photo(photo=hello_photo_id, caption=text_hello_db, reply_markup=reply_markup, parse_mode="MarkdownV2")
    elif has_video:
        await message.answer_video(video=hello_video_id, caption=text_hello_db, reply_markup=reply_markup, parse_mode="MarkdownV2")
    else:
        await message.answer(text=text_hello_db, reply_markup=reply_markup, parse_mode="MarkdownV2")
