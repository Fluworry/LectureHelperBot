from aiogram import types
from aiogram.utils import markdown
from aiogram.utils.deep_linking import get_start_link

from keyboards.reply.default import default_kb
from loader import SOURCE_CODE_LINK

from sqlalchemy.ext.asyncio import AsyncSession
from db.requests import add_group, add_user, add_user_to_group


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


async def create_group(member: types.ChatMemberUpdated, session: AsyncSession):
    if member.new_chat_member.status != 'member':  # TODO: make custom filter
        return

    group = await add_group(
        session, member.chat.title, 
        member.from_user.id, member.chat.id
    )
    
    invite_link = await get_start_link(group.invite_token)
    await session.commit()
    
    await member.bot.send_message(chat_id=member.chat.id, parse_mode="html",
        text="Данный бот рассылает уведомления о начале лекции.\n\n"
            "Перейдите по пригласительной ссылке, чтобы получать уведомления о начале лекций:\n"
            f"{invite_link}\n\n"
            "Если вы пригласили бота в этот чат, вы можете добавить новые лекции в меню бота.\n\n"
            f"<a href='{SOURCE_CODE_LINK}'>Исходный код</a>")
