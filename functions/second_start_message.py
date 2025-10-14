# from aiogram import types
# import aiosqlite
# from config_data.config import Config, load_config
# from aiogram import F, Bot
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode

# config: Config = load_config()
# bot = Bot(
#         token=config.tg_bot.token,
#         default=DefaultBotProperties(parse_mode=ParseMode.HTML)
#     )

# async def second_text_hello():
#     connect = await aiosqlite.connect('bot.db')
#     cursor = await connect.cursor()
#     text_hello = await cursor.execute('SELECT text FROM hello_message WHERE m_number = 2')
#     text_hello = await text_hello.fetchone()
#     await cursor.close()
#     await connect.close()
#     return text_hello

# async def second_photo_button():
#     connect = await aiosqlite.connect('bot.db')
#     cursor = await connect.cursor()
#     photo = await cursor.execute('SELECT photo FROM hello_message WHERE m_number = 2')
#     photo = await photo.fetchone()
#     await cursor.close()
#     await connect.close()
#     return photo

# async def second_video_button():
#     connect = await aiosqlite.connect('bot.db')
#     cursor = await connect.cursor()
#     video = await cursor.execute('SELECT video FROM hello_message WHERE m_number = 2')
#     video = await video.fetchone()
#     await cursor.close()
#     await connect.close()
#     return video

# async def second_name_button():
#     connect = await aiosqlite.connect('bot.db')
#     cursor = await connect.cursor()
#     name_button = await cursor.execute('SELECT button FROM hello_message WHERE m_number = 2')
#     name_button = await name_button.fetchone()
#     await cursor.close()
#     await connect.close()
#     return name_button

# async def call_second_start(message: types.Message) -> None:
#     text_hello_db = await second_text_hello()
#     text_hello_db = text_hello_db[0]
#     hello_photo_id = await second_photo_button()
#     hello_photo_id = hello_photo_id[0]
#     hello_video_id = await second_video_button()
#     hello_video_id = hello_video_id[0]
#     button_name = await second_name_button()
#     button_name = button_name[0]

#     kb = types.InlineKeyboardMarkup(inline_keyboard=[
#         [types.InlineKeyboardButton(text=button_name, callback_data='handler_last_message')]
#     ])
#     if hello_photo_id == "NONE":
#         await message.answer_video(video=hello_video_id, caption=text_hello_db, reply_markup=kb, parse_mode="MarkdownV2")
#     else:
#         await message.answer_photo(photo=hello_photo_id, caption=text_hello_db, reply_markup=kb, parse_mode="MarkdownV2")  ##  Проверить HTML парсинг
