from aiogram import types, F, Router
from aiogram.types import CallbackQuery
import aiosqlite
import json

from functions.db_handler import call_capcha_edit, get_capcha_timer, get_privetka_timer
import keyboards.admin_message_kb as kb
# from keyboards.subadm_kb import get_simple_keyboard
from state_fsm.fsm import AdminState
from aiogram.fsm.context import FSMContext
from keyboards.admin_kb import button_back_to_capcha

router = Router()

kb_button_back_to_capcha = types.InlineKeyboardMarkup(inline_keyboard=button_back_to_capcha)

@router.callback_query(F.data == 'capcha_message')
async def message_git(query: types.CallbackQuery):
    await query.message.edit_text('🔞 Меню капчи', reply_markup=await kb.reply_menu_capcha())

##  Удаление сообщений
@router.callback_query(lambda c: c.data and c.data.startswith('capcha_delete_') and c.data[14:].isdigit())
async def delete_message_handler(callback: CallbackQuery):
    try:
        message_id = int(callback.data[14:])  # Берем все после "capcha_delete_"
        
        # Остальной код удаления...
        connect = await aiosqlite.connect('bot.db')
        cursor = await connect.cursor()
        
        await cursor.execute('DELETE FROM capcha_kb WHERE id = ?', (message_id,))
        await connect.commit()
        
        await cursor.close()
        await connect.close()
        
        await callback.message.edit_reply_markup(
            reply_markup=await kb.reply_menu_capcha()
        )
        
    except Exception as e:
        await callback.answer(f"Ошибка при удалении: {e}", show_alert=True)

## Просмотр сообщений
@router.callback_query(lambda c: c.data and c.data.startswith('capcha_message_') and c.data[15:].isdigit())
async def edit_message_handler_capcha(query: types.CallbackQuery):
    try:
        message_id = int(query.data[15:])
        await query.message.answer(f'🔞 Вы смотрите {message_id}-ую капчу')
        msg_data = await call_capcha_edit(message_id)

        if msg_data['video'] and msg_data['video'] != 'NONE':
            await query.message.answer_video(
                video=msg_data['video'], 
                caption=msg_data['text'],
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await query.message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(message_id))
        elif msg_data['photo'] and msg_data['photo'] != 'NONE':
            await query.message.answer_photo(
                photo=msg_data['photo'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await query.message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(message_id))
        else:
        # Если нет ни фото, ни видео
            await query.message.answer(
                text=msg_data['text'],
                reply_markup=msg_data['reply_markup'],
                parse_mode="MarkdownV2"
            )
            await query.message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(message_id))
    except Exception as e:
        print(f"Capcha.edit_message_handler_capcha| Ошибка при просмотре: {e}")

##  Редактируем медиа
@router.callback_query(lambda c: c.data and c.data.startswith('capcha_edit_media_') and c.data[18].isdigit())
async def edit_message_handler(query: types.CallbackQuery, state: FSMContext):
    message_id = int(query.data[18:])
    await query.message.answer('🔞🏞️ Отправь мне фото или видео(гифку)\n\n' \
                               '⚠️ Можешь так же прислать мне пост ,я сам заберу медиа файл\n\n' \
                               'Или вернитесь назад', reply_markup=kb_button_back_to_capcha)
    await state.update_data(message_id=message_id)
    await state.set_state(AdminState.fsm_capcha_media)

@router.message(AdminState.fsm_capcha_media)
async def process_media_put(message: types.Message, state: FSMContext):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    data = await state.get_data()
    message_id = data.get('message_id')
    if message.photo:
        photo_id = message.photo[-1].file_id
        put_photo = await cursor.execute('UPDATE capcha_kb SET photo = ? WHERE id=?', (photo_id,message_id,))
        clear_video = await cursor.execute('UPDATE capcha_kb SET video = "NONE" WHERE id=?', (message_id,))
        await connect.commit()
        put_photo = await put_photo.fetchone()
        clear_video = await clear_video.fetchone()
    elif message.video:
        video_id = message.video.file_id
        put_video = await cursor.execute('UPDATE capcha_kb SET video = ? WHERE id=?', (video_id,message_id))
        clear_photo = await cursor.execute('UPDATE capcha_kb SET photo = "NONE" WHERE id=?', (message_id,))
        await connect.commit()
        put_photo = await put_video.fetchone()
        clear_photo = await clear_photo.fetchone()
    else:
        await message.answer('🔞❌ Ошибка!\n\n' \
                             '🏞️ Пришли фото или видео\n\n' \
                             'Или вернитесь назад', reply_markup=kb_button_back_to_capcha)
    await cursor.close()
    await connect.close()
    await message.answer(f'✅🔞 Медиа CAPCHA {message_id}-ого сообщения изменено\n\n')
    await state.clear()
    msg_data = await call_capcha_edit(message_id)
    try:
        await message.answer(f'Вы смотрите {message_id}-ое сообщение')
        if msg_data['video'] and msg_data['video'] != 'NONE':
            await message.answer_video(
                video=msg_data['video'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(message_id))
        elif msg_data['photo'] and msg_data['photo'] != 'NONE':
            await message.answer_photo(
                photo=msg_data['photo'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(message_id))
    except Exception as e:
        await message.answer(f"Ошибка при просмотре: {e}", show_alert=True)

##  Редактируем текст
@router.callback_query(lambda c: c.data and c.data.startswith('capcha_edit_text_') and c.data[17].isdigit())
async def edit_message_handler(query: types.CallbackQuery, state: FSMContext):
    message_id = int(query.data[17:])
    await query.message.answer('🔞💬 Введите текст\n\n' \
                               '⚠️ Можешь так же прислать мне пост ,я сам заберу текст\n\n' \
                               '⚠️ Чтобы убрать подпись(пусто) - отправь любую картинку\n\n' \
                               'Или вернитесь назад', reply_markup=kb_button_back_to_capcha)
    await state.update_data(message_id=message_id)
    await state.set_state(AdminState.fsm_capcha_text)

@router.message(AdminState.fsm_capcha_text)
async def edit_hello_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    if message.md_text:
        new_text = message.md_text
    else:
        new_text = message.caption
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    hello_text = await cursor.execute('UPDATE capcha_kb SET text = ? WHERE id=?', (new_text, message_id,))
    await connect.commit()
    hello_text = await hello_text.fetchone()
    await cursor.close()
    await connect.close()
    await message.answer(f'🔞✅ Текст CAPCHA {message_id}-ого сообщение изменен\n\n')
    await state.clear()
    msg_data = await call_capcha_edit(message_id)
    try:
        await message.answer(f'Вы смотрите {message_id}-ое сообщение')
        if msg_data['video'] and msg_data['video'] != 'NONE':
            await message.answer_video(
                video=msg_data['video'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(message_id))
        elif msg_data['photo'] and msg_data['photo'] != 'NONE':
            await message.answer_photo(
                photo=msg_data['photo'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(message_id))
    except Exception as e:
        await message.answer(f"Ошибка при просмотре: {e}", show_alert=True)

##  Редактируем кнопку
@router.callback_query(lambda c: c.data and c.data.startswith('capcha_edit_button_') and c.data[19].isdigit())
async def edit_message_handler(query: types.CallbackQuery, state: FSMContext):
    message_id = int(query.data[19:])
    await query.message.answer('🔞🔘 Отправьте боту список URL-кнопок в следующем формате👇:\n' \
                               'Кнопка 1\n'
                               'Кнопка 2\n\n'
                               'Или вернитесь назад', reply_markup=kb_button_back_to_capcha)
    await state.update_data(message_id=message_id)
    await state.set_state(AdminState.fsm_capcha_button)

@router.message(AdminState.fsm_capcha_button)
async def process_capcha_buttons(message: types.Message, state: FSMContext):
    try:
        # Получаем данные из состояния
        state_data = await state.get_data()
        message_id = state_data.get('message_id')
        # Парсим текст с кнопками
        button_lines = message.text.strip().split('\n')
        keyboard = []
        
        for line in button_lines:
            line = line.strip()
            if not line:
                continue
            
            # Добавляем кнопку в клавиатуру
            keyboard.append([types.KeyboardButton(text=line)])
        
        # Создаем клавиатуру
        reply_markup = types.ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        reply_markup_json = reply_markup.model_dump_json()

        connect = await aiosqlite.connect('bot.db')
        cursor = await connect.cursor()
        await cursor.execute('UPDATE capcha_kb SET button_name = ? WHERE id=?', (reply_markup_json, message_id, ))
        await connect.commit()
        await cursor.close()
        await connect.close()
        await message.answer(f"🔞✅ Кнопка CAPCHA {message_id}-ого сообщения изменена: \n\n")
        await state.clear()
        msg_data = await call_capcha_edit(message_id)

        try:
            await message.answer(f'Вы смотрите {message_id}-ое сообщение')
            if msg_data['video'] and msg_data['video'] != 'NONE':
                await message.answer_video(
                    video=msg_data['video'], 
                    caption=msg_data['text'], 
                    reply_markup=reply_markup, 
                    parse_mode="MarkdownV2"
                )
                await message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(message_id))
            elif msg_data['photo'] and msg_data['photo'] != 'NONE':
                await message.answer_photo(
                    photo=msg_data['photo'], 
                    caption=msg_data['text'], 
                    reply_markup=reply_markup, 
                    parse_mode="MarkdownV2"
                )
                await message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(message_id))
            else:
                await message.answer(
                text=msg_data.get('text', ''),
                reply_markup=reply_markup,
                parse_mode="MarkdownV2"
            )
        except Exception as e:
            print(f"Capcha.process_capcha_buttons| Произошла ошибка: {str(e)}")
    except Exception as e:
        print(f"Capcha.process_capcha_buttons| Произошла ошибка: {str(e)}")

##  Редактируем таймер для сообщений
@router.callback_query(lambda c: c.data and c.data.startswith('capcha_timer_') and c.data[13].isdigit())
async def edit_message_handler(query: types.CallbackQuery, state: FSMContext):
    message_id = int(query.data[13:])
    await query.message.answer('⏱️ Отправь значение времени в секундах для СПАМА КАПЧИ\n\n' \
                               'Или вернитесь назад', reply_markup=kb_button_back_to_capcha)
    await state.update_data(message_id=message_id)
    await state.set_state(AdminState.fms_capcha_timer)

@router.message(AdminState.fms_capcha_timer)
async def process_media_put(message: types.Message, state: FSMContext):
    ##  Получаем время капчи и сравниваем, чтобы работало корректно
    capcha_timer = await get_capcha_timer()
    privetka_timer = await get_privetka_timer()
    timer_values = [item[0] for item in privetka_timer]
    if int(capcha_timer[0]) == int(message.text) or int(message.text) in timer_values:
        await message.answer(f'❌ Данное время уже установлено для CAPCHA({capcha_timer[0]}s) или приветки({timer_values}s)\n' \
                             '👀 Введите новое время')
    else:
        connect = await aiosqlite.connect('bot.db')
        cursor = await connect.cursor()
        data = await state.get_data()
        message_id = data.get('message_id')
        new_timer = message.text
        connect = await aiosqlite.connect('bot.db')
        cursor = await connect.cursor()
        process_timer_put = await cursor.execute('UPDATE capcha_kb SET timer = ? WHERE id=?', (new_timer, message_id, ))
        await connect.commit()
        process_timer_put = await process_timer_put.fetchone()
        await cursor.close()
        await connect.close()
        await message.answer(f"🔞✅ СПАМЕР КАПЧА для  {message_id}-ого приветственного сообщения изменен\n"
                         f"Текущее значение {new_timer} секунд\n\n"
                         '⚙️ Меню сообщений', reply_markup=await kb.reply_menu_capcha())
        await state.clear()

##  Добавление целого поста
@router.callback_query(F.data == 'capcha_add_message')
async def add_new_message_for_user(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_text('🔞📳 Пришли мне текст и медиа:\n\n' \
                               'Или вернитесь назад', reply_markup=kb_button_back_to_capcha)
    await state.set_state(AdminState.fsm_new_capcha)

@router.message(AdminState.fsm_new_capcha)
async def edit_hello_text(message: types.Message, state: FSMContext):
    try:
        # Подготовка данных сообщения
        has_valid_content = (
            message.md_text or  # просто текст
            (message.photo and message.caption) or  # фото с подписью
            (message.video and message.caption)  # видео с подписью
        )

        if not has_valid_content:
            await message.answer('❌ Ошибка!\n\n' \
                         'Нет картинки и текста, или видео и текста или текста\n\n' \
                         'Отправь еще раз', reply_markup=kb_button_back_to_capcha)
    except Exception as e:
        await message.answer(f"Capcha.edit_hello_text| Произошла ошибка при сохранении: {str(e)}")
        print(f"Capcha.edit_hello_text| Произошла ошибка при сохранении: {str(e)}")

    message_data = {
        'text' : message.md_text if message.photo or message.video else message.md_text,
        'photo': message.photo[-1].file_id if message.photo else None,
        'video': message.video.file_id if message.video else None,
    }
    ##  блок записи в БД
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    current_id = await cursor.execute('SELECT max(id) FROM capcha_kb')
    current_id = await cursor.fetchone()
    if current_id is None or current_id[0] is None:
        current_id = 1
    else:
        current_id = int(current_id[0]) + 1
    if message.photo:
        put_photo = await cursor.execute('''
            INSERT INTO capcha_kb (id, text, photo)
            VALUES (?, ?, ?)                 
            ''', (current_id, message_data['text'], message_data['photo']))
        await connect.commit()
        put_photo = await put_photo.fetchone()
    elif message.video:
        put_photo = await cursor.execute('''
            INSERT INTO capcha_kb (id, text, video)
            VALUES (?, ?, ?)                 
            ''', (current_id, message_data['text'], message_data['video']))
        await connect.commit()
        put_photo = await put_photo.fetchone()
    elif message.md_text:
        put_photo = await cursor.execute('''
            INSERT INTO capcha_kb (id, text)
            VALUES (?, ?)
            ''', (current_id, message_data['text']))
        await connect.commit()
        put_photo = await put_photo.fetchone()
    await state.clear()
    await message.answer('👀 Введите название кнопки')
    await state.set_state(AdminState.fsm_capcha_button_name)

##  Добавляем кнопку
@router.message(AdminState.fsm_capcha_button_name)
async def add_button_privetka(message: types.Message, state: FSMContext):
    button_lines = message.text.strip().split('\n')
    keyboard = []
    
    for line in button_lines:
        line = line.strip()
        if not line:
            continue
            
        # Добавляем кнопку в клавиатуру
        keyboard.append([types.KeyboardButton(text=line)])
        
    # Создаем клавиатуру
    reply_markup = types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    reply_markup_json = reply_markup.model_dump_json()

    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    current_id = await cursor.execute('SELECT max(id) FROM capcha_kb')
    current_id = await cursor.fetchone()
    await cursor.execute('UPDATE capcha_kb SET button_name = ? WHERE id=?', (reply_markup_json, current_id[0], ))
    await connect.commit()
    await cursor.close()
    await connect.close()
    await message.answer(f"🔞✅ Кнопка CAPCHA {current_id[0]}-ого сообщения изменена: \n\n")
    await state.clear()
    msg_data = await call_capcha_edit(current_id[0])

    try:
        await message.answer(f'Вы смотрите {current_id[0]}-ое сообщение')
        if msg_data['video'] and msg_data['video'] != 'NONE':
            await message.answer_video(
                video=msg_data['video'], 
                caption=msg_data['text'], 
                reply_markup=reply_markup, 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(current_id[0]))
        elif msg_data['photo'] and msg_data['photo'] != 'NONE':
            await message.answer_photo(
                photo=msg_data['photo'], 
                caption=msg_data['text'], 
                reply_markup=reply_markup, 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(current_id[0]))
        else:
            await message.answer(
            text=msg_data.get('text', ''),
            reply_markup=reply_markup,
            parse_mode="MarkdownV2"
            )
            await message.answer('⚙️🔞 Вы редактируете CAPCHA', reply_markup=await kb.capcha_edit_menu(current_id[0]))
    except Exception as e:
        print(f"Capcha.add_button_privetka| Произошла ошибка: {str(e)}")