# from bot.loader import start_bot
from aiogram import Dispatcher
from bot.database.database import create_db
from bot.config import TOKEN, ADMIN_ID
from aiogram import executor
from bot.handlers.user_handlers import register_commands
from bot.loader import dp, bot
# from bot.middleware.language_middleware import setup_middleware
from bot.middleware.photo_middleware import AlbumMiddleware

async def on_startup(dp: Dispatcher):
    await bot.send_message(ADMIN_ID[0], "Bot was started successfully!")
    await create_db()
    await register_commands()

async def on_shutdown(dp: Dispatcher):
    await dp.storage.close()


if __name__ == "__main__":
    from bot.handlers.user_handlers import dp
    from bot.handlers.admin_handlers import dp
    dp.middleware.setup(AlbumMiddleware())
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)