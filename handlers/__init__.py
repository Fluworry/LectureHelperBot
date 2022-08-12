from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter, Text

from .start import start_command, create_group
from .edit import *
from .create import *

from states import LectureStates


def setup(dp: Dispatcher):
    # Reply and member updated handlers
    dp.register_message_handler(
        start_command, ChatTypeFilter("private"), 
        state='*', commands=['start']
    )

    dp.register_my_chat_member_handler(
        create_group, ChatTypeFilter("group"), state='*'
    )
    
    dp.register_message_handler(
        show_groups_reply, ChatTypeFilter("private"), 
        Text(endswith=("Мои группы", "Управление группами")), state='*'
    )

    # Callback handlers
    dp.register_callback_query_handler(
        show_lectures, Text("delete_lecture"), state=LectureStates.manage_own_group
    )

    dp.register_callback_query_handler(
        add_lecture, Text("add_lecture"), state=LectureStates.manage_own_group
    )

    dp.register_callback_query_handler(
        manage_own_group, state=LectureStates.manage_own_group
    )

    dp.register_callback_query_handler(
        delete_lecture, state=LectureStates.lecture_edit
    )

    dp.register_message_handler(set_lecture_name, state=LectureStates.waiting_for_name)
    dp.register_message_handler(set_lecture_description, state=LectureStates.waiting_for_description)
    dp.register_callback_query_handler(set_lecture_day, state=LectureStates.waiting_for_day)
    dp.register_message_handler(set_lecture_start_time, state=LectureStates.waiting_for_time)
