import asyncio
from datetime import datetime
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, photo_size, ContentTypes, ContentType, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.dispatcher.filters import CommandStart, Text, MediaGroupFilter
# from aiogram.dispatcher.filters import F
from typing import List
import json 
from aiogram_media_group import media_group_handler
import re
import pickle
import jsonpickle

from bot.keyboards.user_keyboards import choose_language, send_tel_number_markup, user_main_menu_markup, select_article_type_markup, create_article_default_markup, accept_create_article, choose_new_language
from bot.keyboards.admin_keyboard import admin_main_menu_markup
from bot.states.states import CreateArticleStates, RegistrationStates
from bot.database.database import Article, DBCommands, User, DuplicateArticleException
from bot.loader import dp, bot, _
from bot.config import ADMIN_ID
from bot.utils.utils import get_sample_from_article, send_article_to_chanel


db = DBCommands()

@dp.message_handler(commands="start")
async def __start(msg: Message) -> None:
    user_id = msg.from_user.id
    user_name = msg.from_user.full_name
    await bot.send_sticker(msg.from_user.id, sticker="CAACAgIAAxkBAAIJQWSO2SepS6soZ_x0oaMce-r6Vd4QAAJxDgACHIJQS-TTUGYws97lLwQ")
    await msg.bot.send_message(user_id, f'Привет, {user_name}!', reply_markup=ReplyKeyboardRemove())
    await db.add_new_user()
    await msg.bot.send_message(user_id, "Выбери язык", reply_markup=choose_language)

@dp.callback_query_handler(text_contains="lang")
async def __set_language(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    # Достаем последние 2 символа (например ru)
    lang = call.data[-2:]
    user: User  = await db.set_language(lang)
    data = await state.get_data()
    is_edit = data.get('change_language')
    if is_edit:
        reply_markup = admin_main_menu_markup if str(call.from_user.id) in ADMIN_ID else user_main_menu_markup
    else:
        reply_markup = None
    await call.message.answer(_("Ваш язык был изменен", locale=lang), reply_markup=reply_markup)
    await state.reset_data()
    if not is_edit:
        if user.mobile:
        # После того, как мы поменяли язык, в этой функции все еще указан старый, поэтому передаем locale=lang
            
            await bot.send_message(call.from_user.id, _("Добро пожаловать в главное меню!"), reply_markup=admin_main_menu_markup if str(call.from_user.id) in ADMIN_ID else user_main_menu_markup)
        else:
            await bot.send_message(call.from_user.id, _('Отправьте свой номер телефона'), reply_markup=send_tel_number_markup)
            await RegistrationStates.NUMBER.set()
    await call.answer()

@dp.message_handler(content_types=ContentTypes.CONTACT | ContentTypes.TEXT, state=RegistrationStates.NUMBER)
async def __set_number(msg: Message, state: FSMContext):
    if 'contact' in msg:
        phone_number = msg['contact']['phone_number']
    else:
        phone_number = msg.text
        validate_phone_number_pattern = "^\\+?[0-9][0-9]{7,14}$"
        number  = re.match(validate_phone_number_pattern, msg.text)
        if not number: 
            await bot.send_message(msg.from_user.id, _('Неправильный формат номера, попробуй еще раз'))
            return
        
    data = await state.get_data()
    is_edit = data.get('change_number')

    await db.set_mobile(phone_number)
    if is_edit:
        await bot.send_message(msg.from_user.id, _("Номер телефона был изменен"), reply_markup=admin_main_menu_markup if str(msg.from_user.id) in ADMIN_ID else user_main_menu_markup)
    else:
        await bot.send_message(msg.from_user.id, _("Вы в главном меню! 🫡"), reply_markup=admin_main_menu_markup if str(msg.from_user.id) in ADMIN_ID else user_main_menu_markup)
    await state.reset_state()

# @dp.message_handler(state=CreateArticleStates.FINISHED)
@dp.message_handler(Text(equals=[_("❌ Отменить")]), state="*")
async def main_menu(msg: Message, state: FSMContext):
    await bot.send_message(msg.from_user.id, _("Вы в главном меню!"), reply_markup=admin_main_menu_markup if str(msg.from_user.id) in ADMIN_ID else user_main_menu_markup)
    await state.reset_state()
    await state.reset_data()

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.TITLE)
@dp.message_handler(Text(equals=[_("Создать объявление")]))
async def __create_article(msg: Message, state: FSMContext):
    await bot.send_message(msg.from_user.id, _("Выберите категрию"), reply_markup=select_article_type_markup)
    await CreateArticleStates.CATEGORY.set()

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.DESCRIPTION)
@dp.message_handler(state=CreateArticleStates.CATEGORY)
async def __select_category(msg: Message, state: FSMContext):
    article = Article()
    article.user_id = msg.from_user.id
    article.type = msg.text.replace(_("⬅️ Назад"), "")
    await bot.send_message(msg.from_user.id, _("Введите название товара"), reply_markup=create_article_default_markup)
    await CreateArticleStates.TITLE.set()
    # print(article)
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.PRICE)
@dp.message_handler(state=CreateArticleStates.TITLE)
async def __select_title(msg: Message, state: FSMContext):
    data = await state.get_data()
    # print(type(jsonpickle.decode(data['article'])))
    # print(json.loads(jsonpickle.decode(data['article'])))
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.title = msg.text.replace(_("Пропустить ➡️"), "").replace(_("⬅️ Назад"), "")
    await bot.send_message(msg.from_user.id, _("Введите описание товара"), reply_markup=create_article_default_markup)
    await CreateArticleStates.DESCRIPTION.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.PHOTO)
@dp.message_handler(state=CreateArticleStates.DESCRIPTION)
async def __select_description(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.description = msg.text.replace(_("Пропустить ➡️"), "").replace(_("⬅️ Назад"), "")
    if article.type == _("❗️ Продам"):
        await bot.send_message(msg.from_user.id, _("Введите цену товара"), reply_markup=create_article_default_markup)
        await CreateArticleStates.PRICE.set()
    else:
        await bot.send_message(msg.from_user.id, _("Добавьте фото"), reply_markup=create_article_default_markup)
        article.price = ""
        await CreateArticleStates.PHOTO.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.LOCATION)
@dp.message_handler(state=CreateArticleStates.PRICE)
async def __select_price(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.price = msg.text.replace(_("Пропустить ➡️"), "").replace(_("⬅️ Назад"), "")
    await bot.send_message(msg.from_user.id, _("Добавьте фото"), reply_markup=create_article_default_markup)
    await CreateArticleStates.PHOTO.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(content_types=ContentTypes.ANY, state=CreateArticleStates.PHOTO)
@media_group_handler
async def album_handler(messages: List[Message]):
    await messages[-1].reply_media_group(
        [
            InputMediaPhoto(
                media=m.photo[-1].file_id,
                caption=m.caption,
                caption_entities=m.caption_entities,
            )
            for m in messages
        ]
    )

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.NICKNAME)
# @dp.message_handler(content_types=ContentTypes.ANY, state=CreateArticleStates.PHOTO)
@dp.message_handler(MediaGroupFilter(is_media_group=True),content_types=ContentType.PHOTO, state=CreateArticleStates.PHOTO)
# @dp.message_handler(content_types=['photo'])
@media_group_handler
async def __select_photo(msg: Message,state: FSMContext):
    # print(media_group_id)
    images_list = []
    # print(message)
    # print(msg)
    # if album:
    #     if album.photo:
    #         file_id = obj.photo[-1].file_id
    #         images_list.append(file_id)
    #     else:
    #         for obj in album:
    #             if obj.photo:
    #                 file_id = obj.photo[-1].file_id
    #                 images_list.append(file_id)
    #     user_id = album[0].from_user.id
    if msg.photo:
        user_id = msg.from_user.id
        file_id = msg.photo[-1].file_id
        images_list.append(file_id)
    # else: 
    #     return
    print(images_list)
    images = {'images': images_list}
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.photo = json.dumps(images)
    await bot.send_message(user_id, _("Укажите населенный пункт и индекс"), reply_markup=create_article_default_markup)
    await CreateArticleStates.LOCATION.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.MOBILE)
@dp.message_handler(state=CreateArticleStates.LOCATION)
async def __select_location(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    article.location = msg.text.replace(_("Пропустить ➡️"), "").replace(_("⬅️ Назад"), "")
    username = msg.from_user.username
    text = _("Введите логин телеграм (начинается с @).\nНажмите 'Пропустить', что б автоматически указать логин вашего профиля")
    await bot.send_message(msg.from_user.id, text, reply_markup=create_article_default_markup)
    await CreateArticleStates.NICKNAME.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(Text(equals=[_("⬅️ Назад")]), state=CreateArticleStates.MOBILE)
@dp.message_handler(state=CreateArticleStates.NICKNAME)
async def __select_nickname(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    if msg.text not in(_("Пропустить ➡️"), _("⬅️ Назад")) and msg.text.startswith('@'):
        article.username = msg.text
    else:
        article.username = f"@{msg.from_user.username}"
    user: User = await db.get_user(msg.from_user.id)
    article.mobile_number = user.mobile
    text = _("Введите номер телефона.\nНажмите 'Пропустить', что б использовать указанный вами номер: {}".format(user.mobile))
    await bot.send_message(msg.from_user.id, text, reply_markup=create_article_default_markup)
    await CreateArticleStates.MOBILE.set()
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))

@dp.message_handler(state=CreateArticleStates.MOBILE)
async def __select_phone(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    if msg.text not in(_("Пропустить ➡️"), _("⬅️ Назад")) and msg.text.startswith('+'):
        article.mobile_number = msg.text
    await state.update_data(article=json.dumps(jsonpickle.encode(article, unpicklable=False)))
    await bot.send_message(msg.from_user.id, _("Готово! Вы можете посмотреть объявление:"), reply_markup=ReplyKeyboardRemove())
    text = get_sample_from_article(article)
    # article_photos = article.photo
    photos = json.loads(article.photo)['images']
    if len(photos) > 0:
        await bot.send_media_group(msg.from_user.id, media=[InputMediaPhoto(m, caption=text if key == 0 else "",  parse_mode="HTML") for key, m in enumerate(photos)])
    else:
        await bot.send_message(msg.from_user.id, text)
    await bot.send_message(msg.from_user.id, _("Подтвердить? (Да/Нет)"), reply_markup=accept_create_article)
    await CreateArticleStates.CHECK.set()

@dp.message_handler(state=CreateArticleStates.CHECK)
async def __accept_article(msg: Message, state: FSMContext):
    data = await state.get_data()
    article: Article = Article(**json.loads(jsonpickle.decode(data['article']))['__values__'])
    if msg.text == _("Да"):
        article.created_at = datetime.now()
        is_duplicate = await db.check_article_duplicate(article)
        if str(msg.from_user.id) in ADMIN_ID:
            article.is_approved=True
            article.is_reviewed=True
            article.reviewed_at = datetime.now()
            article = await article.create()   
            await send_article_to_chanel(article)
            message = _("Ваш пост опубликован в канале")
            markup = admin_main_menu_markup
        elif is_duplicate and str(msg.from_user.id) not in ADMIN_ID:
            message = _("Публикация одинаковых постов запрещена.\nПопробуйте по-другому 🤓")
            markup = user_main_menu_markup
        else:
            article = await article.create()   
            message = _("Ваш пост отправлен на модерацию.\nКак только он будет проверен Администратором, вы получите уведомление")
            markup = user_main_menu_markup
        await bot.send_message(msg.from_user.id, message, reply_markup=markup)
    elif msg.text == _("Нет"):
        await bot.send_message(msg.from_user.id, _("Создание поста отменено"), reply_markup=admin_main_menu_markup if str(msg.from_user.id) in ADMIN_ID else user_main_menu_markup)
    await state.reset_state()
    await state.reset_data()

@dp.message_handler(Text(equals=[_("Мои объявления")]))
async def __my_articles(msg: Message):
    articles: List[Article] | None = await db.get_user_articles(msg.from_user.id)
    articles.sort(key=lambda x: x.id)
    if len(articles) > 0:
        for key, article in enumerate(articles):
            await send_article_to_chanel(article, msg.from_user.id)
    else:
        await bot.send_message(_('У вас нет активных объявлений 🥺'))

@dp.message_handler(Text(equals=[_("Язык")]))
async def __change_language(msg: Message, state: FSMContext):
    await bot.send_message(msg.from_user.id, "♻️", reply_markup=ReplyKeyboardRemove())
    await bot.send_message(msg.from_user.id, _("Выбери язык"), reply_markup=choose_new_language)
    await state.set_data({"change_language":True})

@dp.message_handler(Text(equals=[_("Номер телефона")]))
async def __change_language(msg: Message, state: FSMContext):
    await bot.send_message(msg.from_user.id, _("Введите номер"), reply_markup=send_tel_number_markup)
    await state.set_data({"change_number":True})
    await RegistrationStates.NUMBER.set()



    # await bot.send_sticker(msg.from_user.id, sticker="CAACAgIAAxkBAAIJQWSO2SepS6soZ_x0oaMce-r6Vd4QAAJxDgACHIJQS-TTUGYws97lLwQ")
    

