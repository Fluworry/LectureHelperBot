from uuid import uuid4
from typing import Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db.models import User, Group, WeekDay, CronJob, Lecture
from services.notification import send_notification


class BaseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session


T = TypeVar("T", bound=BaseRepo)


class Repos(BaseRepo):
    def get_repo(self, Repo: Type[T], *args) -> T:
        return Repo(self.session, *args)


class WeekdayRepo(BaseRepo):
    async def get_all(self) -> list[WeekDay]:
        stmt = select(WeekDay)
        result = await self.session.execute(stmt)
        weekdays = result.scalars().all()
        return weekdays


class UserRepo(BaseRepo):
    async def add(self, user_id: int) -> User:
        user = await self.session.merge(User(user_id=user_id))
        return user

    async def get(self, user_id: int) -> User:
        return await self.session.get(User, user_id)


class LectureRepo(BaseRepo):
    def __init__(
        self, session: AsyncSession, scheduler: AsyncIOScheduler,
    ):
        super().__init__(session)
        self.scheduler = scheduler

    async def add(
        self, name: str, description: str,
        group_id: int, weekdays: list[int], start_time: list[str]
    ):
        lecture = Lecture(
            name=name,
            description=description,
            group_id=group_id
        )
        group_repo = GroupRepo(self.session)
        group = await group_repo.get(group_id)

        for i, weekday_id in enumerate(weekdays):
            weekday = await self.session.get(WeekDay, weekday_id)
            lecture.weekdays.append(weekday)

            hour, minute = start_time[i].split(':')
            scheduler_job = self.scheduler.add_job(
                send_notification, "cron",
                day_of_week=weekday.cron_name, hour=hour, minute=minute,
                args=[name, description, group.user_ids]
            )
            cronjob = CronJob(job_id=scheduler_job.id)
            lecture.cronjobs.append(cronjob)

        self.session.add(lecture)

    async def delete(self, lecture_id: int):
        lecture = await self.get(lecture_id)

        for cronjob in lecture.cronjobs:
            if self.scheduler.get_job(cronjob.job_id):
                self.scheduler.remove_job(cronjob.job_id)

        await self.session.delete(lecture)

    async def get_by_group_id(self, group_id: int) -> list[Lecture]:
        stmt = select(Lecture).where(Lecture.group_id == group_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get(self, lecture_id: int) -> Lecture:
        return await self.session.get(Lecture, lecture_id)


class GroupRepo(BaseRepo):
    async def add(self, name: str, user_id: int, chat_id: int) -> Group:
        stmt = select(Group).where(Group.chat_id == chat_id)
        result = await self.session.execute(stmt)
        group = result.scalar()

        if group is None:
            invite_token = uuid4().hex[:15]
            user_repo = UserRepo(self.session)
            owner = await user_repo.add(user_id)

            group = Group(
                name=name, invite_token=invite_token,
                chat_id=chat_id, owner_id=owner.user_id
            )
            self.session.add(group)
            owner.groups.append(group)

        return group

    async def add_user(self, user: User, invite_token: str):
        stmt = select(Group).where(
            Group.invite_token == invite_token
        ).options(selectinload(Group.users))

        result = await self.session.execute(stmt)
        group = result.scalar()

        if group is not None:
            group.users.append(user)

    async def delete(self, user_id: int, group_id: int):
        user_repo = UserRepo(self.session)
        group_repo = GroupRepo(self.session)

        user = await user_repo.get(user_id)
        group = await group_repo.get(group_id)

        user.groups.remove(group)

    async def get(self, group_id: int) -> Group:
        return await self.session.get(Group, group_id)
