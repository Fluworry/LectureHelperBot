from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.models import Group


def get_groups_kb(groups: list[Group]) -> InlineKeyboardMarkup:
    """ Generates keyboard from groups """
    groups_kb = InlineKeyboardMarkup()

    for group in groups:
        groups_kb.add(InlineKeyboardButton(
            group.name, callback_data=str(group.id)
        ))
    return groups_kb


def get_switchable_kb(
    entities: list, row_width=4, done_button_text="Готово"
) -> InlineKeyboardMarkup:

    """ Generates keyboard from db entities """
    entities_kb = InlineKeyboardMarkup(row_width)

    for entity in entities:
        entities_kb.insert(
            InlineKeyboardButton(entity.name, callback_data=f"{entity.id}:f")
        )
    entities_kb.row(InlineKeyboardButton(
        done_button_text, callback_data="done"
    ))

    return entities_kb


def update_switchable_kb(
    keyboard: InlineKeyboardMarkup, callback_data: str
) -> InlineKeyboardMarkup:

    for row in keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == callback_data:
                callback_id, callback_status = button.callback_data.split(':')

                if callback_status == 'f':
                    button.callback_data = f"{callback_id}:t"
                    button.text = "✅" + button.text
                else:
                    button.callback_data = f"{callback_id}:f"
                    button.text = button.text.replace("✅", "")

                return keyboard
