from aiogram import Bot, Dispatcher, executor
from bot.config import TOKEN
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from bot.middleware.language_middleware import setup_middleware



storage = RedisStorage2(db=1)
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot=bot, storage=storage)
i18n = setup_middleware(dp)

global _
# Создадим псевдоним для метода gettext
_ = i18n.lazy_gettext
# Настроим i18n middleware для работы с многоязычностью

# register_user_handlers(dp)
    
