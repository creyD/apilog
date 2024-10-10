"""empty message

Revision ID: e253d9799d38
Revises: 
Create Date: 2024-10-10 15:23:32.339647

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e253d9799d38"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "apikey",
        sa.Column("note", sa.String(length=512), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_apikey"),
        sa.UniqueConstraint("note", name="uq_apikey_note"),
    )


def downgrade() -> None:
    op.drop_table("apikey")
