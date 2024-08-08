from aiogram import Bot, Dispatcher
from config import token
from handlers import router
import asyncio

bot = Bot(token)
disp = Dispatcher()

async def main():
    disp.include_router(router)
    await disp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())