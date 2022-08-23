from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards import generators
from keyboards.handle_switchable import get_selected_buttons

from states import LectureStates

from sqlalchemy.ext.asyncio import AsyncSession
from db.requests import delete_lectures, get_lectures_by_group_id


async def select_lecture(
    call: types.CallbackQuery, session: AsyncSession,
    state: FSMContext
):
    await LectureStates.lecture_edit.set()

    state_data = await state.get_data()
    group_id = state_data["selected_group_id"]
    lectures = await get_lectures_by_group_id(session, group_id)

    if not lectures:
        await call.message.answer(
            text="Вы ещё не создали ни одной лекции или удалили их."
        )
        return

    switchable_lectures_kb = generators.get_switchable_kb(
        lectures, row_width=3, done_button_text="Удалить"
    )

    await call.message.answer(
        text="Выберите лекции, которые нужно удалить",
        reply_markup=switchable_lectures_kb
    )


async def delete_selected_lectures(
    call: types.CallbackQuery, session: AsyncSession,
    state: FSMContext
):
    if call.data == "done":
        await LectureStates.normal.set()

        selected_lectures = get_selected_buttons(
            call.message.reply_markup
        )

        await delete_lectures(session, list(selected_lectures.keys()))
        # TODO: check if user is group owner

        await session.commit()

        await call.answer(text="Лекции удалены")
        await call.message.edit_text(
            text=f"Лекции {', '.join(selected_lectures.values())} удалены."
        )

        return

    switchable_lectures_kb = generators.update_switchable_kb(
        call.message.reply_markup, call.data
    )
    await call.message.edit_reply_markup(reply_markup=switchable_lectures_kb)
