"""empty message

Revision ID: 74c576cf9560
Revises: 95201f00f6b9
Create Date: 2024-10-10 17:38:19.834168

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "74c576cf9560"
down_revision: Union[str, None] = "95201f00f6b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "logentry",
        sa.Column("application", sa.UUID(), nullable=False),
        sa.Column(
            "l_type",
            sa.Enum("INFO", "WARNING", "ERROR", "CRITICAL", name="logtype"),
            nullable=False,
        ),
        sa.Column(
            "t_type",
            sa.Enum("CREATE", "UPDATE", "DELETE", "UNDEFINED", name="transactiontype"),
            nullable=False,
        ),
        sa.Column("message", sa.String(length=512), nullable=True),
        sa.Column("author", sa.String(length=512), nullable=False),
        sa.Column("object_reference", sa.String(length=512), nullable=True),
        sa.Column("previous_object", sa.JSON(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["application"], ["application.id"], ondelete="CASCADE", name="fk_logentry_application"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_logentry"),
    )


def downgrade() -> None:
    op.drop_table("logentry")
