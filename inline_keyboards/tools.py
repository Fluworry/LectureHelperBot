from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_pressed_inline_button(inline_keyboard, callback_data, row_count=2) -> dict:
    pressed_inline_button = {}

    for row in range(row_count):
        current_row = tuple(dict(inline_keyboard[row]).values())
        if ('callback_data', callback_data) in current_row:
            pressed_button_index = tuple(dict(inline_keyboard[row]).values()).index(
                ('callback_data', callback_data))
            pressed_inline_button = inline_keyboard[row][pressed_button_index]

    return pressed_inline_button


def get_selected_inline_days(inline_keyboard, row_count=2) -> list:
    all_days = []
    selected_days = []

    for row in range(row_count):
        all_days += list(dict(inline_keyboard[row]).keys())

    for day in all_days:
        if day[1].endswith('✅'):
            selected_days.append(day[1].replace('✅', '').rstrip())

    return selected_days
