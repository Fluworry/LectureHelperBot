from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class SchedulerMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, scheduler: AsyncIOScheduler):
        super().__init__()
        self.scheduler = scheduler

    async def pre_process(self, obj, data, *args):
        data["scheduler"] = self.scheduler
