from peewee import *
from inline_keyboards.keyboards import days_buttons


db = SqliteDatabase('lecture_bot.db')


class BaseModel(Model):
    class Meta:
        database = db


class Course(BaseModel):
    course_name = CharField()
    course_id = IntegerField()


# class User(BaseModel):
#     user_id = IntegerField()
#     course = ForeignKeyField(Course)


class Day(BaseModel):
    weekday = CharField()


class Lecture(BaseModel):
    lecture_name = CharField(50)
    description = CharField(100, null=True)
    time = TimeField(null=True)
    days = ManyToManyField(Day, backref='lectures')
    course = ForeignKeyField(Course)


LectureDay = Lecture.days.get_through_model()

# class LectureToDay(BaseModel):
#     lecture = ForeignKeyField(Lecture)
#     day = ForeignKeyField(Day)
#     course = ForeignKeyField(Course)


def db_init():
    db.create_tables([
        Course,
        Day,
        Lecture,
        LectureDay
    ])

    for day in days_buttons.values():
        Day.create(weekday=day)
