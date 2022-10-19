import os

from aiogram.dispatcher import Dispatcher
from aiogram.bot import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage


API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
