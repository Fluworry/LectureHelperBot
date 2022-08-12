from aiogram.types import InlineKeyboardMarkup


def get_selected_buttons(
        keyboard: InlineKeyboardMarkup
    ) -> dict[int, str]:

    selected_buttons = {}

    for row in keyboard.inline_keyboard:
        for button in row:
            if ':' not in button.callback_data:
                continue
            
            callback_id, callback_status = button.callback_data.split(':')

            if callback_status == 't':
                selected_buttons[int(callback_id)] = button.text.replace("✅", "")

    return selected_buttons