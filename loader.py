from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from cron import cron_config

from dotenv import load_dotenv
import os
import logging

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
scheduler = AsyncIOScheduler(cron_config.config)

