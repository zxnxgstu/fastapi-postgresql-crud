"""add refunded payment status

Revision ID: 5f51373b5850
Revises: 0e66e16bc157
Create Date: 2026-09-11 07:37:58.652276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f51373b5850'
down_revision: Union[str, Sequence[str], None] = '0e66e16bc157'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_payments_status",
        "payments",
        type_="check"
    )

    op.create_check_constraint(
        "ck_payments_status",
        "payments",
        "status IN ('pending', 'paid', 'failed', 'refunded')"
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_payments_status",
        "payments",
        type_="check"
    )

    op.create_check_constraint(
        "ck_payments_status",
        "payments",
        "status IN ('pending', 'paid', 'failed')"
    )
