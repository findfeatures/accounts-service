"""Added user projects table

Revision ID: ae9ea9766651
Revises: f96a6f19d483
Create Date: 2020-01-03 00:33:17.199174

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "ae9ea9766651"
down_revision = "f96a6f19d483"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users_projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_datetime_utc",
            sa.DateTime(),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("verified", sa.Boolean(), server_default="f", nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "project_id", name="user_projects_unique_ids"),
    )
    op.create_index(
        op.f("ix_users_projects_project_id"),
        "users_projects",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_users_projects_user_id"), "users_projects", ["user_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_users_projects_user_id"), table_name="users_projects")
    op.drop_index(op.f("ix_users_projects_project_id"), table_name="users_projects")
    op.drop_table("users_projects")
    # ### end Alembic commands ###
