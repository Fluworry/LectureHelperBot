from aiogram import executor

from cron.cron_functions import *
from loader import *
import handlers


handlers.setup(dp)

if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
