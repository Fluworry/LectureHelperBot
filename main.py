import os
import logging

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middlewares.db import DbSessionMiddleware
from middlewares.scheduler import SchedulerMiddleware

from loader import bot, dp

from handlers import add_lecture, delete_lecture, manage_group, commands


async def main():
    logging.basicConfig(level=logging.INFO)

    # Load env variables
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")

    # SOURCE_CODE_LINK = os.getenv("SOURCE_CODE_LINK")
    TIMEZONE = os.getenv("TIMEZONE")  # Example: Europe/Kiev

    engine = create_async_engine(
        f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}",
        future=True
    )
    db_pool = sessionmaker(engine, class_=AsyncSession)

    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    scheduler.add_jobstore(
        'sqlalchemy',
        url=f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
    )

    # Register handlers
    add_lecture.register_handlers(dp)
    delete_lecture.register_handlers(dp)
    manage_group.register_handlers(dp)
    commands.register_handlers(dp)

    # Register middlewares
    dp.middleware.setup(DbSessionMiddleware(db_pool))
    dp.middleware.setup(SchedulerMiddleware(scheduler))

    try:
        scheduler.start()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        bot_session = await bot.get_session()
        await bot_session.close()


if __name__ == '__main__':
    asyncio.run(main())
    # handlers.register_handlers(dp)
    # executor.start_polling(dp, skip_updates=True)
