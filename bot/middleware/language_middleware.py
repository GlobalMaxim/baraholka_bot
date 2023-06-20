from aiogram.utils.i18n.middleware import I18nMiddleware, ConstI18nMiddleware
from aiogram import Router, types
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





class ACLMiddleware(i18n):
    
    # Каждый раз, когда нужно узнать язык пользователя - выполняется эта функция
    async def get_user_locale(self, action, args):
        user = types.User.get_current()
        # Возвращаем язык из базы ИЛИ (если не найден) - язык из Телеграма
        return await get_lang(user.id) or user.locale
    i18n_middleware = ConstI18nMiddleware()
    i18n_middleware.setup()


