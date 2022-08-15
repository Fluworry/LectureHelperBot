from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards import generators
from keyboards.handle_switchable import get_selected_buttons
from keyboards.inline.manage import manage_own_group_kb

from states import LectureStates

from sqlalchemy.ext.asyncio import AsyncSession
from db.requests import get_user, get_group, get_lectures_by_group_id
from db.requests import delete_lectures


async def show_groups_reply(message: types.Message, session: AsyncSession):
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


async def manage_own_group(
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


async def show_lectures(
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


async def get_lectures_to_delete(
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
        await call.message.edit_text(text=f"Лекции {', '.join(selected_lectures.values())} удалены.")
        
        return
    
    switchable_lectures_kb = generators.update_switchable_kb(
        call.message.reply_markup,
        call.data
    )
    await call.message.edit_reply_markup(reply_markup=switchable_lectures_kb)
