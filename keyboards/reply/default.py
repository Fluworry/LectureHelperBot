from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton


# main_menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
#     [KeyboardButton('📒 Расписание лекций'), KeyboardButton('🔔 Уведомления')],
#     [KeyboardButton('🔬 Мои курсы'), KeyboardButton('❓ Помощь')],
#     ])

default_kb = ReplyKeyboardMarkup(
    resize_keyboard=True, keyboard=[
        ["Мои группы"],
        ["Управление группами", "Создать группу"],
        ["❓ Помощь"],
    ]
)
