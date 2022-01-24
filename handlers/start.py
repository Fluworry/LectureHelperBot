from aiogram import types
from aiogram.utils import markdown

from peewee import IntegrityError
from db_models import *
from loader import bot


async def private_message_start_handler(message: types.Message):
    await message.answer(parse_mode='markdown',
                         text="Данный бот рассылает уведомления о начале лекции.\n"
                              "Добавьте бота в группу.\n\n"
                              f"{markdown.link('Исходный код', 'https://gitlab.com/Luent/LectureHelperBot')}")


async def create_course_handler(message: types.ChatMemberUpdated):
    try:
        Course.create(course_name=message.chat.title, course_id=message.chat.id)
    except IntegrityError:
        print("Данный курс уже был создан")
    await bot.send_message(chat_id=message.chat.id, parse_mode='markdown',
                           text="Lecture Helper Бот успешно добавлен в группу.\n"
                                "Данный бот рассылает уведомления о начале лекции.\n\n"
                                "Добавить новые лекции можно командой /addlect\n"
                                "Удалить лекции можно командой /rmlect\n"
                                'Напишите "/", чтобы увидеть список доступных команд.\n\n'
                                f"{markdown.link('Исходный код', 'https://gitlab.com/Luent/LectureHelperBot')}")