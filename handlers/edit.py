from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from inline_keyboards.edit_lectures_keyboard import edit_menu_inline_keyboard
from inline_keyboards.tools import *

from loader import scheduler

from peewee import IntegrityError
from db_models import *

from states import LectureStates


async def edit_lecture_choose_handler(message: types.Message, state: FSMContext):
    await state.update_data(for_user=message.from_user.id)
    await LectureStates.lecture_edit_choose.set()

    course = Course.select().where(Course.course_id == message.chat.id).get()

    lectures = Lecture.select().where(Lecture.course == course)
    if not lectures:
        await message.reply(text="Вы ещё не создали ни одной лекции или удалили их.")
    else:
        lecture_names = []
        for lecture in lectures:
            lecture_names.append(lecture.lecture_name)

        await message.reply(text="Выберите лекцию, которую вы хотите удалить.",
                            reply_markup=get_lecture_inline_names(lecture_names))

async def edit_lecture_choose_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    from_user_state_data = await state.get_data('for_user')
    if from_user_state_data['for_user'] == callback_query.from_user.id:
        await state.update_data(edit_lecture=callback_query.data)
        await LectureStates.lecture_edit.set()
        await callback_query.message.edit_text(text=f"Выберите нужное действие для лекции {callback_query.data}",
                                               reply_markup=edit_menu_inline_keyboard)

async def edit_lecture_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    from_user_state_data = await state.get_data('for_user')
    if from_user_state_data['for_user'] == callback_query.from_user.id:
        edit_lecture = await state.get_data()
        edit_lecture = edit_lecture['edit_lecture']

        if callback_query.data == 'delete':
            course = Course.select().where(Course.course_id == callback_query.message.chat.id).get()
            lecture = Lecture.select().where(Lecture.course == course, Lecture.lecture_name == edit_lecture).get()
            for cron_job in lecture.cron_jobs.dicts():
                if scheduler.get_job(cron_job['job_id']):
                    scheduler.remove_job(job_id=cron_job['job_id'])
                CronJob.delete().where(CronJob.job_id == cron_job['job_id']).execute()

            lecture.delete_instance()
            LectureDay.delete().where(LectureDay.lecture == lecture).execute()
            LectureCronJob.delete().where(LectureCronJob.lecture == lecture).execute()
            await callback_query.answer(text="Лекция удалена")
            await callback_query.message.edit_text(text=f"Лекция {edit_lecture} удалена.")

        await LectureStates.normal.set()
