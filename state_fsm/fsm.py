from aiogram.fsm.state import State, StatesGroup

##  FSM class - машина состояний
class AdminState(StatesGroup):
    ##  Редактирование сообщений
    fsm_message_button = State()
    fms_message_media = State()
    fms_message_text = State()
    fms_message_timer = State()
    fsm_new_post = State()
    ##  Редактирование Capcha
    fsm_capcha_button_name = State() # редактировние
    fsm_capcha_media = State()
    fsm_capcha_text = State()
    fsm_new_capcha = State()
    fms_capcha_timer = State()
    fsm_capcha_button = State() # добавление
    ##  Рассылка
    waiting_for_admin_news = State()
    waiting_for_user_news = State()
    waiting_date_miling_message = State()
    ##  Выплаты
    fsm_min_cashback = State()
    fsm_bounty_cashback = State()
    ##  Добавление и удаление сабадминов
    fsm_add_subadmin = State()
    fsm_del_subadmin = State()
    ##  Добавление/изменение реферальной ссылки саб админа
    fsm_process_link_bounty = State()
    fsm_edit_link_bounty = State()

    fsm_new_photo = State()
    

class SubAdminState(StatesGroup):
    ##  Для кошелька
    fsm_wallet_trc_id = State()
    fsm_wallet_bep_id = State()

##  Рассылка
class ScheduleStates(StatesGroup):
    waiting_for_admin_news_first = State() ##  Моментальная отправка
    waiting_date_for_admin_first = State()  ##  Отложенная отправка
    waiting_for_user_news_first = State()  ##  Моментальная отправка
    waiting_date_for_user_first = State()  ##  Отложенная отправка
