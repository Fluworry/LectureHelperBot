from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


edit_menu_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton("Удалить", callback_data="delete")]]
)

manage_own_group_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                "Удалить событие", callback_data="delete_event"
            ),
            InlineKeyboardButton(
                "Добавить событие", callback_data="add_event"
            )
        ],
    ]
)
