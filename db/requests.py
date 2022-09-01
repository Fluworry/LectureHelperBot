from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Group, WeekDay, CronJob, Lecture
from services.scheduler import notify_users

from loader import scheduler
from uuid import uuid4


async def add_user(session: AsyncSession, user_id: int) -> User:
    user = await session.merge(User(user_id=user_id))
    return user


async def get_user(session: AsyncSession, user_id: int) -> User:
    return await session.get(User, user_id)


async def add_user_to_group(
    session: AsyncSession, user: User, invite_token: str
):
    stmt = select(Group).where(
        Group.invite_token == invite_token
    ).options(selectinload(Group.users))

    result = await session.execute(stmt)
    group = result.scalar()

    if group is not None:
        group.users.append(user)


async def add_group(
    session: AsyncSession, name: str,
    user_id: int, chat_id: int
) -> Group:

    stmt = select(Group).where(Group.chat_id == chat_id)
    result = await session.execute(stmt)
    group = result.scalar()

    if group is None:
        invite_token = uuid4().hex[:15]
        owner = await add_user(session, user_id)

        group = Group(
            name=name, invite_token=invite_token,
            chat_id=chat_id, owner_id=owner.user_id
        )
        session.add(group)
        owner.groups.append(group)

    return group


async def get_group(session: AsyncSession, group_id: int) -> Group:
    return await session.get(Group, group_id)


async def get_weekdays(session: AsyncSession) -> list[WeekDay]:
    stmt = select(WeekDay)
    result = await session.execute(stmt)
    weekdays = result.scalars().all()
    return weekdays


async def add_lecture(
    session: AsyncSession, name: str, description: str,
    group_id: int, weekdays: list[int], start_time: list[str]
):
    lecture = Lecture(
        name=name,
        description=description,
        group_id=group_id
    )
    group = await get_group(session, group_id)

    for i, weekday_id in enumerate(weekdays):
        weekday = await session.get(WeekDay, weekday_id)
        lecture.weekdays.append(weekday)

        hour, minute = start_time[i].split(':')
        scheduler_job = scheduler.add_job(
            notify_users, "cron",
            day_of_week=weekday.cron_name, hour=hour, minute=minute,
            args=[name, description, group.user_ids]
        )
        cronjob = CronJob(job_id=scheduler_job.id)
        lecture.cronjobs.append(cronjob)

    session.add(lecture)


async def delete_lectures(session: AsyncSession, lectures: list[int]):
    for lecture_id in lectures:
        lecture = await session.get(Lecture, lecture_id)

        for cronjob in lecture.cronjobs:
            if scheduler.get_job(cronjob.job_id):
                scheduler.remove_job(cronjob.job_id)

        await session.delete(lecture)


async def get_lectures_by_group_id(
    session: AsyncSession,
    group_id: int
) -> list[Lecture]:

    stmt = select(Lecture).where(Lecture.group_id == group_id)
    result = await session.execute(stmt)
    return result.scalars().all()
