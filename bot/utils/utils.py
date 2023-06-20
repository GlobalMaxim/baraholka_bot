import json
from aiogram.types import Message, CallbackQuery, photo_size, ContentTypes, ContentType, ReplyKeyboardRemove, InputMediaPhoto

from bot.loader import dp, bot, _
from bot.database.database import Article
from bot.config import CHANEL_ID
import redis


class EmptyArticleException(Exception):
    pass

class BadWordsException(Exception):
    pass



redis_client = redis.Redis()

def set_work_mode(mode):
    with redis.Redis() as redis_client:
        redis_client.set('work_mode',mode)

async def send_article_to_chanel(article:Article, channel_id=CHANEL_ID):
    text = get_sample_from_article(article)
    article_number_text = _("Лот № {}\n\n").format(article.id)
    text = article_number_text + text
    # article_photos = article.photo
    photos = json.loads(article.photo)['images']
    if len(photos) > 0:
        await bot.send_media_group(channel_id, media=[InputMediaPhoto(m, caption=text if key == 0 else "",  parse_mode="HTML") for key, m in enumerate(photos)])
    else:
        await bot.send_message(channel_id, text)

def get_sample_from_article(article: Article):
    text_arr = []
    art_type = ""
    match article.type:
        case "❗️ Продам":
            art_type = article.type + " / zu Verkaufen ❗️"
        case "❕ Отдам":
            art_type = article.type + " / zu verschenken ❕"
        case "❓ Ищу":
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
    print(article.username)
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
    is_duplicate = await db.check_article_duplicate(article)
    if not article.title:
        raise EmptyArticleException
    
    words = ['сука', "шлюха", "блят", "пидор", "лох", " бля ", "гандон", "бляд", "ёб", "хуй", "доеб"]
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
                raise BadWordsException