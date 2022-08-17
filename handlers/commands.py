from aiogram import types
from aiogram.utils import markdown

from keyboards.reply.default import default_kb
from loader import SOURCE_CODE_LINK

from sqlalchemy.ext.asyncio import AsyncSession
from db.requests import add_user, add_user_to_group


async def start_command(message: types.Message, session: AsyncSession):
    invite_token = message.get_args()
    user = await add_user(session, message.from_user.id)

    if invite_token:
        await add_user_to_group(session, user, invite_token)

    await session.commit()

    await message.answer(parse_mode='markdown', reply_markup=default_kb, 
        text="Данный бот рассылает уведомления о начале лекций всем участникам группы.\n"
            "Пригласите бота в чат, чтобы создать собственную группу."
            "Если вы хотите вступить в группу, перейдите по пригласительной ссылке.\n\n"
            f"{markdown.link('Исходный код', SOURCE_CODE_LINK)}")