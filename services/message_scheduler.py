from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

class MessageScheduler:
    def __init__(self):
        self.scheduler = None
        self.bot = None
    
    def setup(self, bot: Bot, scheduler: AsyncIOScheduler):
        self.bot = bot
        self.scheduler = scheduler
    
    async def schedule_welcome_messages(self, user_id: int):
        if not self.scheduler or not self.bot:
            return
        
        # Второе сообщение через 30 секунд
        self.scheduler.add_job(
            self._send_second_message,
            'date',
            run_date=datetime.now() + timedelta(seconds=10),
            args=[user_id],
            id=f"second_msg_{user_id}"
        )
        
        # Третье сообщение через 120 секунд
        self.scheduler.add_job(
            self._send_third_message,
            'date',
            run_date=datetime.now() + timedelta(seconds=12),
            args=[user_id],
            id=f"third_msg_{user_id}"
        )
    
    async def _send_second_message(self, user_id: int):
        try:
            await self.bot.send_message(
                user_id, 
                "⏰ Это второе сообщение через 10 секунд!"
            )
        except Exception as e:
            print(f"Ошибка отправки второго сообщения: {e}")
    
    async def _send_third_message(self, user_id: int):
        try:
            await self.bot.send_message(
                user_id, 
                "🎯 Прошло 12 сек! Если есть вопросы - обращайтесь!"
            )
        except Exception as e:
            print(f"Ошибка отправки третьего сообщения: {e}")

# Глобальный экземпляр
message_scheduler = MessageScheduler()