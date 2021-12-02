from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

edit_menu_buttons = {'delete': "Удалить"}

edit_menu_inline_keyboard = InlineKeyboardMarkup(row_width=3)

for btn_callback, btn_text in edit_menu_buttons.items():
    edit_menu_inline_keyboard.insert(InlineKeyboardButton(btn_text, callback_data=btn_callback))

# edit_menu_inline_keyboard.add(InlineKeyboardButton("Изменить", callback_data='change'))
# edit_menu_inline_keyboard.add(InlineKeyboardButton("Выбрать другую лекцию", callback_data='back'))
