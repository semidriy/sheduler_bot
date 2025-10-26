import asyncio
from aiogram.filters import Command
from aiogram import Bot, types, Router, F
from functions.db_handler import get_capcha_timer, update_users_alive, update_users_capcha
from functions.last_start_message import bounty_referr
from functions.start_message import delete_previous_message
from services.message_scheduler import message_scheduler
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from functions.get_messages import call_first_start_sales

router = Router()

class UserState(StatesGroup):
    waiting_for_button = State()

@router.message(Command('start'))
async def admin_command(message: types.Message, state: FSMContext) -> None:
    await state.set_state(UserState.waiting_for_button)
    await message_scheduler.schedule_welcome_messages(message.from_user.id)
    await start_periodic_messages(message, state)

async def start_periodic_messages(message: types.Message, state: FSMContext):
    """Запускает периодические сообщения"""
    # user_id = message.from_user.id
    
    # Инициализируем данные состояния
    await state.update_data(
        periodic_task_active=True,
        last_message_id=None,  # ID последнего отправленного сообщения
        message_count=0  # Счетчик отправленных сообщений
    )
    
    # Отправляем первое сообщение
    await call_first_start_sales(message, state)  # Передаем state
    
    # Запускаем периодическую отправку
    asyncio.create_task(periodic_message_worker(message, state))

async def periodic_message_worker(message: types.Message, state: FSMContext):
    """Рабочий процесс для периодической отправки сообщений"""
    ##  Получаем время для спама капчи
    capcha_timer = await get_capcha_timer()

    while True:
        await asyncio.sleep(capcha_timer[0]) 
        
        # Проверяем состояние
        current_state = await state.get_state()
        if current_state != UserState.waiting_for_button.state:
            break
            
        # Проверяем флаг в хранилище
        data = await state.get_data()
        if not data.get('periodic_task_active', True):
            break
            
        # Отправляем новое сообщение (предыдущее удалится внутри функции)
        await call_first_start_sales(message, state)

@router.message(UserState.waiting_for_button)
async def handle_button_press(message: types.Message, state: FSMContext):
    # Удаляем последнее периодическое сообщение перед отправкой ответа
    await delete_previous_message(message, state)
    
    # Останавливаем периодические сообщения
    await state.update_data(periodic_task_active=False)
    await state.clear()
    ## Проставляем статус живого пользователя
    await update_users_alive(message.from_user.id)
    await update_users_capcha(message.from_user.id)
    await bounty_referr(message)


@router.message(Command('delmenu'))
async def del_main_menu(message: types.Message, bot: Bot):
    await bot.delete_my_commands()
    await message.answer(text='Кнопка "Menu" удалена')