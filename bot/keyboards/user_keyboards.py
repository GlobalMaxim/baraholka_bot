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

send_tel_number_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=_("Отправить номер"), request_contact=True)
        ]
    ],
    resize_keyboard=True
)

user_main_menu_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=_("Настройки")),
            KeyboardButton(text=_("Мои объявления"))
        ],
        [
            KeyboardButton(text=_("Создать объявление"))
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
