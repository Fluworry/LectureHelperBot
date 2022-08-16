from db.models import User
from loader import dp


async def lecture_notify(title, description, users: list[User]):
    for user in users:
        await dp.bot.send_message(
            chat_id=user.user_id, parse_mode='html', 
            text=f"Уведомление о начале лекции:\n\n\n"
            f"<b>{title}</b>\n\n{description}"
        )
