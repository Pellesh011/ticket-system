"""add priorities table and migrate priority data

Revision ID: 5098e3e7a4fe
Revises: d4bef338a24e
Create Date: 2026-06-28 14:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5098e3e7a4fe"
down_revision: Union[str, None] = "d4bef338a24e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create priorities table
    op.create_table(
        "priorities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_priorities_id"), "priorities", ["id"], unique=False)
    op.create_index(op.f("ix_priorities_name"), "priorities", ["name"], unique=True)

    # 2. Seed default priorities
    op.execute(
        "INSERT INTO priorities (id, name, sort_order) VALUES "
        "(1, 'low', 0), "
        "(2, 'normal', 1), "
        "(3, 'high', 2)"
    )

    # 3. Add priority_id column (nullable initially)
    with op.batch_alter_table("tickets", schema=None) as batch_op:
        batch_op.add_column(sa.Column("priority_id", sa.Integer(), nullable=True))

    # 4. Migrate existing data: old priority (0,1,2) + 1 = priority_id (1,2,3)
    op.execute("UPDATE tickets SET priority_id = priority + 1")

    # 5. Make priority_id NOT NULL, add FK and index, drop old priority column
    with op.batch_alter_table("tickets", schema=None) as batch_op:
        batch_op.alter_column("priority_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_index("ix_tickets_priority_id", ["priority_id"])
        batch_op.create_foreign_key(
            "fk_tickets_priority_id", "priorities", ["priority_id"], ["id"]
        )
        batch_op.drop_column("priority")


def downgrade() -> None:
    # 1. Add priority column back
    with op.batch_alter_table("tickets", schema=None) as batch_op:
        batch_op.add_column(sa.Column("priority", sa.Integer(), nullable=True))

    # 2. Restore data: priority_id - 1 = old priority value
    op.execute("UPDATE tickets SET priority = priority_id - 1")

    # 3. Make priority NOT NULL, drop FK and priority_id
    with op.batch_alter_table("tickets", schema=None) as batch_op:
        batch_op.alter_column("priority", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_constraint("fk_tickets_priority_id", type_="foreignkey")
        batch_op.drop_index("ix_tickets_priority_id")
        batch_op.drop_column("priority_id")

    # 4. Drop priorities table
    op.drop_index(op.f("ix_priorities_name"), table_name="priorities")
    op.drop_index(op.f("ix_priorities_id"), table_name="priorities")
    op.drop_table("priorities")
