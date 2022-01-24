from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from inline_keyboards.edit_lectures_keyboard import edit_menu_inline_keyboard
from inline_keyboards.tools import *

import inline_keyboards
from inline_keyboards.days_keyboard import inverted_days_buttons
from inline_keyboards.edit_lectures_keyboard import edit_menu_inline_keyboard
from inline_keyboards.tools import *

from loader import scheduler

from peewee import IntegrityError
from db_models import *
from cron.cron_functions import *

from states import LectureStates


async def create_lecture_handler(message: types.Message, state: FSMContext):
    await state.update_data(for_user=message.from_user.id)

    await LectureStates.waiting_for_title.set()
    await message.reply(text="Отправьте название лекции в ответ на это сообщение.")

async def set_lecture_title_handler(message: types.Message, state: FSMContext):
    await state.update_data(tmp_messages=[message.message_id])
    from_user_state_data = await state.get_data('for_user')

    if from_user_state_data['for_user'] == message.from_user.id:
        try:
            Lecture.create(lecture_name=message.text,
                           course=Course.select().where(Course.course_id == message.chat.id).get())
        except IntegrityError:
            await message.reply(text="Лекция с таким названием уже существует\n"
                                     "Выберите другое название и попробуйте ещё раз.")
            raise IntegrityError

        print('Title: ', message.text)

        await LectureStates.waiting_for_description.set()
        await message.reply(text="Отправьте описание лекции в ответ на это сообщение.\n"
                                 "Может содержать ссылки и доп. информацию.")

async def set_lecture_description_handler(message: types.Message, state: FSMContext):
    from_user_state_data = await state.get_data('for_user')

    if from_user_state_data['for_user'] == message.from_user.id:
        course = Course.select().where(Course.course_id == message.chat.id).get()
        add_description_query = Lecture.update({Lecture.description: message.text}).where(Lecture.course == course)
        add_description_query.execute()

        print("Description: ", message.text)

        await LectureStates.waiting_for_day.set()
        await message.reply(reply_markup=inline_keyboards.days_keyboard.choose_days_inline_keyboard,
                            text="Выберите день/дни проведения лекции.\n\n")

async def set_lecture_day_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    from_user_state_data = await state.get_data('for_user')

    if from_user_state_data['for_user'] == callback_query.from_user.id:
        print("Pressed btn: ", callback_query.message)
        message_text = callback_query.message.text
        callback_data = callback_query.data
        inline_keyboard = callback_query.message.reply_markup['inline_keyboard']
        pressed_inline_button = get_pressed_inline_button(inline_keyboard, callback_data)

        if callback_data == 'done':
            selected_days = get_selected_inline_days(inline_keyboard)
            print("Done! Selected days: ", selected_days)
            course = Course.select().where(Course.course_id == callback_query.message.chat.id).get()
            lecture = Lecture.select().where(Lecture.course == course).order_by(Lecture.id.desc()).get()

            if all(day in days_buttons.values() for day in selected_days):
                for day in selected_days:
                    lecture.days.add(Day.select().where(Day.weekday == day).get())

            await callback_query.answer("Готово")
            await callback_query.message.edit_text(parse_mode='html',
                                                   text=f"Выбранные дни: {', '.join(selected_days)}\n\n"
                                                        "Отправьте время для каждого дня в таком порядке, как "
                                                        "перечислено выше, через запятую.\n\n"
                                                        "Например вы можете указать <b>8:30, 13:00, 7:05</b>"
                                                        " для понедельника, четверга и воскресенья соответственно.\n\n")
            await LectureStates.waiting_for_time.set()

        elif callback_data in days_buttons.keys():

            if pressed_inline_button['text'].endswith('✅'):
                pressed_inline_button['text'] = pressed_inline_button['text'][:-1]
                await callback_query.answer("День убран из расписания лекции")
            else:
                pressed_inline_button['text'] += " ✅"
                await callback_query.answer("День добавлен в расписание лекции")

            await callback_query.message.edit_text(reply_markup=callback_query.message.reply_markup,
                                                   text=message_text)

async def set_lecture_time_handler(message: types.Message, state: FSMContext):
    from_user_state_data = await state.get_data('for_user')

    if from_user_state_data['for_user'] == message.from_user.id:
        course = Course.select().where(Course.course_id == message.chat.id).get()
        lecture = Lecture.select().where(Lecture.course == course).order_by(Lecture.id.desc()).get()

        lecture_day_values = []
        for day in lecture.days:
            lecture_day_values.append(day.weekday)

        lecture_time_values = message.text.replace(' ', '').split(',')

        lecture_day_time_values = dict(zip(lecture_day_values, lecture_time_values))

        cron_jobs = []
        for day, time in lecture_day_time_values.items():
            hour = time.split(':')[0]
            minute = time.split(':')[1]
            job = scheduler.add_job(lecture_notify, 'cron',
                                    day_of_week=inverted_days_buttons[day],
                                    hour=hour, minute=minute,
                                    args=[lecture.lecture_name, lecture.description, message.chat.id])

            cron_jobs.append({'job_id': job.id})
        CronJob.insert_many(cron_jobs).execute()

        for job in cron_jobs:
            print('Adding job ' + str(job) + ' to cron_jobs')
            lecture.cron_jobs.add(CronJob.select().where(CronJob.job_id == job['job_id']).get())

        print("Cron jobs started")
        await message.reply(text="Готово")
        await LectureStates.normal.set()

