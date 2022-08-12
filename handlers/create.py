from aiogram import executor, types
from aiogram.dispatcher import FSMContext

from keyboards import generators
from keyboards.handle_switchable import get_selected_buttons

from loader import scheduler

from db.models import CronJob, Lecture, User, Group, WeekDay
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError, NoResultFound

from cron.cron_functions import *

from states import LectureStates


async def add_lecture(callback_query: types.CallbackQuery, state: FSMContext):
    await LectureStates.waiting_for_name.set()
    await callback_query.message.edit_text(text="Отправьте название лекции в ответ на это сообщение")


async def set_lecture_name(message: types.Message, state: FSMContext):
    await LectureStates.waiting_for_description.set()
    await state.update_data({"lecture_name": message.text})
    await message.reply(
        text="Отправьте описание лекции в ответ на это сообщение.\n"
        "Может содержать ссылки и доп. информацию."
    )


async def set_lecture_description(message: types.Message, state: FSMContext):
    await LectureStates.waiting_for_day.set()
    await state.update_data({"lecture_description": message.text})

    db_session = message.bot.get("db")

    async with db_session() as session:
        stmt = select(WeekDay)
        result = await session.execute(stmt)
        weekdays = result.scalars().all()
        
    weekdays_kb = generators.get_switchable_kb(weekdays)
    
    await message.reply(reply_markup=weekdays_kb,
                        text="Выберите день/дни проведения лекции.\n\n")


async def set_lecture_day(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "done":
        await LectureStates.waiting_for_time.set()
        
        selected_weekdays = get_selected_buttons(
            callback_query.message.reply_markup
        )

        await state.update_data({"lecture_weekdays": selected_weekdays})

        await callback_query.message.edit_text(
            parse_mode='html',
            text=f"Выбранные дни: {', '.join(selected_weekdays.values())}\n\n"
                "Отправьте время для каждого дня в таком порядке, как "
                "перечислено выше, через запятую.\n\n"
                "Например вы можете указать <b>8:30, 13:00, 7:05</b> "
                "для понедельника, четверга и воскресенья соответственно.\n\n"
        )
        return

    switchable_weekdays_kb = generators.update_switchable_kb(
        callback_query.message.reply_markup,
        callback_query.data
    )
    await callback_query.message.edit_reply_markup(reply_markup=switchable_weekdays_kb)


async def set_lecture_start_time(message: types.Message, state: FSMContext):
    state_data = await state.get_data()

    group_id = state_data["selected_group_id"]
    lecture_name = state_data["lecture_name"]
    lecture_description = state_data["lecture_description"]
    lecture_weekdays = state_data["lecture_weekdays"]
    lecture_start_time = message.text.replace(' ', '').split(',')

    db_session = message.bot.get("db")
    
    async with db_session() as session:
        # TODO: check if user is a group owner
        lecture = Lecture(
            name=lecture_name, 
            description=lecture_description,
            group_id=group_id
        )

        for i, weekday_id in enumerate(lecture_weekdays.keys()):
            weekday = await session.get(WeekDay, weekday_id)
            lecture.weekday.append(weekday)

            hour, minute = lecture_start_time[i].split(':')

            scheduler_job = scheduler.add_job(
                lecture_notify, "cron",
                day_of_week=weekday.cron_name, hour=hour, minute=minute,
                args=[lecture_name, lecture_description, message.chat.id]
            )
            cronjob = CronJob(job_id=scheduler_job.id)
            lecture.cronjob.append(cronjob)

        session.add(lecture)
        await session.commit()

    await message.reply(text="Готово")
    await LectureStates.normal.set()
