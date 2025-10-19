from logging import config
from aiogram.filters import Command
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
import aiosqlite

from functions.db_handler import get_bounty_cashback, get_count_referal, get_current_cashback, get_min_cashback, get_referrer_bounty_sum, get_referrer_wallet, get_username_for_bouynt
from state_fsm.fsm import SubAdminState
from is_admin.isadmin import IsSubadmin
from keyboards.subadm_kb import subadmin_menu, wallet_kb
from keyboards.admin_kb import cash_out_kb
from config_data.config import Config, load_config

config: Config = load_config()
admin_ids=config.tg_bot.admin_ids

bot = Bot(token=config.tg_bot.token)

out_kb = types.InlineKeyboardMarkup(inline_keyboard=cash_out_kb)

router = Router()

@router.message(F.text == 'Меню', IsSubadmin())
async def profile_menu(message: types.Message) -> None:
    await message.answer('''
📋 <b>Главное меню</b>

Выберите нужный <b>раздел:</b>

📈 <b>Статистика</b> - Информация о вашей статистике
                         
🔗 <b>Реф. ссылка</b> - Информация о реферальной системе
                         
💰 <b>Вывод денег</b> - Запрос вывода денег
                         
📌 <b>Мои реквизиты</b> - Настройки ваших реквизитов
''', reply_markup=subadmin_menu)

@router.message(F.text == 'Реф. ссылка 🔗', IsSubadmin())
async def referral_link(message: types.Message) -> None:
    await message.answer('⤵️ Ваша реферальная ссылка \n'
                         f'└<code>https://t.me/AliBabyUSD_Bot?start={message.from_user.id}</code>\n\n'
                         'Нажмите на ссылку, чтобы ее скопировать', parse_mode="HTML")
    
@router.message(F.text == 'Статистика 📈', IsSubadmin())
async def statistic(message: types.Message) -> None:
    min_cashback = await get_min_cashback()
    user_id = message.from_user.id
    bounty_cashback = await get_bounty_cashback()
    count_referal = await get_count_referal(user_id)
    count_bounty_cashback = count_referal * bounty_cashback
    current_cashback = await get_current_cashback(user_id)
    await message.answer('📊 <b>Статистика:</b>\n\n'
                        f'┌ Вы пригласили: <b>{count_referal}</b>\n'
                        f'├ Доход за все время: <b>{count_bounty_cashback}₽</b>\n'
                        f'└ Доступно к выводу: <b>{current_cashback}₽</b>\n\n'
                        f'⚠️ Минимальная суммы вывода составляет <b>{min_cashback}₽</b>', parse_mode="HTML")

@router.message(F.text == 'Вывод денег 💰', IsSubadmin())
async def cash_output(message: types.Message) -> None:
    admin_ids = config.tg_bot.admin_ids
    min_cashback = await get_min_cashback()
    bounty_sum = await get_referrer_bounty_sum(message.from_user.id)
    wallet_id = await get_referrer_wallet(message.from_user.id)
    ##  Клавиатура обнуления баланса
    kb_reset_bounty_sum = [
        [types.InlineKeyboardButton(text='Обнулить', callback_data=f'clear_balance:{message.from_user.id}')]
    ]
    kb_balance = types.InlineKeyboardMarkup(inline_keyboard=kb_reset_bounty_sum)
    if int(bounty_sum) >= int(min_cashback):
        if message.from_user.username != None:
            await message.answer('Заявка на вывод денег отправлена💰\n\n'
                                f'💰 Сумма к выплате <b>{bounty_sum}₽</b>\n'
                                 'Можете дождаться пока с вами свяжутся или открыть диалог самостоятельно\n'
                                 '                                ↘️ ⬇️ ↙️', reply_markup=out_kb, parse_mode="HTML")
            for admin_id in admin_ids:
                await bot.send_message(admin_id, '⚠️ У вас <b>новая заявка</b> от пользователя\n\n'
                               f'👤 Его ссылка @{message.from_user.username}\n'
                               '📌 Его реквизиты \n\n'
                               f'<code>{wallet_id}</code>\n\n'
                               f'💰 Сумма к выплате {bounty_sum}₽', parse_mode="HTML", reply_markup=kb_balance)
        else:
            await message.answer('Вы запросили <b>вывод денег</b> 💰\n'
                                 'К сожалению у вас отсутствует <b>юзернейм</b> и мы не можем связаться с вами самостоятельно😔\n'
                                 'Пожалуйста воспользуйтесь кнопкой для связи напрямую и вывода средств\n'
                                 'Не забудьте указать адрес вашего кошелька в сети TRC20'
                                 '                                ↘️ ⬇️ ↙️', reply_markup=out_kb, parse_mode="HTML")
    else:
        await message.answer(f'💰 <b>Ваш баланс {bounty_sum}₽</b>\n\n' \
                             f'❌ Баланс для вывода должен быть <b>больше {min_cashback}₽</b>', reply_markup=subadmin_menu, parse_mode="HTML")

@router.callback_query(F.data.startswith('clear_balance'))
async def process_hello_text(query: types.CallbackQuery):
    ##  Получаем id пользователя, который оставил заявку роутера Вывод денег
    user_id = query.data.split(':')[1]
    ##. Получаем username пользователя, который оставил заявку
    username = await get_username_for_bouynt(user_id)
    ##  Получаем его реквизиты и баланс
    wallet_id = await get_referrer_wallet(user_id)
    bounty_sum = await get_referrer_bounty_sum(user_id)

    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    sql = await cursor.execute('UPDATE users SET bounty_sum = 0 WHERE user_id=?', (user_id,))
    await connect.commit()
    sql = await sql.fetchone()
    await cursor.close()
    await connect.close()
    await query.message.edit_text('✅ Заявка выполнена\n\n'
                               f'👤 Его ссылка @{username}\n'
                               '📌 Его реквизиты \n\n'
                               f'<code>{wallet_id}</code>\n\n'
                               f'💰 Сумма к выводу была равна {bounty_sum}₽', parse_mode="HTML")

    await bot.send_message(user_id, 'Администратор <b>обнулил</b> ваш баланс ✅\n\n'
                                    'Деньги на счет придут <b>в течении 5-15 минут</b>'
                                    'Спасибо что выбрали <b>наш сервис</b> 🥳')

@router.message(F.text == 'Мои реквизиты 📌', IsSubadmin())
async def subadm_wallet(message: types.Message) -> None:
    wallet_id = await get_referrer_wallet(message.from_user.id)
    await message.answer(f'👀 <b>Ваши реквизиты кошелька в сети TRC20</b>\n\n<code>{wallet_id}</code>\n\n'
                          '⚪️ Нажмите кнопку <b>✏️ Изменить реквизиты</b> для того чтобы записать или изменить ваши реквизиты\n', reply_markup=wallet_kb, parse_mode="HTML")

@router.message(F.text == 'Изменить ✏️', IsSubadmin())
async def process_put_wallet(message: types.Message, state: FSMContext):
    await message.answer('👀 Введите ваш адрес кошелька в сети TRC20')
    await state.set_state(SubAdminState.fsm_wallet_id)

@router.message(SubAdminState.fsm_wallet_id)
async def edit_wallet_id(message:types.Message, state:FSMContext):
    wallet = message.text
    user_id = message.from_user.id
    connect = await aiosqlite.connect('bot.db')
    cursor = await connect.cursor()
    wallet_id = await cursor.execute('UPDATE users SET wallet_id = ? WHERE user_id=?', (wallet, user_id))
    await connect.commit()
    wallet_id = await wallet_id.fetchone()
    await cursor.close()
    await connect.close()
    await message.answer('✅ Ваши реквизиты изменены', reply_markup=subadmin_menu)
    await state.clear()

@router.message(F.text == 'Назад 🔙', IsSubadmin())
async def process_back_to_menu(message: types.Message):
    await message.answer('Ваш профиль!', reply_markup=subadmin_menu)