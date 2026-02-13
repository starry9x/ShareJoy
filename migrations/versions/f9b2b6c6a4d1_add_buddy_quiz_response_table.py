"""add buddy quiz response table

Revision ID: f9b2b6c6a4d1
Revises: 427f6f7bc3e7
Create Date: 2026-02-14 07:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9b2b6c6a4d1'
down_revision = '427f6f7bc3e7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'buddy_quiz_response',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('user_name', sa.String(length=100), nullable=False),
        sa.Column('answer', sa.String(length=50), nullable=False),
        sa.Column('matched_buddy_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['group.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('buddy_quiz_response')
