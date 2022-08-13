from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

from loader import DB_USER, DB_PASS, DB_HOST, DB_NAME

import keyboards.inline


Base = declarative_base()

user_group_table = Table(
    "user_group",
    Base.metadata,
    Column("user_id", ForeignKey("user.user_id"), primary_key=True),
    Column("group_id", ForeignKey("group.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True)
    groups = relationship(
        "Group", secondary=user_group_table, cascade="all, delete",
        lazy="selectin", back_populates="users"
    )
    owned_groups = relationship("Group", lazy="selectin", back_populates="owner")


class Group(Base):
    __tablename__ = "group"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    
    invite_token = Column(String(15), unique=True)
    chat_id = Column(BigInteger, unique=True, nullable=True)

    owner_id = Column(BigInteger, ForeignKey("user.user_id"))
    owner = relationship("User", back_populates="owned_groups")

    lecture = relationship("Lecture", lazy="selectin")
    users = relationship(
        "User", secondary=user_group_table, lazy="selectin", 
        back_populates="groups"
    )


lecture_cronjob_table = Table(
    "lecture_cronjob",
    Base.metadata,
    Column("lecture_id", ForeignKey("lecture.id"), primary_key=True),
    Column("cronjob_id", ForeignKey("cronjob.id"), primary_key=True)
)

lecture_weekday_table = Table(
    "lecture_weekday",
    Base.metadata,
    Column("lecture_id", ForeignKey("lecture.id"), primary_key=True),
    Column("weekday_id", ForeignKey("weekday.id"), primary_key=True)
)


class WeekDay(Base):
    __tablename__ = "weekday"

    id = Column(Integer, primary_key=True)
    cron_name = Column(String(30))
    name = Column(String(30))

    lectures = relationship(
        "Lecture", secondary=lecture_weekday_table, cascade="all, delete",
        back_populates="weekday"
    )


class CronJob(Base):
    __tablename__ = "cronjob"

    id = Column(Integer, primary_key=True)
    job_id = Column(String(255))


class Lecture(Base):
    __tablename__ = "lecture"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(50), nullable=True)

    group_id = Column(Integer, ForeignKey("group.id"))
    weekday = relationship(
        "WeekDay", secondary=lecture_weekday_table, lazy="selectin", 
        back_populates="lectures"
    )
    cronjob = relationship("CronJob", secondary=lecture_cronjob_table, lazy="selectin")


def db_init():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}", 
        future=True, echo=True
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    days = {
        'mon': "Пн", 'tue': "Вт", 'wed': "Ср",
        'thu': "Чт", 'fri': "Пт", 'sat': "Сб",
        'sun': "Вс"
    }

    for cron_name, name in days.items():
        session.add(WeekDay(cron_name=cron_name, name=name))
    
    session.commit()
    session.close()


def db_drop():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}", 
        future=True, echo=True
    )
    Base.metadata.drop_all(engine)
