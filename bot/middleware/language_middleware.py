from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram import types
from bot.config import I18N_DOMAIN, LOCALES_DIR
from bot.database.database import DBCommands
from aiogram import Dispatcher 

db = DBCommands()


async def get_lang(user_id):
    # Делаем запрос к базе, узнаем установленный язык
    user = await db.get_user(user_id)
    if user:
        # Если пользователь найден - возвращаем его
        return user.language


class ACLMiddleware(I18nMiddleware):
    # Каждый раз, когда нужно узнать язык пользователя - выполняется эта функция
    async def get_user_locale(self, action, args):
        user = types.User.get_current()
        # print(user)
        # Возвращаем язык из базы ИЛИ (если не найден) - язык из Телеграма
        return await get_lang(user.id) or user.locale


def setup_middleware(dp: Dispatcher):
    # Устанавливаем миддлварь
    i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n