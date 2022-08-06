from aiogram import types
from aiogram.utils import markdown
from aiogram.utils.deep_linking import get_start_link
from keyboards import reply, inline

from uuid import uuid4
from loader import SOURCE_CODE_LINK

from db.models import User, Group
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError, NoResultFound


async def start_command(message: types.Message):
    invite_token = message.get_args()
    
    db_session = message.bot.get("db")

    async with db_session() as session:
        try:
            user = User(user_id=message.from_user.id)
            session.add(user)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            stmt = select(User).where(
                User.user_id == message.from_user.id
            )
            
            result = await session.execute(stmt)
            user = result.scalar()

        if invite_token:
            stmt = select(Group).where(
                Group.invite_token == invite_token
            ).options(selectinload(Group.users))

            result = await session.execute(stmt)
            group = result.scalar()

            if group is not None:
                group.users.append(user)
                await session.commit()

    await message.answer(parse_mode='markdown', reply_markup=reply.main_menu,
                         text="Данный бот рассылает уведомления о начале лекций всем участникам группы.\n"
                              "Пригласите бота в чат, чтобы создать собственную группу."
                              "Если вы хотите вступить в группу, перейдите по пригласительной ссылке.\n\n"
                              f"{markdown.link('Исходный код', SOURCE_CODE_LINK)}")


async def create_group(member: types.ChatMemberUpdated):
    if member.new_chat_member.status != 'member':  # TODO: make custom filter
        return

    db_session = member.bot.get("db")
    
    async with db_session() as session:
        stmt = select(Group).where(Group.chat_id == member.chat.id)
        result = await session.execute(stmt)
        current_group = result.scalar()

        if current_group is None:
            invite_token = uuid4().hex[:15]

            try:
                stmt = select(User).where(
                    User.user_id == member.from_user.id
                ).options(selectinload(User.groups))
                
                result = await session.execute(stmt)
                owner = result.scalar_one()
            except NoResultFound:
                owner = User(user_id=member.from_user.id)
                session.add(owner)
                await session.commit()
                await session.refresh(owner)

            current_group = Group(
                name=member.chat.title, invite_token=invite_token, 
                chat_id=member.chat.id, owner_id=owner.id
            )
            session.add(current_group)
            owner.groups.append(current_group)
        else:
            invite_token = current_group.invite_token

        await session.commit()
    
    invite_link = await get_start_link(invite_token)
    await member.bot.send_message(chat_id=member.chat.id, parse_mode="html",
        text="Данный бот рассылает уведомления о начале лекции.\n\n"
            "Перейдите по пригласительной ссылке, чтобы получать уведомления о начале лекций:\n"
            f"{invite_link}\n\n"
            "Если вы пригласили бота в этот чат, вы можете добавить новые лекции в меню бота.\n\n"
            f"<a href='{SOURCE_CODE_LINK}'>Исходный код</a>")
