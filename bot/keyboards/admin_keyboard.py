from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,InlineKeyboardButton, ReplyKeyboardRemove
from bot.loader import _

admin_main_menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=_("Мои объявления")),
            KeyboardButton(text=_("Создать объявление"))
        ],
        [
            KeyboardButton(text=_("Настройки")),
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