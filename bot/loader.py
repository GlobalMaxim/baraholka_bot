from aiogram import Bot, Dispatcher, Router
from bot.config import I18N_DOMAIN, LOCALES_DIR, TOKEN, ADMIN_ID
# from bot.handlers.user_handlers import register_user_handlers
from aiogram.fsm.storage.redis import RedisStorage
import redis
from aiogram.utils.i18n import I18n
# from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.middleware.language_middleware import ACLMiddleware

redis_client = redis.Redis()

storage = RedisStorage(redis=redis_client)
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot=bot, storage=storage)
router = Router()
i18n = I18n(path=LOCALES_DIR, default_locale='ru')


def setup_middleware():
    # Устанавливаем миддлварь
    i18n = ACLMiddleware(i18n)
    router.message.middleware(i18n)
    # dp..setup(i18n)
    return i18n

i18n = setup_middleware()

global _
# Создадим псевдоним для метода gettext
_ = i18n.gettext
# Настроим i18n middleware для работы с многоязычностью

# register_user_handlers(dp)
    
