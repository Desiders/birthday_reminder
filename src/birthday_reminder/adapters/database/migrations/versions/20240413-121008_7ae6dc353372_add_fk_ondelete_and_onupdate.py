"""add-fk-ondelete-and-onupdate

Revision ID: 7ae6dc353372
Revises: 08ccb3d3bf82
Create Date: 2024-04-13 12:10:08.235846

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7ae6dc353372"
down_revision: Union[str, None] = "08ccb3d3bf82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "fk_birthday_reminds_user_id_users",
        "birthday_reminds",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_birthday_reminds_user_id_users"),
        "birthday_reminds",
        "users",
        ["user_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "fk_completed_birthday_reminds_birthday_remind_id_birthd_b49a",
        "completed_birthday_reminds",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f(
            "fk_completed_birthday_reminds_birthday_remind_id_birthday_reminds"
        ),
        "completed_birthday_reminds",
        "birthday_reminds",
        ["birthday_remind_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f(
            "fk_completed_birthday_reminds_birthday_remind_id_birthday_reminds"
        ),
        "completed_birthday_reminds",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_completed_birthday_reminds_birthday_remind_id_birthd_b49a",
        "completed_birthday_reminds",
        "birthday_reminds",
        ["birthday_remind_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_birthday_reminds_user_id_users"),
        "birthday_reminds",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_birthday_reminds_user_id_users",
        "birthday_reminds",
        "users",
        ["user_id"],
        ["id"],
    )
    # ### end Alembic commands ###
