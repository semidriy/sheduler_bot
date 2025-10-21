import asyncio
from datetime import datetime
from aiogram import F, Bot, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from collections import defaultdict

from config_data.config import Config, load_config
from functions.db_handler import get_subadmin_user_id
from is_admin.isadmin import IsAdmin
from keyboards.admin_kb import mailing_menu, mailing_admin_menu, button_back_to_admin
from state_fsm.fsm import AdminState, ScheduleStates
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

config: Config = load_config()
bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

mailing_list = types.InlineKeyboardMarkup(inline_keyboard=mailing_menu)
mailing_admin_menu = types.InlineKeyboardMarkup(inline_keyboard=mailing_admin_menu)
admin_keyboard_main = types.InlineKeyboardMarkup(inline_keyboard=button_back_to_admin)

router = Router()

# Хранилище для отложенных сообщений
scheduled_messages = defaultdict(list)

##  Подменю рассылки
@router.callback_query(F.data == 'news', IsAdmin())
async def admin_hello_message(query: types.CallbackQuery):
    await query.message.edit_text('Для кого делаем рассылку? 👀', reply_markup=mailing_list)

@router.callback_query(F.data == 'admin_news', IsAdmin())
async def admin_news_get(query: types.CallbackQuery):
     await query.message.edit_text('👤 Рассылка для администраторов', reply_markup=mailing_admin_menu)

##  Функция рассылки Админам 2 группы 
@router.callback_query(F.data == 'create_waiting_first', IsAdmin())
async def admin_news_get(query: types.CallbackQuery, state: FSMContext, bot: Bot):
    await query.message.edit_text('👀 Введите пост для рассылки администраторам ⚠️\n\n' \
                                  'Или нажмите кнопку выхода в главное меню',
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="↩️ Отмена", callback_data="news")]]))
    
    await state.set_state(ScheduleStates.waiting_for_admin_news_first)

@router.message(ScheduleStates.waiting_for_admin_news_first)
async def schedule_message(message: types.Message, state: FSMContext):
    await state.set_state(ScheduleStates.waiting_date_for_admin_first)
    
    # Сохраняем сообщение в FSM
    message_data = {
        'text': message.html_text if message.text else (message.caption if message.caption else ""),
        'photo': message.photo[-1].file_id if message.photo else None,
        'video': message.video.file_id if message.video else None,
        'reply_markup': message.reply_markup.model_dump_json() if message.reply_markup else None
    }
    
    await state.update_data(message_data=message_data)
    await message.answer("⏳ Теперь введите время отправки в формате: ЧЧ ММ ДД ММ\n(часы минуты день месяц, например: 12 00 31 12)\n\n" \
                                  'Или нажмите кнопку выхода в главное меню',
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="↩️ Отмена", callback_data="news")]]))

@router.message(ScheduleStates.waiting_date_for_admin_first)
async def process_schedule_time(message: types.Message, state: FSMContext):
    try:
        # Парсим дату и время
        hour, minute, day, month = map(int, message.text.split())
        
        now = datetime.now()
        schedule_time = datetime(now.year, month, day, hour, minute)
        
        if schedule_time < now:
            schedule_time = datetime(now.year + 1, month, day, hour, minute)
            if schedule_time < now:
                await message.answer("❌ Некорректная дата! Указанное время уже прошло.")
                return
            
        data = await state.get_data()
        message_data = data.get('message_data')
        
        # Генерируем уникальный ID для сообщения
        message_id = f"{message.from_user.id}_{datetime.now().timestamp()}"
        
        # Добавляем сообщение в список отложенных
        scheduled_messages[message.from_user.id].append({
            'id': message_id,
            'message': message_data,
            'time': schedule_time,
            'users': await get_subadmin_user_id()
        })
        
        await message.answer(
            f"✅ Сообщение запланировано на {schedule_time.strftime('%d.%m.%Y %H:%M')}\n",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="➕ Добавить еще", callback_data="create_waiting_first")],
                [types.InlineKeyboardButton(text="📝 Мои отложенные админам", callback_data="list_scheduled_admins")],
                [types.InlineKeyboardButton(text="🔙 Назад", callback_data="admin_news")]
            ]
            )
        )
        await state.clear()
        
        # Запускаем задачу на отправку
        asyncio.create_task(send_scheduled_message(message.from_user.id, message_id, schedule_time))  
    except ValueError as e:
        await message.answer("❌ Неверный формат времени. Используйте: ДД ММ ЧЧ ММ")
async def send_scheduled_message(user_id: int, message_id: str, schedule_time: datetime):
    now = datetime.now()
    delay = (schedule_time - now).total_seconds()
    
    if delay > 0:
        await asyncio.sleep(delay)
        
        # Находим сообщение в хранилище
        for msg in scheduled_messages.get(user_id, []):
            if msg['id'] == message_id:
                message_data = msg['message']
                users = msg['users']
                i = 0
                
                for user in users:
                    try:
                        reply_markup = None
                        if message_data['reply_markup']:
                            reply_markup = types.InlineKeyboardMarkup.model_validate_json(message_data['reply_markup'])

                        if message_data['video']:
                            await bot.send_video(
                                chat_id=user,
                                video=message_data['video'],
                                caption=message_data['text'] if message_data['text'] else None,
                                reply_markup=reply_markup,
                                parse_mode="HTML"
                            )
                        elif message_data['photo']:
                            await bot.send_photo(
                                chat_id=user,
                                photo=message_data['photo'],
                                caption=message_data['text'] if message_data['text'] else None,
                                reply_markup=reply_markup,
                                parse_mode="HTML"
                            )
                        else:
                            # Обычное текстовое сообщение
                            await bot.send_message(
                                chat_id=user,
                                text=message_data['text'],
                                reply_markup=reply_markup,
                                parse_mode="HTML"
                            )
                        i += 1
                        await asyncio.sleep(0.3)
                    except Exception as e:
                        print(f"Ошибка отправки для {user}: {e}")
                
                count_user_access = len(users)
                await bot.send_message(
                    user_id,
                    f'📬 Рассылка завершена\n\n'
                    f'👥 Всего пользователей: {count_user_access}\n'
                    f'✅ Удалось отправить: {i}\n❌ Не удалось отправить: {count_user_access - i}',
                    reply_markup=admin_keyboard_main
                )
                
                # Удаляем отправленное сообщение
                scheduled_messages[user_id] = [m for m in scheduled_messages[user_id] if m['id'] != message_id]
                break

# Просмотр всех отложенных сообщений
@router.callback_query(F.data == "list_scheduled_admins", IsAdmin())
async def list_scheduled_messages(query: types.CallbackQuery):
    messages = scheduled_messages.get(query.from_user.id, [])
    
    if not messages:
        await query.message.edit_text("ℹ️ У вас нет отложенных сообщений",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🔙 Назад", callback_data="news")]])
        )
        return
    
    text = "📅 <b>Ваши отложенные сообщения для админов👤:</b>\n\n"
    for msg in messages:
        
        text += (
            f"⏰ <b>Время отправки:</b>\n" 
            f"{msg['time'].strftime('%d.%m.%Y %H:%M')}\n\n"
            f"📝 <b>Текст:</b>\n"
            f"{msg['message']['text']}\n"
            "#############################\n"
        )

    await query.message.edit_text(
        text,
        disable_web_page_preview=True,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="❌ Удалить", callback_data="delete_scheduled_menu")],
            [types.InlineKeyboardButton(text="🔙 Назад", callback_data="news")]
        ]
        )
    )

# Меню удаления сообщений
@router.callback_query(F.data == "delete_scheduled_menu", IsAdmin())
async def delete_scheduled_menu(query: types.CallbackQuery):
    messages = scheduled_messages.get(query.from_user.id, [])
    
    if not messages:
        await query.answer("⚠️ Нет сообщений для удаления")
        return
    
    buttons = []
    for msg in messages:
        buttons.append([
            types.InlineKeyboardButton(
                text=f"Удалить {msg['time'].strftime('%d.%m.%Y %H:%M')}",
                callback_data=f"delete_scheduled_admins_{msg['id']}"
            )
        ])

    # Добавляем кнопку "Назад" в конец
    buttons.append([
        types.InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="list_scheduled_admins"
        )
    ])  
    
    await query.message.edit_text(
        "👀 Выберите сообщение для удаления:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    

# Удаление конкретного сообщения
@router.callback_query(F.data.startswith("delete_scheduled_admins_"), IsAdmin())
async def delete_scheduled_message(query: types.CallbackQuery):
    message_id = query.data.split("_")[-1]
    user_id = query.from_user.id
    
    if user_id in scheduled_messages:
        initial_count = len(scheduled_messages[user_id])
        scheduled_messages[user_id] = [m for m in scheduled_messages[user_id] if m['id'] != message_id]
        
        if len(scheduled_messages[user_id]) < initial_count:
            await query.message.edit_text(f"✅ Сообщение {message_id} удалено")
        else:
            await query.message.edit_text("⚠️ Сообщение не найдено")
    else:
        await query.message.edit_text("ℹ️ Нет отложенных сообщений")

# Функция немедленной отправки
@router.callback_query(F.data == 'send_admin_now', IsAdmin())
async def send_message_immediately(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.waiting_for_admin_news)
    await query.message.edit_text('⚠️⚠️⚠️ Введите пост для немедленной рассылки администраторам 👤:')
    
@router.message(AdminState.waiting_for_admin_news)
async def admin_news_message(message: types.Message, state: FSMContext):
    users = await get_subadmin_user_id()
    i = 0
    await state.clear()
     # Подготовка данных сообщения
    message_data = {
        'text': message.html_text if message.text else (message.caption if message.caption else ""),
        'photo': message.photo[-1].file_id if message.photo else None,
        'video': message.video.file_id if message.video else None,
        'reply_markup': message.reply_markup.model_dump_json() if message.reply_markup else None
    }
    # print(message_data['reply_markup'])
    for user in users:
            try:
                reply_markup = None
                if message_data['reply_markup']:
                    reply_markup = types.InlineKeyboardMarkup.model_validate_json(message_data['reply_markup'])

                if message_data['video']:
                    await bot.send_video(
                        chat_id=user,
                        video=message_data['video'],
                        caption=message_data['text'] if message_data['text'] else None,
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
                elif message_data['photo']:
                    await bot.send_photo(
                        chat_id=user,
                        photo=message_data['photo'],
                        caption=message_data['text'] if message_data['text'] else None,
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
                    print(reply_markup)
                else:
                    # Обычное текстовое сообщение
                    await bot.send_message(
                        chat_id=user,
                        text=message_data['text'],
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
                i += 1
                await asyncio.sleep(0.3)
            except Exception as e:
                print(f"❌ Ошибка отправки для {user}: {e}")
    count_user_access = len(users)
    await message.answer(f'📬 Рассылка завершена\n\n'
                         f'👥 Всего пользователей: {count_user_access}\n'
                         f'✅ Удалось отправить: {i}\n❌ Не удалось отправить: {count_user_access - i}',
                         reply_markup=admin_keyboard_main
    )