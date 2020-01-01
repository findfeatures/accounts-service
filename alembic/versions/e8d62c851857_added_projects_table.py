"""added projects table

Revision ID: e8d62c851857
Revises: 967423dc584a
Create Date: 2020-01-01 18:50:28.674367

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "e8d62c851857"
down_revision = "967423dc584a"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_datetime_utc",
            sa.DateTime(),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=False,
        ),
        sa.Column("deleted_datetime_utc", sa.DateTime(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users_projects",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users_projects")
    op.drop_table("projects")
    # ### end Alembic commands ###
