from aiogram import types
from aiogram.dispatcher import FSMContext

# from keyboards.inline import edit_menu_inline_keyboard
from keyboards import generators
from keyboards.handle_switchable import get_selected_buttons
from keyboards.inline.manage import manage_own_group_kb

from loader import scheduler

from db.models import Lecture, User, Group
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError, NoResultFound

from states import LectureStates


async def show_groups_reply(message: types.Message):
    db_session = message.bot.get("db")

    async with db_session() as session:
        user = await session.get(User, message.from_user.id)

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


async def manage_own_group(callback_query: types.CallbackQuery, state: FSMContext):
    db_session = callback_query.bot.get("db")

    async with db_session() as session:
        selected_group = await session.get(Group, int(callback_query.data))

    await state.update_data({
        "selected_group_id": int(callback_query.data), 
        "selected_group_name": selected_group.name
    })

    await callback_query.answer("Вы выбрали группу")
    await callback_query.message.edit_text(
        f"Опции для группы {selected_group.name}", 
        reply_markup=manage_own_group_kb
    )


async def leave_group(callback_query: types.CallbackQuery, state: FSMContext):
    ...


async def show_lectures(callback_query: types.CallbackQuery, state: FSMContext):
    await LectureStates.lecture_edit.set()

    state_data = await state.get_data()
    group_id = state_data["selected_group_id"]

    db_session = callback_query.bot.get("db")

    async with db_session() as session:
        stmt = select(Lecture).where(Lecture.group_id == group_id)
        result = await session.execute(stmt)
        lectures = result.scalars().all()

    if not lectures:
        await callback_query.message.answer(
            text="Вы ещё не создали ни одной лекции или удалили их."
        )
        return

    switchable_lectures_kb = generators.get_switchable_kb(
        lectures, row_width=3, done_button_text="Удалить"
    )

    await callback_query.message.answer(
        text="Выберите лекции, которые нужно удалить",
        reply_markup=switchable_lectures_kb
    )


async def delete_lecture(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "done":
        await LectureStates.normal.set()

        selected_lectures = get_selected_buttons(
            callback_query.message.reply_markup
        )
        # TODO: check if user is group owner

        db_session = callback_query.bot.get("db")

        async with db_session() as session:
            for lecture_id in selected_lectures.keys():
                lecture = await session.get(Lecture, lecture_id)

                # TODO: CASCADE CronJob instead of manual deleting
                for cronjob in lecture.cronjob:
                    if scheduler.get_job(cronjob.job_id):
                        scheduler.remove_job(cronjob.job_id)
                    await session.delete(cronjob)
                await session.delete(lecture)
            
            await session.commit()

        await callback_query.answer(text="Лекции удалены")
        await callback_query.message.edit_text(text=f"Лекции {', '.join(selected_lectures.values())} удалены.")
        
        return
    
    switchable_lectures_kb = generators.update_switchable_kb(
        callback_query.message.reply_markup,
        callback_query.data
    )
    await callback_query.message.edit_reply_markup(reply_markup=switchable_lectures_kb)
