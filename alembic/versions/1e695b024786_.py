"""empty message

Revision ID: 1e695b024786
Revises: 21dc1dc045b8
Create Date: 2025-01-20 11:36:14.692849

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1e695b024786"
down_revision: Union[str, None] = "21dc1dc045b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("application", schema=None) as batch_op:
        batch_op.add_column(sa.Column("retention_days", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("application", schema=None) as batch_op:
        batch_op.drop_column("retention_days")
