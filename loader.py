from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from middlewares.db import DbSessionMiddleware

import os
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler


logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("API_TOKEN")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# Load some additional env variables
SOURCE_CODE_LINK = os.getenv("SOURCE_CODE_LINK")
TIMEZONE = os.getenv("TIMEZONE")  # Example: Europe/Kiev

engine = create_async_engine(
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}",
    future=True
)
db_pool = sessionmaker(engine, class_=AsyncSession)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# TODO: move it to setup_middlewares function
dp.middleware.setup(DbSessionMiddleware(db_pool))

scheduler = AsyncIOScheduler(timezone=TIMEZONE)
scheduler.add_jobstore(
    'sqlalchemy',
    url=f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
)
scheduler.start()
