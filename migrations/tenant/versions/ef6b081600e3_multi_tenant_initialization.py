"""Multi tenant initialization

Revision ID: ef6b081600e3
Revises: 
Create Date: 2024-04-13 17:29:16.347129

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef6b081600e3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('mime', sa.String(), nullable=False),
    sa.Column('path', sa.String(), nullable=False),
    sa.Column('file_name', sa.String(), nullable=False),
    sa.Column('region', sa.String(), nullable=False),
    sa.Column('size_bytes', sa.Integer(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gateway_return',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('method', sa.String(), nullable=False),
    sa.Column('path', sa.String(), nullable=False),
    sa.Column('body', sa.JSON(), nullable=True),
    sa.Column('headers', sa.JSON(), nullable=True),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('group',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('description')
    )
    op.create_table('token_blocklist',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('jti', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_token_blocklist_jti'), 'token_blocklist', ['jti'], unique=False)
    op.create_table('institution',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('active_on_website', sa.Boolean(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('document', sa.String(), nullable=False),
    sa.Column('has_banking_account', sa.Boolean(), nullable=False),
    sa.Column('banking_account', sa.JSON(), nullable=True),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('file_id', sa.UUID(), nullable=True),
    sa.Column('ranking', sa.Numeric(), server_default='9999', nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('itinerary',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('current_step', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('boarding_date', sa.Date(), nullable=False),
    sa.Column('landing_date', sa.Date(), nullable=False),
    sa.Column('seats', sa.Integer(), nullable=False),
    sa.Column('details', sa.String(), nullable=False),
    sa.Column('summary', sa.String(), nullable=False),
    sa.Column('services', sa.String(), nullable=False),
    sa.Column('terms_and_conditions', sa.String(), nullable=False),
    sa.Column('institution_id', sa.UUID(), nullable=True),
    sa.Column('cover_id', sa.UUID(), nullable=True),
    sa.Column('group_id', sa.UUID(), nullable=True),
    sa.Column('cover_small_id', sa.UUID(), nullable=True),
    sa.Column('cancelation_rules', sa.String(), server_default='', nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['cover_id'], ['file.id'], ),
    sa.ForeignKeyConstraint(['cover_small_id'], ['file.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institution.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('booking',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('itinerary_id', sa.UUID(), nullable=True),
    sa.Column('payer_name', sa.String(), nullable=False),
    sa.Column('payer_email', sa.String(), nullable=False),
    sa.Column('payer_phone', sa.String(), nullable=False),
    sa.Column('payer_document', sa.String(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['itinerary_id'], ['itinerary.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('itinerary_document',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('link', sa.String(), nullable=False),
    sa.Column('document_id', sa.UUID(), nullable=True),
    sa.Column('itinerary_id', sa.UUID(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['file.id'], ),
    sa.ForeignKeyConstraint(['itinerary_id'], ['itinerary.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('itinerary_entry',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('itinerary_id', sa.UUID(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['itinerary_id'], ['itinerary.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('itinerary_photo',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('photo_id', sa.UUID(), nullable=True),
    sa.Column('itinerary_id', sa.UUID(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['itinerary_id'], ['itinerary.id'], ),
    sa.ForeignKeyConstraint(['photo_id'], ['file.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('itinerary_rule',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('purchase_deadline', sa.Date(), nullable=False),
    sa.Column('installments', sa.Integer(), nullable=False),
    sa.Column('itinerary_id', sa.UUID(), nullable=True),
    sa.Column('pix_discount', sa.Numeric(), server_default='0', nullable=False),
    sa.Column('seat_price', sa.Numeric(), server_default='0', nullable=False),
    sa.Column('montly_interest', sa.Numeric(), server_default='0', nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['itinerary_id'], ['itinerary.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('booking_traveler',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('booking_id', sa.UUID(), nullable=True),
    sa.Column('traveler_name', sa.String(), nullable=False),
    sa.Column('traveler_birthdate', sa.Date(), nullable=False),
    sa.Column('traveler_gender', sa.String(), nullable=False),
    sa.Column('traveler_extras', sa.JSON(), nullable=True),
    sa.Column('total_cents', sa.Integer(), server_default='0', nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('invoice',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('booking_id', sa.UUID(), nullable=True),
    sa.Column('invoice_id', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('method', sa.String(), nullable=False),
    sa.Column('due_date', sa.DateTime(), nullable=False),
    sa.Column('items_total_cents', sa.Integer(), server_default='0', nullable=False),
    sa.Column('discount_cents', sa.Integer(), server_default='0', nullable=False),
    sa.Column('total_cents', sa.Integer(), server_default='0', nullable=False),
    sa.Column('invoice_url', sa.String(), nullable=True),
    sa.Column('invoice_extras', sa.JSON(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['booking.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_invoice_id'), 'invoice', ['invoice_id'], unique=False)
    op.create_table('invoice_event',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('invoice_id', sa.UUID(), nullable=True),
    sa.Column('gatewayreturn_id', sa.UUID(), nullable=True),
    sa.Column('event', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('inserted_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['gatewayreturn_id'], ['gateway_return.id'], ),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoice.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
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
    op.create_index(op.f('ix_invoice_installment_external_installment_id'), 'invoice_installment', ['external_installment_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_invoice_installment_external_installment_id'), table_name='invoice_installment')
    op.drop_table('invoice_installment')
    op.drop_table('invoice_event')
    op.drop_index(op.f('ix_invoice_invoice_id'), table_name='invoice')
    op.drop_table('invoice')
    op.drop_table('booking_traveler')
    op.drop_table('itinerary_rule')
    op.drop_table('itinerary_photo')
    op.drop_table('itinerary_entry')
    op.drop_table('itinerary_document')
    op.drop_table('booking')
    op.drop_table('itinerary')
    op.drop_table('institution')
    op.drop_index(op.f('ix_token_blocklist_jti'), table_name='token_blocklist')
    op.drop_table('token_blocklist')
    op.drop_table('group')
    op.drop_table('gateway_return')
    op.drop_table('file')
    # ### end Alembic commands ###
