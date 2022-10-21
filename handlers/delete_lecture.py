from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import generators
from keyboards.switchable import get_selected_buttons, update_switchable_kb

from states import LectureStates
from services.repositories import Repos, LectureRepo


async def select_lecture(
    call: types.CallbackQuery, session: AsyncSession, repo: Repos,
    state: FSMContext
):
    await LectureStates.lecture_edit.set()

    state_data = await state.get_data()
    group_id = state_data["selected_group_id"]
    lectures = await repo.get_repo(LectureRepo).get_by_group_id(group_id)

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
    call: types.CallbackQuery, session: AsyncSession, repo: Repos,
    state: FSMContext
):
    if call.data == "done":
        await LectureStates.normal.set()

        selected_lectures = get_selected_buttons(
            call.message.reply_markup
        )

        for lecture_id in selected_lectures:
            await repo.get_repo(LectureRepo).delete(lecture_id)
        # TODO: check if user is group owner

        await session.commit()

        await call.answer(text="Лекции удалены")
        await call.message.edit_text(
            text=f"Лекции {', '.join(selected_lectures.values())} удалены."
        )

        return

    switchable_lectures_kb = update_switchable_kb(
        call.message.reply_markup, call.data
    )
    await call.message.edit_reply_markup(reply_markup=switchable_lectures_kb)


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        select_lecture, Text("delete_lecture"),
        state=LectureStates.manage_own_group
    )

    dp.register_callback_query_handler(
        delete_selected_lectures,
        state=LectureStates.lecture_edit
    )
