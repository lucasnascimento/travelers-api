"""add total cents into invoice

Revision ID: ac812beb411c
Revises: d2963c46266f
Create Date: 2024-02-03 07:29:07.559018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac812beb411c'
down_revision = 'd2963c46266f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('invoice', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total_cents', sa.Integer(), server_default='0', nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('invoice', schema=None) as batch_op:
        batch_op.drop_column('total_cents')

    # ### end Alembic commands ###
