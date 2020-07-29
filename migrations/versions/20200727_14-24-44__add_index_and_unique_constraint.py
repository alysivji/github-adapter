"""add index and unique constraint

Revision ID: 31f9b92e97db
Revises: 50cefad49d98
Create Date: 2020-07-27 14:24:44.542662

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "31f9b92e97db"
down_revision = "50cefad49d98"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        op.f("ix_upcoming_events_group_meetup_urlname"),
        "upcoming_events_group",
        ["meetup_urlname"],
        unique=False,
    )
    op.create_unique_constraint(
        "unique_group_per_config",
        "upcoming_events_group",
        ["config_id", "meetup_urlname"],
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "unique_group_per_config", "upcoming_events_group", type_="unique"
    )
    op.drop_index(
        op.f("ix_upcoming_events_group_meetup_urlname"),
        table_name="upcoming_events_group",
    )
    # ### end Alembic commands ###
