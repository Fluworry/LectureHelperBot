import logging

from aiogram import Bot, Dispatcher, executor, types, filters
import aiogram.utils.exceptions
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

import inline_keyboards
from inline_keyboards.keyboards import days_buttons
from inline_keyboards.tools import get_pressed_inline_button

from db_models import *

from dotenv import load_dotenv


API_TOKEN = '2118355263:AAFW-Ntf0TKK1IaHdc3_nTOLRlK8XqX7vps'

logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class LectureStates(StatesGroup):
    normal = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_day = State()
    waiting_for_time = State()


@dp.my_chat_member_handler()
async def create_course_handler(message: types.ChatMemberUpdated):
    Course.create(course_name=message.chat.title, course_id=message.chat.id)
    await bot.send_message(chat_id=message.chat.id, text="Lecture Helper Бот успешно добавлен в группу.\n"
                                                         "Данный бот рассылает уведомления о начале лекции.\n\n"
                                                         "Администратор группы может добавить новые "
                                                         "лекции в расписание используя команду /newlect")


@dp.message_handler(lambda msg: msg.chat.type == 'group', commands=['newlect'])
async def create_lecture_handler(message: types.Message):
    await LectureStates.waiting_for_title.set()
    await message.reply(reply=False, text="Отправьте название лекции в ответ на это сообщение.\n\n")


@dp.message_handler(state=LectureStates.waiting_for_title)
async def set_lecture_title_handler(message: types.Message):
    Lecture.create(lecture_name=message.text, course=Course.get(Course.course_id == message.chat.id))

    print('Title: ', message.text)

    await LectureStates.waiting_for_description.set()
    await message.reply(reply=False, text="Отправьте описание лекции в ответ на это сообщение.\n"
                                          "Может содержать ссылки и доп. информацию.")


@dp.message_handler(state=LectureStates.waiting_for_description)
async def set_lecture_description_handler(message: types.Message):
    course = Course.get(Course.course_id == message.chat.id)
    add_description_query = Lecture.update({Lecture.description: message.text}).where(Lecture.course == course)
    add_description_query.execute()

    print("Description: ", message.text)

    await LectureStates.waiting_for_day.set()
    await message.reply(reply=False, reply_markup=inline_keyboards.keyboards.choose_days_inline_keyboard,
                        text="Выберите день/дни проведения лекции.\n Выбранные дни: ")


@dp.callback_query_handler(state=LectureStates.waiting_for_day)
async def set_lecture_day_callback_handler(callback_query: types.CallbackQuery):
    message_text = callback_query.message.text
    callback_data = callback_query.data
    inline_keyboard = callback_query.message.reply_markup['inline_keyboard']
    pressed_inline_button = get_pressed_inline_button(inline_keyboard, callback_data)

    if callback_data == 'done':
        print("Done! ")

        await LectureStates.normal.set()

    elif callback_data in days_buttons.keys():

        if pressed_inline_button['text'].endswith('✅'):
            pressed_inline_button['text'] = pressed_inline_button['text'][:-1]
            await callback_query.answer("День убран из расписания лекции")
        else:
            pressed_inline_button['text'] += " ✅"
            await callback_query.answer("День добавлен в расписание лекции")

        await callback_query.message.edit_text(reply_markup=callback_query.message.reply_markup,
                                               text=message_text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
