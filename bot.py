from aiogram import Bot, Dispatcher
from config import token
from handlers import router, setup_bot_commands
import asyncio


bot = Bot(token)
disp = Dispatcher()


async def main():
    disp.include_router(router)
    await setup_bot_commands()
    await disp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())