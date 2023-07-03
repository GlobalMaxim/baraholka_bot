from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup,InlineKeyboardButton, ReplyKeyboardRemove
from bot.loader import _

choose_language = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [   
                InlineKeyboardButton(text="🇺🇦Україньска", callback_data="lang_uk"),
                InlineKeyboardButton(text="Русский", callback_data="lang_ru")
            ],
            [
                InlineKeyboardButton(text="🇬🇧English", callback_data="lang_en"),
                InlineKeyboardButton(text="🇩🇪Deutsch", callback_data="lang_de")
                
            ]
        ]
    )

choose_new_language = InlineKeyboardMarkup(
        inline_keyboard=
        [
            [   
                InlineKeyboardButton(text="🇺🇦Україньска", callback_data="new_lang_uk"),
                InlineKeyboardButton(text="Русский", callback_data="new_lang_ru")
            ],
            [
                InlineKeyboardButton(text="🇬🇧English", callback_data="new_lang_en"),
                InlineKeyboardButton(text="🇩🇪Deutsch", callback_data="new_lang_de")
                
            ]
        ]
    )

def get_tel_number(lang):
    send_tel_number_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Отправить номер", locale=lang), request_contact=True)
            ]
        ],
        resize_keyboard=True
    )
    return send_tel_number_markup

user_main_menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=_("Создать объявление 🆕"))
        ],
        [
            KeyboardButton(text=_("Настройки ⚙️")),
            KeyboardButton(text=_("Мои объявления"))
        ]
        
    ],
    resize_keyboard=True
)

select_article_type_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("❗️ Продам"))
            ],
            [
                KeyboardButton(text=_("❕ Отдам")),
                KeyboardButton(text=_("❓ Ищу"))
            ],
            [
                KeyboardButton(text=_("❌ Отменить"))
            ]

        ],
        resize_keyboard=True
    )
# def get_create_article_default_markup()
create_article_default_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Пропустить ➡️")),
                
            ],
            [
                KeyboardButton(text=_("⬅️ Назад")),
                KeyboardButton(text=_("❌ Отменить"))
            ]
        ],
        resize_keyboard=True
    )

geoposition_markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Отправить местоположение 📍"),request_location=True)
            ],
            [
                KeyboardButton(text=_("⬅️ Назад")),
                KeyboardButton(text=_("Пропустить ➡️")),
                KeyboardButton(text=_("❌ Отменить"))
            ]
        ],
        resize_keyboard=True
    )

accept_create_article = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=_("Да")),
                KeyboardButton(text=_("Нет"))
            ]
        ],
        resize_keyboard=True
    )

user_settings_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=_("Язык")),
            KeyboardButton(text=_("Номер телефона"))
        ],
        [
            KeyboardButton(text=_("❌ Отменить"))
        ]
    ],
    resize_keyboard=True
)
