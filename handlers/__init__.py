from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext

from .start import create_course_handler, private_message_start_handler
from .edit import *
from .create import *

from states import LectureStates


def setup(dp: Dispatcher):
    dp.register_my_chat_member_handler(create_course_handler, lambda msg: msg.chat.type == 'group')
    dp.register_message_handler(private_message_start_handler, lambda msg: msg.chat.type == 'private', state='*', commands=['start'])

    dp.register_message_handler(edit_lecture_choose_handler, lambda msg: msg.chat.type == 'group', state='*', commands=['rmlect'])
    dp.register_callback_query_handler(edit_lecture_choose_callback_handler, state=LectureStates.lecture_edit_choose)
    dp.register_callback_query_handler(edit_lecture_callback_handler, state=LectureStates.lecture_edit)

    dp.register_message_handler(create_lecture_handler, lambda msg: msg.chat.type == 'group', state='*', commands=['addlect'])
    dp.register_message_handler(set_lecture_title_handler, state=LectureStates.waiting_for_title)
    dp.register_message_handler(set_lecture_description_handler, state=LectureStates.waiting_for_description)
    dp.register_callback_query_handler(set_lecture_day_callback_handler, state=LectureStates.waiting_for_day)
    dp.register_message_handler(set_lecture_time_handler, state=LectureStates.waiting_for_time)
