"""add invoice_intallment table

Revision ID: 0532a76899f6
Revises: 4d1584124c82
Create Date: 2024-03-02 12:07:35.691741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0532a76899f6'
down_revision = '4d1584124c82'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invoice_installment',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('invoice_id', sa.UUID(), nullable=True),
    sa.Column('external_installment_id', sa.String(), nullable=False),
    sa.Column('installment', sa.Integer(), nullable=False),
    sa.Column('due_date', sa.DateTime(), nullable=False),
    sa.Column('amount_cents', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoice.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('invoice_installment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_invoice_installment_external_installment_id'), ['external_installment_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('invoice_installment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_invoice_installment_external_installment_id'))

    op.drop_table('invoice_installment')
    # ### end Alembic commands ###
