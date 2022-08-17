from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.deep_linking import get_start_link

from keyboards import generators
from keyboards.inline.manage import manage_own_group_kb
from loader import SOURCE_CODE_LINK

from states import LectureStates

from sqlalchemy.ext.asyncio import AsyncSession
from db.requests import get_user, get_group, add_group


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


async def select_group(message: types.Message, session: AsyncSession):
    user = await get_user(session, message.from_user.id)

    answer_message = "Выберите группу"

    if message.text == "Управление группами":
        await LectureStates.manage_own_group.set()
        groups_kb = generators.get_groups_kb(user.owned_groups)
        answer_message = "Выберите группу, чтобы добавить/убрать лекции"

    elif message.text == "Мои группы":
        await LectureStates.leave_group.set()
        groups_kb = generators.get_groups_kb(user.groups)
        answer_message = "Нажмите на группу, чтобы выйти из неё"
    
    await message.answer(answer_message, reply_markup=groups_kb)


async def show_group_settings(
    call: types.CallbackQuery, session: AsyncSession, 
    state: FSMContext
):

    selected_group = await get_group(session, int(call.data))

    await state.update_data({
        "selected_group_id": int(call.data), 
        "selected_group_name": selected_group.name
    })

    await call.answer("Вы выбрали группу")
    await call.message.edit_text(
        f"Опции для группы {selected_group.name}", 
        reply_markup=manage_own_group_kb
    )


async def leave_group(call: types.CallbackQuery, state: FSMContext):
    ...
