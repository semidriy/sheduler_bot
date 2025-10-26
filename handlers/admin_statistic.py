import asyncio
from aiogram import types, F, Router
import keyboards.admin_message_kb as kboard
import keyboards.admin_kb as kb

from functions.db_handler import del_groupid_subadmin, get_admin_count_referal, get_admin_current_cashback, get_bounty_cashback, get_sum_users, get_sum_users_alive, get_sum_users_alive_referal, get_sum_users_dead, get_sum_users_dead_referal
from is_admin.isadmin import IsAdmin
from keyboards.admin_kb import button_back_to_admin_statistic, button_back_to_admin

router = Router()

kb_button_back_to_admin_statistic = types.InlineKeyboardMarkup(inline_keyboard=button_back_to_admin_statistic)
kb_button_back_to_admin = types.InlineKeyboardMarkup(inline_keyboard=button_back_to_admin)

@router.callback_query(F.data == 'bd_stat')
async def db_process_stat(query: types.CallbackQuery):
    try:
        all_users = await get_sum_users()
        alive_users = await get_sum_users_alive()
        dead_users = await get_sum_users_dead()
        await query.message.edit_text(f'''
╔═📋Статистика Бота📋
║
╠═🌐Всего: {all_users} чел.
║
╠═💪Живые: {alive_users} чел.
╚═💀Мертвые: {dead_users} чел.
''', reply_markup=kb_button_back_to_admin)
    except Exception as e:
        await query.message.answer(f"admin_statistic.db_process_stat | Ошибка при просмотре: {e}", show_alert=True)
        print(f"admin_statistic.db_process_stat | Ошибка при удалении: {str(e)}")

@router.callback_query(F.data == 'admin_stat')
async def admin_process_stat(query: types.CallbackQuery):
    await query.message.edit_text('⚙️ Список админов', reply_markup=await kboard.stat_subadmin_kb())

@router.callback_query(lambda c: c.data and c.data.startswith('statistic_'))
async def edit_message_handler(query: types.CallbackQuery):
    try:
        # Берем все после "statistic_" - это username (строка)
        username = query.data[10:]
        #  Получаем статистику
        bounty_cashback = await get_bounty_cashback()
        count_referal = await get_admin_count_referal(username)
        count_bounty_cashback = count_referal * bounty_cashback
        current_cashback = await get_admin_current_cashback(username)
        capcha_referal = await get_sum_users_alive_referal(username)
        dead_capcha_referal = await get_sum_users_dead_referal(username)
        await query.message.edit_text(f'👤 @{username}\n\n' \
                                    #    f'Его реферальная ссылка:\n {referal_link}\n\n'
                                       '📈 Его статистика:\n\n'
                                       f'┌ Всего приглашенных пользователей: {count_referal}\n'
                                       f'├ <b>Прошли капчу:</b> {capcha_referal}₽\n'
                                       f'├ <b>Не прошли капчу:</b> {dead_capcha_referal}₽\n'
                                       f'├ <b>Выплачено:</b> {count_bounty_cashback}₽\n'
                                       f'└ Текущий кошелек: {current_cashback}₽', disable_web_page_preview=True, reply_markup=await kb.subadmin_delete_kb(username))
    except Exception as e:
        await query.message.answer(f"admin_statistic.edit_message_handler | Ошибка при просмотре: {e}", show_alert=True)
        print(f"admin_statistic.edit_message_handler | Ошибка при удалении: {str(e)}")

@router.callback_query(lambda c: c.data and c.data.startswith('delete_sub_'))
async def process_delete_subadmin(query: types.CallbackQuery):
    try:
        # Берем все после "delete_sub_" - это username (строка)
        username = query.data[11:]
        await del_groupid_subadmin(username)
        await query.message.edit_text('🚮 Саб-админ удален!\n\n' \
                             '⚙️ Список админов', reply_markup=await kboard.stat_subadmin_kb())
    except Exception as e:
        await query.message.answer(f"admin_statistic.process_delete_subadmin | Ошибка при удалении: {e}", show_alert=True)
        print(f"admin_statistic.process_delete_subadmin | Ошибка при удалении: {str(e)}")