"""Add group_id optional on itinerary table

Revision ID: e061e3fa6040
Revises: 26fb39a5aab1
Create Date: 2024-01-27 17:23:22.491315

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e061e3fa6040'
down_revision = '26fb39a5aab1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('itinerary', schema=None) as batch_op:
        batch_op.add_column(sa.Column('group_id', sa.UUID(), nullable=True))
        batch_op.create_foreign_key(None, 'group', ['group_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('itinerary', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('group_id')

    # ### end Alembic commands ###
