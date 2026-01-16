"""add image_url to contact

Revision ID: ff72bc94b9dd
Revises: d99ce86d8603
Create Date: 2026-01-15 22:21:16.246052

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff72bc94b9dd'
down_revision = 'd99ce86d8603'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('contact', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.String(length=200), nullable=True))

def downgrade():
    with op.batch_alter_table('contact', schema=None) as batch_op:
        batch_op.drop_column('image_url')

