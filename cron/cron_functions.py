from loader import dp


async def lecture_notify(title, description, chat_id):
    await dp.bot.send_message(chat_id=chat_id, parse_mode='html',
                           text=f"Уведомление о начале лекции:\n\n\n"
                                f"<b>{title}</b>\n\n"
                                f"{description}")
