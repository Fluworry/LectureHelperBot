from aiogram.dispatcher.filters.state import State, StatesGroup


class LectureStates(StatesGroup):
    normal = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_day = State()
    waiting_for_time = State()

    lecture_edit_choose = State()
    lecture_edit = State()