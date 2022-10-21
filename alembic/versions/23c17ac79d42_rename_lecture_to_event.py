"""rename lecture to event

Revision ID: 23c17ac79d42
Revises: 01_initial
Create Date: 2022-10-21 17:37:14.020581

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "23c17ac79d42"
down_revision = "01_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.Column("description", sa.String(length=50), nullable=True),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "event_cronjob",
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("cronjob_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cronjob_id"],
            ["cronjobs.id"],
        ),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
        ),
        sa.PrimaryKeyConstraint("event_id", "cronjob_id"),
    )
    op.create_table(
        "event_weekday",
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("weekday_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["events.id"],
        ),
        sa.ForeignKeyConstraint(
            ["weekday_id"],
            ["weekdays.id"],
        ),
        sa.PrimaryKeyConstraint("event_id", "weekday_id"),
    )
    op.drop_table("lecture_cronjob")
    op.drop_table("lecture_weekday")
    op.drop_table("lectures")
    op.drop_index(
        "ix_apscheduler_jobs_next_run_time", table_name="apscheduler_jobs"
    )
    op.drop_table("apscheduler_jobs")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "apscheduler_jobs",
        sa.Column(
            "id", sa.VARCHAR(length=191), autoincrement=False, nullable=False
        ),
        sa.Column(
            "next_run_time",
            postgresql.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "job_state", postgresql.BYTEA(), autoincrement=False,
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="apscheduler_jobs_pkey"),
    )
    op.create_index(
        "ix_apscheduler_jobs_next_run_time",
        "apscheduler_jobs",
        ["next_run_time"],
        unique=False,
    )
    op.create_table(
        "lectures",
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text("nextval('lectures_id_seq'::regclass)"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "name", sa.VARCHAR(length=50), autoincrement=False, nullable=True
        ),
        sa.Column(
            "description", sa.VARCHAR(length=50), autoincrement=False,
            nullable=True
        ),
        sa.Column(
            "group_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["group_id"], ["groups.id"], name="lectures_group_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="lectures_pkey"),
        sa.UniqueConstraint("name", name="lectures_name_key"),
        postgresql_ignore_search_path=False,
    )
    op.create_table(
        "lecture_weekday",
        sa.Column(
            "lecture_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "weekday_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["lecture_id"], ["lectures.id"],
            name="lecture_weekday_lecture_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["weekday_id"], ["weekdays.id"],
            name="lecture_weekday_weekday_id_fkey"
        ),
        sa.PrimaryKeyConstraint(
            "lecture_id", "weekday_id", name="lecture_weekday_pkey"
        ),
    )
    op.create_table(
        "lecture_cronjob",
        sa.Column(
            "lecture_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "cronjob_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["cronjob_id"], ["cronjobs.id"],
            name="lecture_cronjob_cronjob_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["lecture_id"], ["lectures.id"],
            name="lecture_cronjob_lecture_id_fkey"
        ),
        sa.PrimaryKeyConstraint(
            "lecture_id", "cronjob_id", name="lecture_cronjob_pkey"
        ),
    )
    op.drop_table("event_weekday")
    op.drop_table("event_cronjob")
    op.drop_table("events")
    # ### end Alembic commands ###