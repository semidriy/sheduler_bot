from aiogram import Bot
import aiosqlite
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

class MessageScheduler:
    def __init__(self):
        self.scheduler = None
        self.bot = None
        self.db_name = 'bot.db'
    
    def setup(self, bot: Bot, scheduler: AsyncIOScheduler):
        self.bot = bot
        self.scheduler = scheduler
    
    async def schedule_welcome_messages(self, user_id: int):
        if not self.scheduler or not self.bot:
            return
        
        try:
            # Получаем сообщения и их тайминги из БД
            async with aiosqlite.connect(self.db_name) as connect:
                cursor = await connect.cursor()
                
                # Предполагаем, что в таблице msg_kb есть поле timer
                await cursor.execute('''
                    SELECT id, text, photo, video, reply_markup, url, timer 
                    FROM msg_kb 
                    WHERE timer IS NOT NULL 
                ''')
                messages = await cursor.fetchall()
                
                for msg in messages:
                    msg_id, text, photo, video, reply_markup, url, timer = msg
                    
                    self.scheduler.add_job(
                        self._send_message_with_keyboard,
                        'date',
                        run_date=datetime.now() + timedelta(seconds=timer),
                        args=[user_id, text, photo, video, reply_markup, url],
                        id=f"msg_{msg_id}_user_{user_id}"
                    )
                    
        except Exception as e:
            print(f"1AdvancedMessageScheduler: ошибка - {e}")

    async def _send_message_with_keyboard(self, user_id: int, text: str, photo:str, video: str, 
                                        reply_markup: str, url: str):
        """Отправляем сообщение с конструктором клавиатур"""
        try:
            # Создаем клавиатуру через конструктор
            keyboard = None
            if reply_markup and url:
                from aiogram.utils.keyboard import InlineKeyboardBuilder
                from aiogram.types import InlineKeyboardButton
                
                builder = InlineKeyboardBuilder()
                builder.add(InlineKeyboardButton(
                    text=reply_markup,
                    url=url
                ))
                keyboard = builder.as_markup()
            
            # Отправляем сообщение
            if photo == 'NONE':
                await self.bot.send_video(
                    chat_id=user_id,
                    video=video,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="MarkdownV2"
                )
            else:
                await self.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="MarkdownV2"
                )
                
        except Exception as e:
            print(f"AdvancedMessageScheduler: ошибка отправки - {e}")
        # # Второе сообщение через 30 секунд
        # self.scheduler.add_job(
        #     self._send_second_message,
        #     'date',
        #     run_date=datetime.now() + timedelta(seconds=10),
        #     args=[user_id],
        #     id=f"second_msg_{user_id}"
        # )
        
        # # Третье сообщение через 120 секунд
        # self.scheduler.add_job(
        #     self._send_third_message,
        #     'date',
        #     run_date=datetime.now() + timedelta(seconds=12),
        #     args=[user_id],
        #     id=f"third_msg_{user_id}"
        # )
    
    # async def _send_second_message(self, user_id: int):
    #     try:
    #         await self.bot.send_message(
    #             user_id, 
    #             "⏰ Это второе сообщение через 10 секунд!"
    #         )
    #     except Exception as e:
    #         print(f"Ошибка отправки второго сообщения: {e}")
    
    # async def _send_third_message(self, user_id: int):
    #     try:
    #         await self.bot.send_message(
    #             user_id, 
    #             "🎯 Прошло 12 сек! Если есть вопросы - обращайтесь!"
    #         )
    #     except Exception as e:
    #         print(f"Ошибка отправки третьего сообщения: {e}")

# Глобальный экземпляр
message_scheduler = MessageScheduler()