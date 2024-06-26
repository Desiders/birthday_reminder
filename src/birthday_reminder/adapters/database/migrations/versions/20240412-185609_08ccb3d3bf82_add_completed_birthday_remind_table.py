"""add-completed-birthday-remind-table

Revision ID: 08ccb3d3bf82
Revises: 544a963233cc
Create Date: 2024-04-12 18:56:09.597600

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "08ccb3d3bf82"
down_revision: Union[str, None] = "544a963233cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "completed_birthday_reminds",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("uuid_generate_v7()"),
            nullable=False,
        ),
        sa.Column("birthday_remind_id", sa.Uuid(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column(
            "reminder_type",
            sa.Enum("BeforehandInOneDay", "OnTheDay", name="remindertype"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["birthday_remind_id"],
            ["birthday_reminds.id"],
            name=op.f(
                "fk_completed_birthday_reminds_birthday_remind_id_birthday_reminds"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_completed_birthday_reminds")
        ),
        sa.UniqueConstraint(
            "birthday_remind_id",
            "year",
            "reminder_type",
            name=op.f(
                "uq_completed_birthday_reminds_birthday_remind_id_year_reminder_type"
            ),
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("completed_birthday_reminds")
    # ### end Alembic commands ###
