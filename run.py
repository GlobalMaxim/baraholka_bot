# from bot.loader import start_bot
import asyncio
from aiogram import Dispatcher
from bot.database.database import create_db
from bot.config import TOKEN, ADMIN_ID
from aiogram import executor
from bot.handlers.user_handlers import register_commands
from bot.loader import dp, bot
# from bot.middleware.language_middleware import setup_middleware
from bot.middleware.photo_middleware import AlbumMiddleware

import aioschedule
from bot.middleware.throttling_middleware import ThrottlingMiddleware

from bot.utils.utils import send_notification_to_admin_about_new_post

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
    from bot.handlers.user_handlers import dp
    from bot.handlers.admin_handlers import dp
    dp.middleware.setup(AlbumMiddleware())
    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)