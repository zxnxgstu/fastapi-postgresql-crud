"""Create products table

Revision ID: 0e40a069490f
Revises: 
Create Date: 2026-09-10 17:32:41.343389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e40a069490f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('in_stock', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_products_id'),
        'products',
        ['id'],
        unique=False
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_products_id'),
        table_name='products'
    )

    op.drop_table('products')