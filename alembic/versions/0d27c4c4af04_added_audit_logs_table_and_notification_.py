"""Added audit logs table and notification table, as well as changed column type on Stripe Session

Revision ID: 0d27c4c4af04
Revises: b3af54251b82
Create Date: 2020-01-22 09:44:17.668093

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0d27c4c4af04"
down_revision = "b3af54251b82"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_datetime_utc",
            sa.DateTime(),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=False,
        ),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("log_type", sa.Text(), nullable=False),
        sa.Column("meta_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_logs_log_type"), "audit_logs", ["log_type"], unique=False
    )
    op.create_index(
        op.f("ix_audit_logs_project_id"), "audit_logs", ["project_id"], unique=False
    )
    op.create_table(
        "user_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_datetime_utc",
            sa.DateTime(),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notification_type", sa.Text(), nullable=False),
        sa.Column("meta_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_notifications_notification_type"),
        "user_notifications",
        ["notification_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_notifications_user_id"),
        "user_notifications",
        ["user_id"],
        unique=False,
    )
    op.execute(
        """
        ALTER TABLE stripe_sessions_completed
        ALTER COLUMN event_data
        SET DATA TYPE jsonb
        USING event_data::jsonb;
    """
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        """
        ALTER TABLE stripe_sessions_completed
        ALTER COLUMN event_data
        SET DATA TYPE json
        USING event_data::json;
    """
    )
    op.drop_index(
        op.f("ix_user_notifications_user_id"), table_name="user_notifications"
    )
    op.drop_index(
        op.f("ix_user_notifications_notification_type"), table_name="user_notifications"
    )
    op.drop_table("user_notifications")
    op.drop_index(op.f("ix_audit_logs_project_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_log_type"), table_name="audit_logs")
    op.drop_table("audit_logs")
    # ### end Alembic commands ###
