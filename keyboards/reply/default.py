from aiogram.types import ReplyKeyboardMarkup


default_kb = ReplyKeyboardMarkup(
    resize_keyboard=True, keyboard=[
        ["My groups"],
        ["❓ Help", "Configure groups"],
    ]
)
