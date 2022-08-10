from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


edit_menu_inline_keyboard = InlineKeyboardMarkup( 
    inline_keyboard=[[InlineKeyboardButton("Удалить", callback_data="delete")]]
)

manage_own_group_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Удалить лекцию", callback_data="delete_lecture"),
            InlineKeyboardButton("Добавить лекцию", callback_data="add_lecture")      
        ],
    ]
)
# edit_menu_inline_keyboard.add(InlineKeyboardButton("Изменить", callback_data='change'))
# edit_menu_inline_keyboard.add(InlineKeyboardButton("Выбрать другую лекцию", callback_data='back'))
