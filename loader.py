import os

from aiogram.dispatcher import Dispatcher
from aiogram.bot import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler


SOURCE_CODE_LINK = os.getenv("SOURCE_CODE_LINK")
TIMEZONE = os.getenv("TIMEZONE")  # Example: Europe/Kiev

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

scheduler = AsyncIOScheduler(timezone=TIMEZONE)
