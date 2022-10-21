from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.utils import markdown

from sqlalchemy.ext.asyncio import AsyncSession
from loader import SOURCE_CODE_LINK

from keyboards.reply.default import default_kb
from services.repositories import Repos, UserRepo, GroupRepo


async def start_command(
    message: types.Message, session: AsyncSession, repo: Repos
):
    invite_token = message.get_args()
    user = await repo.get_repo(UserRepo).add(message.from_user.id)

    if invite_token:
        await repo.get_repo(GroupRepo).add_user(user, invite_token)

    await session.commit()

    await message.answer(
        parse_mode='markdown', reply_markup=default_kb,
        text="Данный бот рассылает уведомления о начале лекций "
        "всем участникам группы.\n"
        "Пригласите бота в чат, чтобы создать собственную группу."
        "Если вы хотите вступить в группу, "
        "перейдите по пригласительной ссылке.\n\n"
        f"{markdown.link('Исходный код', SOURCE_CODE_LINK)}"
    )


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(
        start_command, ChatTypeFilter("private"),
        state='*', commands=['start']
    )
