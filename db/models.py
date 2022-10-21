from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.associationproxy import association_proxy


Base = declarative_base()

user_group_table = Table(
    "user_group",
    Base.metadata,
    Column("user_id", ForeignKey("users.user_id"), primary_key=True),
    Column("group_id", ForeignKey("groups.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    groups = relationship(
        "Group", secondary=user_group_table, cascade="all, delete",
        lazy="selectin", back_populates="users"
    )
    owned_groups = relationship(
        "Group", lazy="selectin", back_populates="owner"
    )


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))

    invite_token = Column(String(15), unique=True)
    chat_id = Column(BigInteger, unique=True)

    owner_id = Column(BigInteger, ForeignKey("users.user_id"))
    owner = relationship("User", back_populates="owned_groups")

    events = relationship("Event", lazy="selectin")
    users = relationship(
        "User", secondary=user_group_table, lazy="selectin",
        back_populates="groups"
    )
    user_ids = association_proxy("users", "user_id")


event_cronjob_table = Table(
    "event_cronjob",
    Base.metadata,
    Column("event_id", ForeignKey("events.id"), primary_key=True),
    Column("cronjob_id", ForeignKey("cronjobs.id"), primary_key=True)
)

event_weekday_table = Table(
    "event_weekday",
    Base.metadata,
    Column("event_id", ForeignKey("events.id"), primary_key=True),
    Column("weekday_id", ForeignKey("weekdays.id"), primary_key=True)
)


class WeekDay(Base):
    __tablename__ = "weekdays"

    id = Column(Integer, primary_key=True)
    cron_name = Column(String(30))
    name = Column(String(30))

    events = relationship(
        "Event", secondary=event_weekday_table,
        cascade="all, delete", back_populates="weekdays"
    )


class CronJob(Base):
    __tablename__ = "cronjobs"

    id = Column(Integer, primary_key=True)
    job_id = Column(String(255))


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(50), nullable=True)

    group_id = Column(Integer, ForeignKey("groups.id"))
    weekdays = relationship(
        "WeekDay", secondary=event_weekday_table,
        lazy="selectin", back_populates="events"
    )
    cronjobs = relationship(
        "CronJob", secondary=event_cronjob_table,
        cascade="all, delete", lazy="selectin"
    )
