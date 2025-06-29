"""Add Example model

Revision ID: 2cc5a6ee4d63
Revises:
Create Date: 2023-12-29 12:36:54.070091

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2cc5a6ee4d63'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'examples',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=32), nullable=False),
        sa.Column('birthday', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('examples_pkey')),
    )
    op.create_index(op.f('examples_name_idx'), 'examples', ['name'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('examples_name_idx'), table_name='examples')
    op.drop_table('examples')
