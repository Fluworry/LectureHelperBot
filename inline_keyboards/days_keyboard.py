from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

choose_days_inline_keyboard = InlineKeyboardMarkup(row_width=4)

days_buttons = {
    'mon': "Пн", 'tue': "Вт", 'wed': "Ср",
    'thu': "Чт", 'fri': "Пт", 'sat': "Сб",
    'sun': "Вс"}
inverted_days_buttons = {day_text: day_callback for day_callback, day_text in days_buttons.items()}

for btn_callback, btn_text in days_buttons.items():
    choose_days_inline_keyboard.insert(InlineKeyboardButton(btn_text, callback_data=btn_callback))

choose_days_inline_keyboard.row(InlineKeyboardButton("Готово", callback_data="done"))
