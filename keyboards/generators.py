from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.models import Group, WeekDay


def get_weekdays_kb(weekdays: list[WeekDay]):
    """ Generates menu from weekdays """
    weekdays_kb = InlineKeyboardMarkup(row_width=4)

    for weekday in weekdays:
        weekdays_kb.insert(
            InlineKeyboardButton(weekday.name, callback_data=f"{weekday.id}:f")
        )
    weekdays_kb.row(InlineKeyboardButton("Готово", callback_data="done"))

    return weekdays_kb


def get_groups_kb(groups: list[Group]) -> InlineKeyboardMarkup:
    """ Generates keyboard from groups """
    groups_kb = InlineKeyboardMarkup()

    for group in groups:
        groups_kb.add(InlineKeyboardButton(group.name, callback_data=str(group.id)))
    return groups_kb


def get_toggled_weekdays_kb(days_keyboard: InlineKeyboardMarkup, callback_data: str):
    day_id = callback_data.split(':')[0]
    button_status = callback_data.split(':')[1]
    
    if button_status == 'f':
        toggled_callback_data = f"{day_id}:t"
    else:
        toggled_callback_data = f"{day_id}:f"

    for row in days_keyboard.inline_keyboard:
        for button in row:
            if button.callback_data == callback_data:
                button.callback_data = toggled_callback_data

                if button.text[-1] == "✅":
                    button.text = button.text.replace("✅", "")
                else:
                    button.text = button.text + "✅"

                return days_keyboard
