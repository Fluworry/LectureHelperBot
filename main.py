import logging
import os

from aiogram import Bot, Dispatcher, executor, types, filters
import aiogram.utils.exceptions
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

import inline_keyboards
from inline_keyboards.days_keyboard import days_buttons, inverted_days_buttons
from inline_keyboards.edit_lectures_keyboard import edit_menu_inline_keyboard
from inline_keyboards.tools import *

from db_models import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cron.cron_config import *
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
scheduler = AsyncIOScheduler(config)


async def lecture_notify(title, description, chat_id):
    await bot.send_message(chat_id=chat_id, parse_mode='html',
                           text=f"Уведомление о начале лекции:\n\n\n"
                                f"<b>{title}</b>\n\n"
                                f"{description}")


class LectureStates(StatesGroup):
    normal = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_day = State()
    waiting_for_time = State()

    lecture_edit_choose = State()
    lecture_edit = State()


@dp.my_chat_member_handler()
async def create_course_handler(message: types.ChatMemberUpdated):
    Course.create(course_name=message.chat.title, course_id=message.chat.id)
    await bot.send_message(chat_id=message.chat.id, text="Lecture Helper Бот успешно добавлен в группу.\n"
                                                         "Данный бот рассылает уведомления о начале лекции.\n\n"
                                                         "Добавить новые лекции в расписание можно командой /addlect")


@dp.message_handler(lambda msg: msg.chat.type == 'private', state='*', commands=['start'])
async def private_message_start_handler(message: types.Message):
    await message.answer(text="Данный бот рассылает уведомления о начале лекции.\n"
                              "Добавьте бота в группу.")


@dp.message_handler(lambda msg: msg.chat.type == 'group', state='*', commands=['rmlect'])
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


@dp.callback_query_handler(state=LectureStates.lecture_edit_choose)
async def edit_lecture_choose_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    from_user_state_data = await state.get_data('for_user')
    if from_user_state_data['for_user'] == callback_query.from_user.id:
        await state.update_data(edit_lecture=callback_query.data)
        await LectureStates.lecture_edit.set()
        await callback_query.message.edit_text(text=f"Выберите нужное действие для лекции {callback_query.data}",
                                               reply_markup=edit_menu_inline_keyboard)


@dp.callback_query_handler(state=LectureStates.lecture_edit)
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


@dp.message_handler(lambda msg: msg.chat.type == 'group', state='*', commands=['addlect'])
async def create_lecture_handler(message: types.Message, state: FSMContext):
    await state.update_data(for_user=message.from_user.id)

    await LectureStates.waiting_for_title.set()
    await message.reply(text="Отправьте название лекции в ответ на это сообщение.")


@dp.message_handler(state=LectureStates.waiting_for_title)
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


@dp.message_handler(state=LectureStates.waiting_for_description)
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


@dp.callback_query_handler(state=LectureStates.waiting_for_day)
async def set_lecture_day_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    from_user_state_data = await state.get_data('for_user')

    if from_user_state_data['for_user'] == callback_query.from_user.id:
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
                                                   text=f"Выбранные дни: {', '.join(selected_days)}\n"
                                                        "Отправьте время для каждого дня в ответ на это сообщение, "
                                                        "через запятую.\n\n"
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


@dp.message_handler(state=LectureStates.waiting_for_time)
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


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
