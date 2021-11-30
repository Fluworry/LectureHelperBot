from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_pressed_inline_button(inline_keyboard, callback_data, row_count=2):
    selected_button = {}

    for row in range(row_count):
        current_row = tuple(dict(inline_keyboard[row]).values())
        if ('callback_data', callback_data) in current_row:
            selected_button_index = tuple(dict(inline_keyboard[row]).values()).index(
                ('callback_data', callback_data))
            selected_button = inline_keyboard[row][selected_button_index]

    return selected_button
