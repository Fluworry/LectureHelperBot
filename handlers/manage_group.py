import os

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text, ChatTypeFilter
from aiogram.dispatcher import FSMContext
from aiogram.utils.deep_linking import get_start_link

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import generators
from keyboards.inline.manage import manage_own_group_kb

from states.event import EventStates
from services.repositories import Repos, UserRepo, GroupRepo


SOURCE_CODE_LINK = os.getenv("SOURCE_CODE_LINK")


async def create_group(
    member: types.ChatMemberUpdated, session: AsyncSession, repo: Repos
):
    if member.new_chat_member.status != 'member':  # TODO: make custom filter
        return

    group = await repo.get_repo(GroupRepo).add(
        member.chat.title, member.from_user.id, member.chat.id
    )

    invite_link = await get_start_link(group.invite_token)
    await session.commit()

    await member.bot.send_message(
        chat_id=member.chat.id, parse_mode="html",
        text="This bot notifies you about upcoming events.\n"
        "Follow the invitation link "
        f"to start receiving notifications:\n{invite_link}\n\n"
        "Also you can add new events from the bot menu.\n"
        f"<a href='{SOURCE_CODE_LINK}'>Source code</a>",
        disable_web_page_preview=True
    )


async def select_group(
    message: types.Message, session: AsyncSession, repo: Repos
):
    user = await repo.get_repo(UserRepo).get(message.from_user.id)

    answer_message = "Select a group"

    if message.text == "Configure groups":
        await EventStates.manage_own_group.set()
        groups_kb = generators.get_groups_kb(user.owned_groups)
        answer_message = "Select a group to add or remove events"

    elif message.text == "My groups":
        await EventStates.leave_group.set()
        groups_kb = generators.get_groups_kb(user.groups)
        answer_message = "Select a group to leave it"

    await message.answer(answer_message, reply_markup=groups_kb)


async def show_group_settings(
    call: types.CallbackQuery, session: AsyncSession, repo: Repos,
    state: FSMContext
):
    selected_group = await repo.get_repo(GroupRepo).get(int(call.data))

    await state.update_data({
        "selected_group_id": int(call.data),
        "selected_group_name": selected_group.name
    })

    await call.answer("You have selected the group")
    await call.message.edit_text(
        f"Options for the group {selected_group.name}",
        reply_markup=manage_own_group_kb
    )


async def leave_group(
    call: types.CallbackQuery, session: AsyncSession, repo: Repos,
    state: FSMContext
):
    await EventStates.normal.set()

    await repo.get_repo(GroupRepo).delete(call.from_user.id, int(call.data))
    await session.commit()

    await call.message.edit_text("You have left the group")


def register_handlers(dp: Dispatcher):
    dp.register_my_chat_member_handler(
        create_group, ChatTypeFilter(["group", "supergroup"]),
        state='*'
    )

    dp.register_message_handler(
        select_group, ChatTypeFilter("private"),
        Text(endswith=("My groups", "Configure groups")),
        state='*'
    )

    dp.register_callback_query_handler(
        show_group_settings,
        state=EventStates.manage_own_group
    )

    dp.register_callback_query_handler(
        leave_group,
        state=EventStates.leave_group
    )
