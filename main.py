from aiogram import executor

from cron.cron_functions import *
from loader import *
import handlers


if __name__ == '__main__':
    handlers.register_handlers(dp)

    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
