from datetime import datetime, timedelta
import json
from typing import List
from aiogram.types import Message, CallbackQuery, photo_size, ContentTypes, ContentType, ReplyKeyboardRemove, InputMediaPhoto

from bot.loader import dp, bot, _
from bot.database.database import Article, DBCommands
from bot.config import ADMIN_ID, CHANEL_ID
import redis
import logging


class EmptyArticleException(Exception):
    pass

class BadWordsException(Exception):
    pass

logger = logging.getLogger('utils')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="bot/logs/utils.log")
formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# redis_client = redis.Redis()
db = DBCommands()

redis_client = redis.Redis()

def set_work_mode(mode):
    try:
        with redis.Redis() as redis_client:
            redis_client.set('work_mode',mode)
    except Exception:
        logger.exception('Cannot change work mode')

async def send_article_to_chanel(article:Article, channel_id=CHANEL_ID):
    try:
        text = get_sample_from_article(article)
        article_number_text = _("Лот № {}\n\n").format(article.id)
        text = article_number_text + text
        # article_photos = article.photo
        photos = json.loads(article.photo)['images']
        if len(photos) > 0:
            return await bot.send_media_group(channel_id, media=[InputMediaPhoto(m, caption=text if key == 0 else "",  parse_mode="HTML") for key, m in enumerate(photos)])
        else:
            return await bot.send_message(channel_id, text)
    except Exception:
        logger.exception('Send article to channel exception')

def get_sample_from_article(article: Article):
    text_arr = []
    art_type = ""
    if article.type == str(_("❗️ Продам")):
        art_type = article.type + " / zu Verkaufen ❗️"
    elif article.type == str(_("❕ Отдам")):
        art_type = article.type + " / zu verschenken ❕"
    elif article.type == str(_("❓ Ищу")):
        art_type = article.type + " / zu suchen ❓"
    text_arr.append(f"{art_type}\n")
    if article.title:
        text_arr.append(f"{article.title}\n")
    if article.description:
        text_arr.append(f"{article.description}\n")
    if article.price:
        text_arr.append(f"{_('Цена: ')}{article.price}\n")
    if article.location:
        text_arr.append(f"{_('Местоположение: ')}{article.location}\n")
    if article.mobile_number:
        text_arr.append(f"{_('Номер: ')}{article.mobile_number}\n")
    # print(article.username)
    if article.username and article.username != "@None":
        text_arr.append(article.username)
    text = "\n".join(text_arr)
    return text

def distance(a, b): 
        n, m = len(a), len(b)
        if n > m:
        
            a, b = b, a
            n, m = m, n

        current_row = range(n + 1)
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if a[j - 1] != b[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)

        return current_row[n]

async def check_article_for_errors(article: Article):
    db = DBCommands()
    
    if (not article.title and not article.description):
        return _("Обьявление заполнено не полностью.\nНужно переделать 🐈")
    
    if (not article.mobile_number and not article.username):
        return _("Вы не указали контактные данные. 🥴\nЗаполните номер телефона или имя пользователя")

    try:
        await db.check_article_duplicate(article)
    except:
        return _("Публикация одинаковых постов запрещена.\nПопробуйте по-другому 🤓")
    
    words = ['сука', "шлюх", "блят", "пидор", "лох", "бля", "гандон", "бляд", "ёб", "хуй", "доеб", "пидр"]
    text = get_sample_from_article(article)
    phrase = text.lower()

    d =   {'а' : ['а', 'a', '@'],
    'б' : ['б', '6', 'b'],
    'в' : ['в', 'b', 'v'],
    'г' : ['г', 'r', 'g'],
    'д' : ['д', 'd'],
    'е' : ['е', 'e'],
    'ё' : ['ё', 'e'],
    'ж' : ['ж', 'zh', '*'],
    'з' : ['з', '3', 'z'],
    'и' : ['и', 'u', 'i'],
    'й' : ['й', 'u', 'i', 'y'],
    'к' : ['к', 'k', 'i{', '|{'],
    'л' : ['л', 'l', 'ji'],
    'м' : ['м', 'm'],
    'н' : ['н', 'h', 'n'],
    'о' : ['о', 'o', '0'],
    'п' : ['п', 'n', 'p'],
    'р' : ['р', 'r', 'p'],
    'с' : ['с', 'c', 's'],
    'т' : ['т', 'm', 't'],
    'у' : ['у', 'y', 'u'],
    'ф' : ['ф', 'f'],
    'х' : ['х', 'x', 'h' , '}{'],
    'ц' : ['ц', 'c', 'u,'],
    'ч' : ['ч', 'ch'],
    'ш' : ['ш', 'sh'],
    'щ' : ['щ', 'sch'],
    'ь' : ['ь', 'b'],
    'ы' : ['ы', 'bi'],
    'ъ' : ['ъ'],
    'э' : ['э', 'e'],
    'ю' : ['ю', 'io'],
    'я' : ['я', 'ya']
    }

    for key, value in d.items():
        for letter in value:
            for phr in phrase:
                if letter == phr:
                    phrase = phrase.replace(phr, key)

    for word in words:
        for part in range(len(phrase)):
            fragment = phrase[part: part+len(word)]
            if distance(fragment, word) <= len(word)*0.15:
                return _("В статье нельзя использовать маты 👊")
    return

async def send_notification_to_admin_about_new_post():
    try:
        articles: List[Article] = await db.get_non_reviewed_articles()
        if articles and len(articles) > 0:
            with redis.Redis() as redis_client:
                last_sent_notification = redis_client.get('last_sent_notification')
                last_moderation = redis_client.get('last_moderation')
                is_notif_in_2_hrs = int(redis_client.get('is_notificated_in_2_hrs')) == 1
                # print(is_notif_in_2_hrs)
            last_sent_notification_date = datetime.strptime(last_sent_notification.decode('utf-8'), "%Y-%m-%d %H:%M:%S") if last_sent_notification else None 
            last_moderation_date = datetime.strptime(last_moderation.decode('utf-8'), "%Y-%m-%d %H:%M:%S") if last_moderation else None 
            
            # set_last_notification_time()
            # prev_time_2_hrs = datetime.now() - timedelta(hours=2)
            prev_time_2_hrs = datetime.now() - timedelta(minutes=5)
            prev_time_24_hrs = datetime.now() - timedelta(hours=24)
            if last_sent_notification_date and last_sent_notification_date < prev_time_24_hrs:
                print('1')
                for admin in ADMIN_ID:
                    await bot.send_message(admin, _("У вас {} новых объявлений.\nЗайдите в модерацию для проверки.").format(len(articles)))
                    set_last_notification_time()
            elif last_sent_notification_date is None:
                print('2')
                for admin in ADMIN_ID:
                    await bot.send_message(admin, _("У вас {} новых объявлений.\nЗайдите в модерацию для проверки.").format(len(articles)))
                    set_last_notification_time()
            elif last_sent_notification_date < prev_time_2_hrs and not is_notif_in_2_hrs:
                print('3')
                for admin in ADMIN_ID:
                    await bot.send_message(admin, _("У вас {} новых объявлений.\nЗайдите в модерацию для проверки.").format(len(articles)))
                    set_last_notification_time()
                with redis.Redis() as redis_client:
                    redis_client.set('is_notificated_in_2_hrs', int(True))
            elif last_moderation_date and last_moderation_date > last_sent_notification_date:
                print('4')
                for admin in ADMIN_ID:
                    await bot.send_message(admin, _("У вас {} новых объявлений.\nЗайдите в модерацию для проверки.").format(len(articles)))
                    set_last_notification_time()
    except Exception:
        logger.exception('Send notification to admin about new post exception')

def set_last_moderation_time():
    try:
        with redis.Redis() as redis_client:
            cur_datetime = datetime.now()
            redis_client.set('last_moderation', cur_datetime.strftime("%Y-%m-%d %H:%M:%S"))
            redis_client.set('is_notificated_in_2_hrs', int(False))
        # last_moderation = redis_client.get('last_moderation')
    except Exception:
        logger.exception('Set last moderation time exception')

def set_last_notification_time():
    try:
        with redis.Redis() as redis_client:
            cur_datetime = datetime.now()
            redis_client.set('last_sent_notification', cur_datetime.strftime("%Y-%m-%d %H:%M:%S"))
    except Exception:
        logger.exception('Set last notification time exception')
