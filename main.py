from aiogram import executor

from loader import dp
import handlers


if __name__ == '__main__':
    handlers.register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
