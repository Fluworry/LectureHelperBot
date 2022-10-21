from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import generators
from keyboards.switchable import get_selected_buttons, update_switchable_kb

from states.event import EventStates
from services.repositories import Repos, EventRepo


async def select_event(
    call: types.CallbackQuery, session: AsyncSession, repo: Repos,
    state: FSMContext
):
    await EventStates.event_edit.set()

    state_data = await state.get_data()
    group_id = state_data["selected_group_id"]
    events = await repo.get_repo(EventRepo).get_by_group_id(group_id)

    if not events:
        await call.message.answer(
            text="Вы ещё не создали ни одного события."
        )
        return

    switchable_events_kb = generators.get_switchable_kb(
        events, row_width=3, done_button_text="Удалить"
    )

    await call.message.answer(
        text="Выберите события, которые нужно удалить",
        reply_markup=switchable_events_kb
    )


async def delete_selected_events(
    call: types.CallbackQuery, session: AsyncSession, repo: Repos,
    state: FSMContext
):
    if call.data == "done":
        await EventStates.normal.set()

        selected_events = get_selected_buttons(
            call.message.reply_markup
        )

        for event_id in selected_events:
            await repo.get_repo(EventRepo).delete(event_id)
        # TODO: check if user is group owner

        await session.commit()

        await call.answer(text="События удалены")
        await call.message.edit_text(
            text=f"События {', '.join(selected_events.values())} удалены."
        )

        return

    switchable_events_kb = update_switchable_kb(
        call.message.reply_markup, call.data
    )
    await call.message.edit_reply_markup(reply_markup=switchable_events_kb)


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        select_event, Text("delete_event"),
        state=EventStates.manage_own_group
    )

    dp.register_callback_query_handler(
        delete_selected_events,
        state=EventStates.event_edit
    )
