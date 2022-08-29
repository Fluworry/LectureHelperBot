from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards import generators
from keyboards.switchable import get_selected_buttons, update_switchable_kb

from states import LectureStates

from sqlalchemy.ext.asyncio import AsyncSession
from db.requests import get_weekdays, add_lecture


async def get_lecture_name(call: types.CallbackQuery):
    await LectureStates.waiting_for_name.set()
    await call.message.edit_text(
        text="Отправьте название лекции в ответ на это сообщение"
    )


async def set_lecture_name(message: types.Message, state: FSMContext):
    await LectureStates.waiting_for_description.set()
    await state.update_data({"lecture_name": message.text})
    await message.reply(
        text="Отправьте описание лекции в ответ на это сообщение.\n"
        "Может содержать ссылки и доп. информацию."
    )


async def set_lecture_description(
    message: types.Message, session: AsyncSession,
    state: FSMContext
):
    await LectureStates.waiting_for_day.set()
    await state.update_data({"lecture_description": message.text})

    weekdays = await get_weekdays(session)
    weekdays_kb = generators.get_switchable_kb(weekdays)

    await message.reply(
        reply_markup=weekdays_kb,
        text="Выберите день/дни проведения лекции.\n\n"
    )


async def select_lecture_weekdays(
    call: types.CallbackQuery, state: FSMContext
):
    if call.data == "done":
        await LectureStates.waiting_for_time.set()

        selected_weekdays = get_selected_buttons(
            call.message.reply_markup
        )

        await state.update_data({"lecture_weekdays": selected_weekdays})

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


async def set_lecture_start_time(
    message: types.Message, session: AsyncSession,
    state: FSMContext
):
    await LectureStates.normal.set()
    state_data = await state.get_data()

    group_id = state_data["selected_group_id"]
    lecture_name = state_data["lecture_name"]
    lecture_description = state_data["lecture_description"]
    lecture_weekdays = state_data["lecture_weekdays"]
    lecture_start_time = message.text.replace(' ', '').split(',')

    await add_lecture(
        session, lecture_name, lecture_description,
        group_id, lecture_weekdays.keys(), lecture_start_time
    )
    await session.commit()

    await message.reply(text="Готово")
