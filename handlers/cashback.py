from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
import aiosqlite

from functions.db_handler import get_bounty_cashback, get_min_cashback
from is_admin.isadmin import IsAdmin
from keyboards.admin_kb import edit_cashback
from state_fsm.fsm import AdminState

router = Router()

cashback_edit_kb = types.InlineKeyboardMarkup(inline_keyboard=edit_cashback)

@router.callback_query(F.data == 'cashback', IsAdmin())
async def edit_cashback(query: types.CallbackQuery):
    min_cashback = await get_min_cashback()
    bounty_cashback = await get_bounty_cashback(query.from_user.id)
    await query.message.edit_text(f'⚠️ Сумма минимальной выплаты составляет {min_cashback}₽\n\n'
                                  f'💸 Оплата за реферала составляет {bounty_cashback}₽', reply_markup=cashback_edit_kb)
    
@router.callback_query(F.data == 'edit_min_cashback', IsAdmin())
async def process_min_cashback(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_text('👀 Введи новую минимальную суммы для выплаты')
    await state.set_state(AdminState.fsm_min_cashback)

@router.message(AdminState.fsm_min_cashback)
async def edit_min_cashback(message:types.Message, state:FSMContext):
    cashback_sum = message.text
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    cashback = await cursor.execute('UPDATE others  SET value_int = ? WHERE key="min_cashback";', (int(cashback_sum),))
    await connect.commit()
    cashback = await cashback.fetchone()
    await cursor.close()
    await connect.close()
    await message.answer('✅ Сумма минимальной выплаты изменена!', reply_markup=cashback_edit_kb)
    await state.clear()

@router.callback_query(F.data == 'edit_bounty_cashback', IsAdmin())
async def process_min_cashback(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_text('👀 Введи новую сумму за реферала')
    await state.set_state(AdminState.fsm_bounty_cashback)

@router.message(AdminState.fsm_bounty_cashback)
async def edit_min_cashback(message:types.Message, state: FSMContext):
    bounty_cashback = message.text
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    cashback = await cursor.execute('UPDATE others  SET value_int = ? WHERE key="bounty_cashback";', (int(bounty_cashback),))
    await connect.commit()
    cashback = await cashback.fetchone()
    await cursor.close()
    await connect.close()
    await message.answer('✅ Сумма оплаты за реферала изменена!', reply_markup=cashback_edit_kb)
    await state.clear()