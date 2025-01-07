import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from config import TOKEN
from app.handlers import router

bot = Bot(token=TOKEN,)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
  

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
    