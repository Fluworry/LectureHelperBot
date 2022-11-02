from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


edit_menu_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton("Удалить", callback_data="delete")]]
)

manage_own_group_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                "Delete the event", callback_data="delete_event"
            ),
            InlineKeyboardButton(
                "Add new event", callback_data="add_event"
            )
        ],
    ]
)
