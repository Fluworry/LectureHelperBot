from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

choose_days_inline_keyboard = InlineKeyboardMarkup(row_width=4)

days_buttons = {
    'monday': "Пн", 'tuesday': "Вт", 'wednesday': "Ср",
    'thursday': "Чт", 'friday': "Пт", 'saturday': "Сб",
    'sunday': "Вс"}
days_buttons.keys()

for btn_callback, btn_text in days_buttons.items():
    choose_days_inline_keyboard.insert(InlineKeyboardButton(btn_text, callback_data=btn_callback))

choose_days_inline_keyboard.row(InlineKeyboardButton("Готово", callback_data="done"))
