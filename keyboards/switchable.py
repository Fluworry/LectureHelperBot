from aiogram.types import InlineKeyboardMarkup


def update_switchable_kb(
    keyboard: InlineKeyboardMarkup, callback_data: str
) -> InlineKeyboardMarkup:

    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == callback_data:
                if "✅" in button.text:
                    button.text = button.text.replace("✅", "")
                else:
                    button.text = "✅" + button.text

                return keyboard


def get_selected_buttons(
        keyboard: InlineKeyboardMarkup
) -> dict[int, str]:

    selected_buttons = {}

    for row in keyboard.inline_keyboard:
        for button in row:
            if "✅" in button.text:
                selected_buttons[
                    int(button.callback_data)
                ] = button.text.replace("✅", "")

    return selected_buttons
