"""set up task model for current workflow

Revision ID: 9bc99f240f5f
Revises: 337517ec92c5
Create Date: 2020-07-08 21:59:03.748035

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

from busy_beaver.common.models import Task

# revision identifiers, used by Alembic.
revision = "9bc99f240f5f"
down_revision = "337517ec92c5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("task", sa.Column("data", sa.JSON(), nullable=True))
    op.add_column(
        "task",
        sa.Column(
            "task_state",
            sqlalchemy_utils.types.choice.ChoiceType(Task.TaskState.STATES),
            nullable=True,
        ),
    )
    op.create_index(op.f("ix_task_task_state"), "task", ["task_state"], unique=False)
    op.drop_column("task", "description")
    op.drop_column("task", "failed")
    op.drop_column("task", "type")
    op.drop_column("task", "complete")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "task", sa.Column("complete", sa.BOOLEAN(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "task",
        sa.Column("type", sa.VARCHAR(length=55), autoincrement=False, nullable=True),
    )
    op.add_column(
        "task", sa.Column("failed", sa.BOOLEAN(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "task",
        sa.Column(
            "description", sa.VARCHAR(length=128), autoincrement=False, nullable=True
        ),
    )
    op.drop_index(op.f("ix_task_task_state"), table_name="task")
    op.drop_column("task", "task_state")
    op.drop_column("task", "data")
    # ### end Alembic commands ###
