from datetime import datetime
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, photo_size, ContentTypes, ContentType, ReplyKeyboardRemove, InputMediaPhoto, KeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher.filters import CommandStart, Text, MediaGroupFilter, Filter
from typing import List
import json

import jsonpickle 

from bot.keyboards.user_keyboards import user_main_menu_markup, user_settings_markup
from bot.keyboards.admin_keyboard import admin_main_menu_markup, moderate_markup, settings_markup, work_mode_markup
from bot.states.states import CreateArticleStates, RegistrationStates, ModerationStates
from bot.database.database import Article, DBCommands, User
from bot.loader import dp, bot, _
from bot.config import ADMIN_ID
from bot.utils.utils import get_sample_from_article, send_article_to_chanel, set_work_mode, redis_client

db = DBCommands()

@dp.message_handler(state=ModerationStates.MODERATE)
@dp.message_handler(Text(equals=[_("Модерация")]))
async def __moderation(msg: Message, state: FSMContext):
    if str(msg.from_user.id) in ADMIN_ID:
        # print(await state.get_state())
        if await state.get_state():
            # print(1)
            data = await state.get_data()
            article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
            article.is_reviewed = True
            article.reviewed_at = datetime.now()
            if msg.text == "👎":
                article.is_approved = False
                user_id = article.user_id
                await bot.send_message(user_id, _("Ваше объявление было отклонено"))
            elif msg.text == "👍":
                article.is_approved = True
                user_id = article.user_id
                mess = await send_article_to_chanel(article)
                if isinstance(mess, list):
                    sender_chat_id = mess[0].sender_chat.id
                    mess_id = mess[0].message_id
                else:
                    sender_chat_id = mess.sender_chat.id
                    mess_id = mess.message_id
                # print(mess)
                await bot.send_message(user_id, _("Ваше объявление было опубликовано"))
                await bot.forward_message(user_id, sender_chat_id, mess_id)
            await db.update_article(article)

        articles: List[Article] = await db.get_non_reviewed_articles()
        if len(articles)>0:
            article: Article = articles[0]
            await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))
            text = get_sample_from_article(article)
            article_number_text = _("Лот № {}\n\n").format(article.id)
            text = article_number_text + text
            photos = json.loads(article.photo)['images']
            if len(photos) > 0:
                await bot.send_media_group(msg.from_user.id, media=[InputMediaPhoto(m, caption=text if key == 0 else "",  parse_mode="HTML") for key, m in enumerate(photos)])
                await bot.send_message(msg.from_user.id, _('Опубликовать?'), reply_markup=moderate_markup)
            else:
                await bot.send_message(msg.from_user.id, text)
                await bot.send_message(msg.from_user.id, _('Опубликовать?'), reply_markup=moderate_markup)
            await ModerationStates.MODERATE.set()
        else:
            await bot.send_message(msg.from_user.id, _("В данный момент нет новых постов."), reply_markup=admin_main_menu_markup)
            await state.reset_state()
            await state.reset_data()

@dp.message_handler(Text(equals=[_("Статистика")]))
async def __moderation(msg: Message):
    if str(msg.from_user.id) in ADMIN_ID:
        total_users, active_posts = await db.get_statistic()
        text = _("Всего пользователей: {}\nВсего опубликованных постов: {}").format(total_users, active_posts)
        await bot.send_message(msg.from_user.id, text)

@dp.message_handler(Text(equals=[_("Настройки ⚙️")]))
async def __moderation(msg: Message):
    # if str(msg.from_user.id) in ADMIN_ID:
    await bot.send_message(msg.from_user.id, "⚙️", reply_markup=settings_markup if str(msg.from_user.id) in ADMIN_ID else user_settings_markup)


@dp.message_handler(Text(equals=[_("Ручной")]))
@dp.message_handler(Text(equals=[_("Автоматический")]))
async def __moderation(msg: Message):
    if str(msg.from_user.id) in ADMIN_ID:
        if msg.text == str(_("Ручной")):
            set_work_mode('manual')
            await bot.send_message(msg.from_user.id, "Вы выбрали ручной режим работы ✍️", reply_markup=settings_markup if str(msg.from_user.id) in ADMIN_ID else user_settings_markup)
        elif msg.text == str(_("Автоматический")):
            set_work_mode('auto')
            await bot.send_message(msg.from_user.id, "Вы выбрали автоматический режим работы 🤖", reply_markup=settings_markup if str(msg.from_user.id) in ADMIN_ID else user_settings_markup)
        # await bot.send_message(msg.from_user.id, "⚙️", reply_markup=settings_markup if str(msg.from_user.id) in ADMIN_ID else user_settings_markup)

@dp.message_handler(Text(equals=[_("Режим работы бота")]))
async def __moderation(msg: Message):
    if str(msg.from_user.id) in ADMIN_ID:
        redis = redis_client.get('work_mode')
        if redis:
            redis = redis.decode("utf-8")
        if not redis or redis == 'manual':
            keyboard=[
                [
                    KeyboardButton(text=_("Автоматический"))
                ],
                [
                    KeyboardButton(text=_("❌ Отменить"))
                ]
            ]
            await bot.send_message(msg.from_user.id, "У вас выбран ручной режим. Все сообщения проходят модерацию", reply_markup=ReplyKeyboardMarkup(keyboard=keyboard,resize_keyboard=True))
        else:
            keyboard=[
                [
                    KeyboardButton(text=_("Ручной"))
                ],
                [
                    KeyboardButton(text=_("❌ Отменить"))
                ]
            ]
            await bot.send_message(msg.from_user.id, "У вас выбран автоматический режим. Сообщения публикуются без предварительной проверки", reply_markup=ReplyKeyboardMarkup(keyboard=keyboard,resize_keyboard=True))
            # set_work_mode('manual')
        # await bot.send_message(msg.from_user.id, "⚙️", reply_markup=settings_markup if str(msg.from_user.id) in ADMIN_ID else user_settings_markup)


@dp.message_handler(content_types=ContentType.ANY)
async def __my_articles(msg: Message):
    await bot.send_message(msg.from_user.id, _("Нет такой команды 🙄"), reply_markup=admin_main_menu_markup if str(msg.from_user.id) in ADMIN_ID else user_main_menu_markup)