"""empty message

Revision ID: 95201f00f6b9
Revises: e253d9799d38
Create Date: 2024-10-10 15:45:50.089915

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "95201f00f6b9"
down_revision: Union[str, None] = "e253d9799d38"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "application",
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_application"),
        sa.UniqueConstraint("name", name="uq_application_name"),
    )


def downgrade() -> None:
    op.drop_table("application")
