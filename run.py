# from bot.loader import start_bot
from aiogram import Dispatcher
from aiogram import executor
from bot.database.database import create_db
from bot.config import TOKEN, ADMIN_ID
from bot.handlers.user_handlers import register_commands
from bot.loader import dp, bot
from bot.middleware.photo_middleware import AlbumMiddleware
from bot.middleware.throttling_middleware import ThrottlingMiddleware
import asyncio
import logging
import aioschedule

from bot.utils.utils import send_notification_to_admin_about_new_post

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="bot/logs/main.log")
formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

async def scheduler():
    aioschedule.every(10).seconds.do(send_notification_to_admin_about_new_post)
    
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(dp: Dispatcher):
    await bot.send_message(ADMIN_ID[0], "Bot was started successfully!")
    await create_db()
    await register_commands()
    asyncio.create_task(scheduler())

async def on_shutdown(dp: Dispatcher):
    await dp.storage.close()


if __name__ == "__main__":
    try:
        from bot.handlers.user_handlers import dp
        from bot.handlers.admin_handlers import dp
        dp.middleware.setup(AlbumMiddleware())
        dp.middleware.setup(ThrottlingMiddleware())
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
    except Exception:
        logger.exception('Main')