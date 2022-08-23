from aiogram.types import ReplyKeyboardMarkup


default_kb = ReplyKeyboardMarkup(
    resize_keyboard=True, keyboard=[
        ["Мои группы"],
        ["❓ Помощь", "Управление группами"],
    ]
)
