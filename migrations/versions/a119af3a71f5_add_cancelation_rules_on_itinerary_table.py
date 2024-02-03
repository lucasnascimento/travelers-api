"""add cancelation_rules on itinerary table

Revision ID: a119af3a71f5
Revises: ac812beb411c
Create Date: 2024-02-03 17:26:45.402387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a119af3a71f5'
down_revision = 'ac812beb411c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('itinerary', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cancelation_rules', sa.String(), server_default='', nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('itinerary', schema=None) as batch_op:
        batch_op.drop_column('cancelation_rules')

    # ### end Alembic commands ###
