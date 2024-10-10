"""empty message

Revision ID: 21dc1dc045b8
Revises: 74c576cf9560
Create Date: 2024-10-10 20:32:12.579725

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "21dc1dc045b8"
down_revision: Union[str, None] = "74c576cf9560"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("logentry", schema=None) as batch_op:
        batch_op.add_column(sa.Column("environment", sa.String(length=64), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("logentry", schema=None) as batch_op:
        batch_op.drop_column("environment")
