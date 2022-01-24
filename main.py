from aiogram import executor, types
from aiogram.utils import markdown
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

import inline_keyboards
from inline_keyboards.days_keyboard import inverted_days_buttons
from inline_keyboards.edit_lectures_keyboard import edit_menu_inline_keyboard
from inline_keyboards.tools import *

from db_models import *
from cron.cron_functions import *
from loader import *
import handlers

from states import LectureStates

handlers.setup(dp)



if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
