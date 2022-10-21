from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import generators
from keyboards.switchable import get_selected_buttons, update_switchable_kb

from states.event import EventStates
from services.repositories import Repos, WeekdayRepo, EventRepo


async def get_event_name(call: types.CallbackQuery):
    await EventStates.waiting_for_name.set()
    await call.message.edit_text(
        text="Отправьте название события в ответ на это сообщение"
    )


async def set_event_name(message: types.Message, state: FSMContext):
    await EventStates.waiting_for_description.set()
    await state.update_data({"event_name": message.text})
    await message.reply(
        text="Отправьте описание события в ответ на это сообщение.\n"
        "Может содержать ссылки и доп. информацию."
    )


async def set_event_description(
    message: types.Message, repo: Repos, state: FSMContext
):
    await EventStates.waiting_for_day.set()
    await state.update_data({"event_description": message.text})

    weekdays = await repo.get_repo(WeekdayRepo).get_all()
    weekdays_kb = generators.get_switchable_kb(weekdays)

    await message.reply(
        reply_markup=weekdays_kb,
        text="Выберите день/дни проведения события.\n\n"
    )


async def select_event_weekdays(
    call: types.CallbackQuery, state: FSMContext
):
    if call.data == "done":
        await EventStates.waiting_for_time.set()

        selected_weekdays = get_selected_buttons(
            call.message.reply_markup
        )

        await state.update_data({"event_weekdays": selected_weekdays})

        await call.message.edit_text(
            parse_mode='html',
            text=f"Выбранные дни: {', '.join(selected_weekdays.values())}\n\n"
            "Отправьте время для каждого дня в таком порядке, как "
            "перечислено выше, через запятую.\n\n"
            "Например вы можете указать <b>8:30, 13:00, 7:05</b> "
            "для понедельника, четверга и воскресенья соответственно.\n\n"
        )
        return

    switchable_weekdays_kb = update_switchable_kb(
        call.message.reply_markup, call.data
    )
    await call.message.edit_reply_markup(reply_markup=switchable_weekdays_kb)


async def set_event_start_time(
    message: types.Message, session: AsyncSession, repo: Repos,
    state: FSMContext
):
    await EventStates.normal.set()
    state_data = await state.get_data()

    group_id = state_data["selected_group_id"]
    event_name = state_data["event_name"]
    event_description = state_data["event_description"]
    event_weekdays = state_data["event_weekdays"]
    event_start_time = message.text.replace(' ', '').split(',')

    await repo.get_repo(EventRepo).add(
        event_name, event_description,
        group_id, event_weekdays.keys(), event_start_time
    )
    await session.commit()

    await message.reply(text="Готово")


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        get_event_name, Text("add_event"),
        state=EventStates.manage_own_group
    )

    dp.register_message_handler(
        set_event_name,
        state=EventStates.waiting_for_name
    )

    dp.register_message_handler(
        set_event_description,
        state=EventStates.waiting_for_description
    )

    dp.register_callback_query_handler(
        select_event_weekdays,
        state=EventStates.waiting_for_day
    )

    dp.register_message_handler(
        set_event_start_time,
        state=EventStates.waiting_for_time
    )
