from aiogram import Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter, Text

from .commands import start_command
from . import manage_group
from . import add_lecture
from . import delete_lecture

from states import LectureStates


def register_handlers(dp: Dispatcher):
    # Reply and member updated handlers
    dp.register_message_handler(
        start_command, ChatTypeFilter("private"),
        state='*', commands=['start']
    )

    dp.register_my_chat_member_handler(
        manage_group.create_group, ChatTypeFilter(["group", "supergroup"]),
        state='*'
    )

    dp.register_message_handler(
        manage_group.select_group, ChatTypeFilter("private"),
        Text(endswith=("Мои группы", "Управление группами")),
        state='*'
    )

    # Callback handlers
    dp.register_callback_query_handler(
        delete_lecture.select_lecture, Text("delete_lecture"),
        state=LectureStates.manage_own_group
    )

    dp.register_callback_query_handler(
        delete_lecture.delete_selected_lectures,
        state=LectureStates.lecture_edit
    )

    dp.register_callback_query_handler(
        add_lecture.get_lecture_name, Text("add_lecture"),
        state=LectureStates.manage_own_group
    )

    dp.register_callback_query_handler(
        manage_group.show_group_settings,
        state=LectureStates.manage_own_group
    )

    dp.register_callback_query_handler(
        manage_group.leave_group,
        state=LectureStates.leave_group
    )

    dp.register_message_handler(
        add_lecture.set_lecture_name,
        state=LectureStates.waiting_for_name
    )

    dp.register_message_handler(
        add_lecture.set_lecture_description,
        state=LectureStates.waiting_for_description
    )

    dp.register_callback_query_handler(
        add_lecture.select_lecture_weekdays,
        state=LectureStates.waiting_for_day
    )

    dp.register_message_handler(
        add_lecture.set_lecture_start_time,
        state=LectureStates.waiting_for_time
    )
