from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from sqlalchemy.orm import sessionmaker
from services.repositories import Repos


class DbSessionMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, session_pool: sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def pre_process(self, obj, data, *args):
        session = self.session_pool()
        data["session"] = session
        data["repo"] = Repos(session)

    async def post_process(self, obj, data, *args):
        session = data.get("session")
        if session:
            await session.close()
