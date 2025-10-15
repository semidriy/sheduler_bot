from aiogram import types, F, Router
from aiogram.types import CallbackQuery
import aiosqlite
import json

from functions.db_handler import call_message_edit
import keyboards.admin_message_kb as kb
from state_fsm.fsm import AdminState
from aiogram.fsm.context import FSMContext
from keyboards.admin_kb import button_back_to_privetka

router = Router()

kb_button_back_to_privetka = types.InlineKeyboardMarkup(inline_keyboard=button_back_to_privetka)

@router.callback_query(F.data == 'admin_hello_message')
async def message_git(query: types.CallbackQuery):
    await query.message.edit_text('⚙️ Меню приветки', reply_markup=await kb.reply_menu())

##  Удаление сообщений
@router.callback_query(lambda c: c.data and c.data.startswith('delete_') and c.data[7:].isdigit())
async def delete_message_handler(callback: CallbackQuery):
    try:
        message_id = int(callback.data[7:])  # Берем все после "delete_"
        
        # Остальной код удаления...
        connect = await aiosqlite.connect('bot.db')
        cursor = await connect.cursor()
        
        await cursor.execute('DELETE FROM msg_kb WHERE id = ?', (message_id,))
        await connect.commit()
        
        await cursor.close()
        await connect.close()
        
        await callback.message.edit_reply_markup(
            reply_markup=await kb.reply_menu()
        )
        
    except Exception as e:
        await callback.answer(f"Ошибка при удалении: {e}", show_alert=True)



## Просмотр сообщений
@router.callback_query(lambda c: c.data and c.data.startswith('message_') and c.data[8:].isdigit())
async def edit_message_handler(query: types.CallbackQuery):
    try:
        message_id = int(query.data[8:])
        await query.message.answer(f'Вы смотрите {message_id}-ое сообщение')
        msg_data = await call_message_edit(message_id)
        if msg_data['video'] and msg_data['video'] != 'NONE':
            await query.message.answer_video(
                video=msg_data['video'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await query.message.answer('⚙️ Что хотели бы отредактировать?', reply_markup=await kb.edit_menu(message_id))
        elif msg_data['photo'] and msg_data['photo'] != 'NONE':
            await query.message.answer_photo(
                photo=msg_data['photo'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await query.message.answer('⚙️ Что хотели бы отредактировать?', reply_markup=await kb.edit_menu(message_id))
    except Exception as e:
        await query.message.answer(f"Ошибка при просмотре: {e}", show_alert=True)

##  Редактируем медиа
@router.callback_query(lambda c: c.data and c.data.startswith('edit_media_') and c.data[11].isdigit())
async def edit_message_handler(query: types.CallbackQuery, state: FSMContext):
    message_id = int(query.data[11:])
    await query.message.answer('🏞️ Отправь мне фото или видео(гифку)\n\n' \
                               '⚠️ Можешь так же прислать мне пост ,я сам заберу медиа файл\n\n' \
                               'Или вернитесь назад', reply_markup=kb_button_back_to_privetka)
    await state.update_data(message_id=message_id)
    await state.set_state(AdminState.fms_message_media)

@router.message(AdminState.fms_message_media)
async def process_media_put(message: types.Message, state: FSMContext):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    data = await state.get_data()
    message_id = data.get('message_id')
    if message.photo:
        photo_id = message.photo[-1].file_id
        put_photo = await cursor.execute('UPDATE msg_kb SET photo = ? WHERE id=?', (photo_id,message_id,))
        clear_video = await cursor.execute('UPDATE msg_kb SET video = "NONE" WHERE id=?', (message_id,))
        await connect.commit()
        put_photo = await put_photo.fetchone()
        clear_video = await clear_video.fetchone()
    elif message.video:
        video_id = message.video.file_id
        put_video = await cursor.execute('UPDATE msg_kb SET video = ? WHERE id=?', (video_id,message_id))
        clear_photo = await cursor.execute('UPDATE msg_kb SET photo = "NONE" WHERE id=?', (message_id,))
        await connect.commit()
        put_photo = await put_video.fetchone()
        clear_photo = await clear_photo.fetchone()
    else:
        await message.answer('❌ Ошибка!\n\n' \
                             '🏞️ Пришли фото или видео\n\n' \
                             'Или вернитесь назад', reply_markup=kb_button_back_to_privetka)
    await cursor.close()
    await connect.close()
    await message.answer(f'✅ Медиа {message_id}-ого приветственного сообщения изменено\n\n')
    await state.clear()
    msg_data = await call_message_edit(message_id)
    try:
        await message.answer(f'Вы смотрите {message_id}-ое сообщение')
        msg_data = await call_message_edit(message_id)
        if msg_data['video'] and msg_data['video'] != 'NONE':
            await message.answer_video(
                video=msg_data['video'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️ Что хотели бы отредактировать?', reply_markup=await kb.edit_menu(message_id))
        elif msg_data['photo'] and msg_data['photo'] != 'NONE':
            await message.answer_photo(
                photo=msg_data['photo'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️ Что хотели бы отредактировать?', reply_markup=await kb.edit_menu(message_id))
    except Exception as e:
        await message.answer(f"Ошибка при просмотре: {e}", show_alert=True)

##  Редактируем текст
@router.callback_query(lambda c: c.data and c.data.startswith('edit_text_') and c.data[10].isdigit())
async def edit_message_handler(query: types.CallbackQuery, state: FSMContext):
    message_id = int(query.data[10:])
    await query.message.answer('💬 Введите текст\n\n' \
                               '⚠️ Можешь так же прислать мне пост ,я сам заберу текст\n\n' \
                               '⚠️ Чтобы убрать подпись(пусто) - отправь любую картинку\n\n' \
                               'Или вернитесь назад', reply_markup=kb_button_back_to_privetka)
    await state.update_data(message_id=message_id)
    await state.set_state(AdminState.fms_message_text)

@router.message(AdminState.fms_message_text)
async def edit_hello_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    if message.md_text:
        new_text = message.md_text
    else:
        new_text = message.caption
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    hello_text = await cursor.execute('UPDATE msg_kb SET text = ? WHERE id=?', (new_text, message_id,))
    await connect.commit()
    hello_text = await hello_text.fetchone()
    await cursor.close()
    await connect.close()
    await message.answer(f'✅ Текст {message_id}-ого приветственного сообщение изменен\n\n')
    await state.clear()
    msg_data = await call_message_edit(message_id)
    try:
        await message.answer(f'Вы смотрите {message_id}-ое сообщение')
        msg_data = await call_message_edit(message_id)
        if msg_data['video'] and msg_data['video'] != 'NONE':
            await message.answer_video(
                video=msg_data['video'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️ Что хотели бы отредактировать?', reply_markup=await kb.edit_menu(message_id))
        elif msg_data['photo'] and msg_data['photo'] != 'NONE':
            await message.answer_photo(
                photo=msg_data['photo'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️ Что хотели бы отредактировать?', reply_markup=await kb.edit_menu(message_id))
    except Exception as e:
        await message.answer(f"Ошибка при просмотре: {e}", show_alert=True)

##  Редактируем название кнопки
@router.callback_query(lambda c: c.data and c.data.startswith('edit_button_name_') and c.data[17].isdigit())
async def edit_message_handler(query: types.CallbackQuery, state: FSMContext):
    message_id = int(query.data[17:])
    await query.message.answer('📍 Введи название кнопки:\n' \
                               'Или вернитесь назад', reply_markup=kb_button_back_to_privetka)
    await state.update_data(message_id=message_id)
    await state.set_state(AdminState.fsm_message_button_name)

@router.message(AdminState.fsm_message_button_name)
async def process_button_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    if not message.text:
        await message.answer('❌ Сообщение должно содержать только текст!\n\n' \
                             '📌 Пришли пожалуйста название кнопки\n\n' \
                             'Или вернитесь назад', reply_markup=kb_button_back_to_privetka)
        return
    new_name_button = message.md_text
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    hello_buttom = await cursor.execute('UPDATE msg_kb SET reply_markup = ? WHERE id=?', (new_name_button, message_id, ))
    await connect.commit()
    hello_buttom = await hello_buttom.fetchone()
    await cursor.close()
    await connect.close()
    await message.answer(f"✅ Название кнопки {message_id}-ого приветственного сообщения изменено на: \n\n")
    await state.clear()
    msg_data = await call_message_edit(message_id)
    try:
        await message.answer(f'Вы смотрите {message_id}-ое сообщение')
        msg_data = await call_message_edit(message_id)
        if msg_data['video'] and msg_data['video'] != 'NONE':
            await message.answer_video(
                video=msg_data['video'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️ Что хотели бы отредактировать?', reply_markup=await kb.edit_menu(message_id))
        elif msg_data['photo'] and msg_data['photo'] != 'NONE':
            await message.answer_photo(
                photo=msg_data['photo'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️ Что хотели бы отредактировать?', reply_markup=await kb.edit_menu(message_id))
    except Exception as e:
        await message.answer(f"Ошибка при просмотре: {e}", show_alert=True)

##  Редактиуем ссылку
@router.callback_query(lambda c: c.data and c.data.startswith('edit_url_') and c.data[9].isdigit())
async def edit_message_handler(query: types.CallbackQuery, state: FSMContext):
    message_id = int(query.data[9:])
    await query.message.answer('🔗 Введи ссылку для кнопки:\n' \
                               'Или вернитесь назад', reply_markup=kb_button_back_to_privetka)
    await state.update_data(message_id=message_id)
    await state.set_state(AdminState.fsm_url_button_name)

@router.message(AdminState.fsm_url_button_name)
async def process_button_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    button_url = message.text.strip()
# Проверяем, что URL начинается с http:// или https://
    if not (button_url.startswith('http://') or button_url.startswith('https://')):
        await message.answer(
        '❌ URL должен начинаться с http:// или https://\n'
        'Введите URL повторно или вернитесь назад\n\n'
        'Или вернитесь назад', 
        reply_markup=kb_button_back_to_privetka
        )
        return  # Прерываем выполнение функции
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    procces_button_url = await cursor.execute('UPDATE msg_kb SET url = ? WHERE id=?', (button_url, message_id, ))
    await connect.commit()
    procces_button_url = await procces_button_url.fetchone()
    await cursor.close()
    await connect.close()
    await message.answer(f'✅ Название кнопки {message_id}-ого приветственного сообщения изменено')
    await state.clear()
    msg_data = await call_message_edit(message_id)
    try:
        await message.answer(f'Вы смотрите {message_id}-ое сообщение')
        msg_data = await call_message_edit(message_id)
        if msg_data['video'] and msg_data['video'] != 'NONE':
            await message.answer_video(
                video=msg_data['video'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️ Что хотели бы отредактировать?', reply_markup=await kb.edit_menu(message_id))
        elif msg_data['photo'] and msg_data['photo'] != 'NONE':
            await message.answer_photo(
                photo=msg_data['photo'], 
                caption=msg_data['text'], 
                reply_markup=msg_data['reply_markup'], 
                parse_mode="MarkdownV2"
            )
            await message.answer('⚙️ Что хотели бы отредактировать?', reply_markup=await kb.edit_menu(message_id))
    except Exception as e:
        await message.answer(f"Ошибка при просмотре: {e}", show_alert=True)

##  Редактируем таймер для сообщений
@router.callback_query(lambda c: c.data and c.data.startswith('timer_') and c.data[6].isdigit())
async def edit_message_handler(query: types.CallbackQuery, state: FSMContext):
    message_id = int(query.data[6:])
    await query.message.answer('⏱️ Отправь значение времени в секундах\n\n' \
                               '⚠️ Внимание, отсчет происходит от первого прожатия /start пользователем\n\n' \
                               'Или вернитесь назад', reply_markup=kb_button_back_to_privetka)
    await state.update_data(message_id=message_id)
    await state.set_state(AdminState.fms_message_timer)

@router.message(AdminState.fms_message_timer)
async def process_media_put(message: types.Message, state: FSMContext):
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    data = await state.get_data()
    message_id = data.get('message_id')
    new_timer = message.text
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    process_timer_put = await cursor.execute('UPDATE msg_kb SET timer = ? WHERE id=?', (new_timer, message_id, ))
    await connect.commit()
    process_timer_put = await process_timer_put.fetchone()
    await cursor.close()
    await connect.close()
    await message.answer(f"✅ Таймер для  {message_id}-ого приветственного сообщения изменен\n"
                         f"Текущее значение {new_timer} секунд\n\n"
                         '⚙️ Меню сообщений', reply_markup=await kb.reply_menu())
    await state.clear()
    

##  Добавление целого поста
@router.callback_query(F.data == 'add_message')
async def add_new_message_for_user(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_text('📳 Пришли мне целый пост:\n\n' \
                               'Или вернитесь назад', reply_markup=kb_button_back_to_privetka)
    await state.set_state(AdminState.fsm_new_post)

@router.message(AdminState.fsm_new_post)
async def edit_hello_text(message: types.Message, state: FSMContext):
    try:
        # Подготовка данных сообщения
        if not message.reply_markup:
            await message.answer('❌ Ошибка!\n\n' \
                                 'Пост не содержит кнопку\n\n' \
                                 '📝 Пришли целый пост', reply_markup=kb_button_back_to_privetka)
            return
        else:
            markup_data = json.loads(message.reply_markup.model_dump_json())
            text_button = markup_data['inline_keyboard'][0][0]['text']
            url_button = markup_data['inline_keyboard'][0][0]['url']
    except Exception as e:
        await message.answer(f"Произошла ошибка при сохранении: {str(e)}")
        print(f"Произошла ошибка при сохранении: {str(e)}")

    message_data = {
        'text' : message.md_text if message.photo or message.video else None,
        'photo': message.photo[-1].file_id if message.photo else None,
        'video': message.video.file_id if message.video else None,
        'reply_markup': text_button if message.reply_markup else None,
        'url': url_button if message.reply_markup else None
    }
    # ##  блок записи в БД
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    current_id = await cursor.execute('SELECT max(id) FROM msg_kb')
    current_id = await cursor.fetchone()
    if current_id is None or current_id[0] is None:
        current_id = 1
    else:
        current_id = int(current_id[0]) + 1
    if message.photo:
        put_photo = await cursor.execute('''
            INSERT INTO msg_kb (id, text, photo, reply_markup, url)
            VALUES (?, ?, ?, ?, ?)                 
            ''', (current_id, message_data['text'], message_data['photo'], message_data['reply_markup'], message_data['url']))
        await connect.commit()
        put_photo = await put_photo.fetchone()
        await message.answer('✅ Пост успешно добавлен', reply_markup=await kb.reply_menu())
    elif message.video:
        put_photo = await cursor.execute('''
            INSERT INTO msg_kb (id, text, video, reply_markup, url)
            VALUES (?, ?, ?, ?, ?)                 
            ''', (current_id, message_data['text'], message_data['video'], message_data['reply_markup'], message_data['url']))
        await connect.commit()
        put_video = await put_video.fetchone()
        await message.answer('✅ Пост успешно добавлен', reply_markup=await kb.reply_menu())
    await state.clear()
    