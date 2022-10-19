from loader import bot


async def send_notification(
    title: str, description: str, user_ids: list[int]
):
    for user_id in user_ids:
        await bot.send_message(
            chat_id=user_id, parse_mode='html',
            text=f"Уведомление о начале лекции:\n\n\n"
            f"<b>{title}</b>\n\n{description}"
        )
