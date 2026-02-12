"""Updated models with non-nullable fields and new constraints

Revision ID: e80c7fdc1c70
Revises: b1ee26f24177
Create Date: 2026-02-12 22:25:48.348858

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e80c7fdc1c70'
down_revision = 'b1ee26f24177'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('contact', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(length=12),
               type_=sa.String(length=8),
               nullable=False)
        batch_op.create_unique_constraint('uq_contact_phone', ['phone'])

    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=True))
        batch_op.alter_column('timestamp',
               existing_type=sa.DATETIME(),
               nullable=False)
        batch_op.alter_column('contact_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.create_index(batch_op.f('ix_message_timestamp'), ['timestamp'], unique=False)
        batch_op.drop_constraint('fk_message_contact', type_='foreignkey')
        batch_op.create_foreign_key('fk_message_contact', 'contact', ['contact_id'], ['id'], ondelete='CASCADE')


def downgrade():
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_constraint('fk_message_contact', type_='foreignkey')
        batch_op.create_foreign_key('fk_message_contact', 'contact', ['contact_id'], ['id'])
        batch_op.drop_index(batch_op.f('ix_message_timestamp'))
        batch_op.alter_column('contact_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('timestamp',
               existing_type=sa.DATETIME(),
               nullable=True)
        batch_op.drop_column('status')

    with op.batch_alter_table('contact', schema=None) as batch_op:
        batch_op.drop_constraint('uq_contact_phone', type_='unique')
        batch_op.alter_column('phone',
               existing_type=sa.String(length=8),
               type_=sa.VARCHAR(length=12),
               nullable=True)
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###
