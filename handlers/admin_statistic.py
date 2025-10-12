import asyncio
from aiogram import types, F, Router

from functions.db_handler import get_admin_count_referal, get_admin_current_cashback, get_admin_referal_link, get_all_admin_count_referal, get_bounty_cashback
from is_admin.isadmin import IsAdmin
from keyboards.admin_kb import button_back_to_admin

router = Router()

kb_button_back_to_admin = types.InlineKeyboardMarkup(inline_keyboard=button_back_to_admin)

@router.callback_query(F.data == 'admin_stat', IsAdmin())
async def admin_process_stat(query: types.CallbackQuery):
    try:
        subadmin_users = await get_all_admin_count_referal()
        
        if not subadmin_users:
            await query.message.answer("❌ Список администраторов пуст.")
            return
        
        await query.message.edit_text(f"🔍 Всего {len(subadmin_users)} администраторов:")
        
        for subadmin in subadmin_users:
            username = subadmin[0]  # Извлекаем имя из кортежа
            ##  Получаем статистику
            bounty_cashback = await get_bounty_cashback()
            referal_link = await get_admin_referal_link(username)
            count_referal = await get_admin_count_referal(username)
            count_bounty_cashback = count_referal * bounty_cashback
            current_cashback = await get_admin_current_cashback(username)
            # Отправляем каждого админа отдельно
            await query.message.answer(f"👤 @{username}\n\n"
                                       f'Его реферальная ссылка:\n {referal_link}\n\n'
                                       '📈 Его статистика:\n\n'
                                       f'┌ Приглашенные пользователи: {count_referal}\n'
                                       f'├ Доход за все время: {count_bounty_cashback}₽\n'
                                       f'└ Доступно к выводу: {current_cashback}₽', disable_web_page_preview=True)
            await asyncio.sleep(0.3)
    except Exception as e:
        await query.message.answer(f"⚠️ Ошибка: {e}")
    await query.message.answer('Вернуться назад?', reply_markup=kb_button_back_to_admin)