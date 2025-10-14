from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext

from functions.db_handler import del_groupid_subadmin, edit_link_subadmin, get_group_id_subadmin, get_link_subadmin, put_group_id_subadmin
from is_admin.isadmin import IsAdmin
from keyboards.admin_kb import subadmin_kb, button_back_subadmin
from state_fsm.fsm import AdminState

router = Router()

subadmin_kb_edit = types.InlineKeyboardMarkup(inline_keyboard=subadmin_kb)
kb_button_back_subadmin = types.InlineKeyboardMarkup(inline_keyboard=button_back_subadmin)

@router.callback_query(F.data == 'admin_edit', IsAdmin())
async def admin_hello_message(query: types.CallbackQuery):
    await query.message.edit_text('🧑‍🧑‍🧒‍🧒 Вы в меню управления админами\n' \
    'Что хотите сделать?', reply_markup=subadmin_kb_edit)

@router.callback_query(F.data == 'grant_subadmin_profile', IsAdmin())
async def process_add_subadmin(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_text('👀 Введите USERNAME пользователя без @ для добавление в группу саб-админов', reply_markup=kb_button_back_subadmin)
    await state.set_state(AdminState.fsm_add_subadmin)

@router.message(AdminState.fsm_add_subadmin)
async def add_subadmin(message:types.Message, state:FSMContext):
    username = message.text
    subadmin_group_id = await get_group_id_subadmin(username)
    if subadmin_group_id == 3:
        await put_group_id_subadmin(username)
        await message.answer('✅ Саб-админ добавлен!\n\n' \
                             '🧑‍🧑‍🧒‍🧒 Вы в меню управления админами\n' \
                             'Что хотите сделать?', reply_markup=subadmin_kb_edit)
    elif subadmin_group_id == 2:
        await message.answer('👀 Саб-админ уже в нужной группе!\n\n' \
                             '🧑‍🧑‍🧒‍🧒 Вы в меню управления админами\n' \
                             'Что хотите сделать?', reply_markup=subadmin_kb_edit)
    elif subadmin_group_id == None:
        await message.answer('❌ Пользователя не существует\n\n'
                             '🧑‍🧑‍🧒‍🧒 Вы в меню управления админами\n' \
                             'Что хотите сделать?', reply_markup=subadmin_kb_edit)
    await state.clear()

@router.callback_query(F.data == 'grant_down_subadmin_profile', IsAdmin())
async def process_del_subadmin(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_text('⚠️ Введите USERNAME пользователя без @ для УДАЛЕНИЯ из группы саб-админов', reply_markup=kb_button_back_subadmin)
    await state.set_state(AdminState.fsm_del_subadmin)

@router.message(AdminState.fsm_del_subadmin)
async def delete_subadmin(message:types.Message, state:FSMContext):
    username = message.text
    subadmin_group_id = await get_group_id_subadmin(username)
    if subadmin_group_id == 2:
        await del_groupid_subadmin(username)
        await message.answer('✅ Саб-админ удален!\n\n' \
                             '🧑‍🧑‍🧒‍🧒 Вы в меню управления админами\n' \
                             'Что хотите сделать?', reply_markup=subadmin_kb_edit)
    elif subadmin_group_id == 3:
        await message.answer('👀 Пользователь уже в нужной группе!\n\n' \
                             '🧑‍🧑‍🧒‍🧒 Вы в меню управления админами\n' \
                             'Что хотите сделать?', reply_markup=subadmin_kb_edit)
    elif subadmin_group_id == None:
        await message.answer('❌ Пользователя не существует\n\n'
                             '🧑‍🧑‍🧒‍🧒 Вы в меню управления админами\n' \
                             'Что хотите сделать?', reply_markup=subadmin_kb_edit)
    await state.clear()

@router.callback_query(F.data == 'edit_bounty_link', IsAdmin())
async def process_edit_link_subadmin(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_text('⚠️ Введите USERNAME пользователя без @ для изменения реферальной ссылки', reply_markup=kb_button_back_subadmin)
    await state.set_state(AdminState.fsm_process_link_bounty)

@router.message(AdminState.fsm_process_link_bounty)
async def link_subadmin(message:types.Message, state:FSMContext):
    username = message.text
    subadmin_group_id = await get_group_id_subadmin(username)
    if subadmin_group_id == 2:
        await state.set_state(AdminState.fsm_edit_link_bounty)
        subadmin_link = await get_link_subadmin(username)
        await state.update_data(username=username)
        await message.answer(f'🧑‍🧑‍🧒‍🧒 Пользователь - {username}\n'
                             f'🔗 Его реферальная ссылка - {subadmin_link}\n\n'
                             '⚠️ Введите новую ссылку, чтобы изменить?', reply_markup=kb_button_back_subadmin)
    elif subadmin_group_id == 3:
        await state.clear()
        await message.answer('❌ Пользователь не является саб-админом!\n\n' \
                             '🧑‍🧑‍🧒‍🧒 Вы в меню управления админами\n' \
                             'Что хотите сделать?', reply_markup=subadmin_kb_edit)
    elif subadmin_group_id == None:
        await message.answer('❌ Пользователя не существует\n\n'
                             '🧑‍🧑‍🧒‍🧒 Вы в меню управления админами\n' \
                             'Что хотите сделать?', reply_markup=subadmin_kb_edit)

@router.message(AdminState.fsm_edit_link_bounty)
async def link_subadmin(message:types.Message, state:FSMContext):
    data = await state.get_data()
    username = data.get('username')
    subadmin_link = message.text
    if not (subadmin_link.startswith('http://') or subadmin_link.startswith('https://')):
            await message.answer('❌ URL должен начинаться с http:// или https://\n' \
                             'Введите URL повторно или вернитесь назад' , reply_markup=subadmin_kb_edit)
            return
        
    await edit_link_subadmin(subadmin_link, username)
    await message.answer('✅ Реферальная ссылка изменена!\n\n'
                         f'🧑‍🧑‍🧒‍🧒 Пользователь - {username}\n'
                         f'🔗 Его новая реферальная ссылка - {subadmin_link}\n\n'
                         'Что хотите сделать?', reply_markup=subadmin_kb_edit,
                         parse_mode=None)