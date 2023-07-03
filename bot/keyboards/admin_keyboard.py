from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,InlineKeyboardButton, ReplyKeyboardRemove
from bot.config import ADMIN_ID
from bot.loader import _
from aiogram.types import Message

admin_main_menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=_("Мои объявления")),
            KeyboardButton(text=_("Создать объявление 🆕"))
        ],
        [
            KeyboardButton(text=_("Настройки ⚙️")),
            KeyboardButton(text=_("Модерация")),
            KeyboardButton(text=_("Статистика")),
        ]
    ],
    resize_keyboard=True
)

moderate_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="👎"),
            KeyboardButton(text="👍")
        ],
        [
            KeyboardButton(text=_("❌ Отменить"))
        ]
    ],
    resize_keyboard=True
)

settings_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=_("Язык")),
            KeyboardButton(text=_("Номер телефона")),
            KeyboardButton(text=_("Режим работы бота"))
        ],
        [
            KeyboardButton(text=_("❌ Отменить"))
        ]
    ],
    resize_keyboard=True
)

work_mode_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=_("Ручной")),
            KeyboardButton(text=_("Автоматический"))
        ],
        [
            KeyboardButton(text=_("❌ Отменить"))
        ]
    ],
    resize_keyboard=True
)

def get_lang_markup(lang, msg):
    print(lang, msg)
    admin_main_menu_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Мои объявления", locale=lang)),
                KeyboardButton(text=_("Создать объявление 🆕", locale=lang))
            ],
            [
                KeyboardButton(text=_("Настройки ⚙️", locale=lang)),
                KeyboardButton(text=_("Модерация", locale=lang)),
                KeyboardButton(text=_("Статистика", locale=lang)),
            ]
        ],
        resize_keyboard=True
    )
    user_main_menu_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Настройки ⚙️", locale=lang)),
                KeyboardButton(text=_("Мои объявления", locale=lang))
            ],
            [
                KeyboardButton(text=_("Создать объявление 🆕", locale=lang))
            ]
        ],
        resize_keyboard=True
    )   
    return admin_main_menu_markup if str(msg.from_user.id) in ADMIN_ID else user_main_menu_markup