"""initial schema — all models

Revision ID: f20e733eb781
Revises:
Create Date: 2026-03-27 11:11:16.188205
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'f20e733eb781'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- ticket_types ---
    op.create_table('ticket_types',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.Enum('speaker', 'partner', 'press', 'vip', 'vip_black', 'general', 'investor', 'startup', name='ticketcategory'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_eur', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_complimentary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('requires_application', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('quantity_total', sa.Integer(), nullable=True),
        sa.Column('quantity_sold', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # --- attendees ---
    op.create_table('attendees',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    # --- admin_users ---
    op.create_table('admin_users',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    # --- orders ---
    op.create_table('orders',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('order_number', sa.String(20), nullable=False),
        sa.Column('attendee_id', UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('pending', 'confirmed', 'cancelled', 'refunded', name='orderstatus'), nullable=False),
        sa.Column('payment_status', sa.Enum('unpaid', 'paid', 'complimentary', 'refunded', name='paymentstatus'), nullable=False),
        sa.Column('total_eur', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('stripe_session_id', sa.String(255), nullable=True),
        sa.Column('stripe_payment_intent', sa.String(255), nullable=True),
        sa.Column('voucher_code', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['attendee_id'], ['attendees.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_orders_order_number', 'orders', ['order_number'], unique=True)
    op.create_index('ix_orders_voucher_code', 'orders', ['voucher_code'])

    # --- order_items ---
    op.create_table('order_items',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', UUID(as_uuid=True), nullable=False),
        sa.Column('ticket_type_id', UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('unit_price_eur', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['ticket_type_id'], ['ticket_types.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # --- vouchers ---
    op.create_table('vouchers',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('ticket_type_id', UUID(as_uuid=True), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('used_by_email', sa.String(255), nullable=True),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['ticket_type_id'], ['ticket_types.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_vouchers_code', 'vouchers', ['code'], unique=True)

    # --- applications ---
    op.create_table('applications',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('ticket_type_id', UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='applicationstatus'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('publication', sa.String(255), nullable=True),
        sa.Column('portfolio_url', sa.String(500), nullable=True),
        sa.Column('startup_name', sa.String(255), nullable=True),
        sa.Column('startup_website', sa.String(500), nullable=True),
        sa.Column('startup_stage', sa.String(100), nullable=True),
        sa.Column('voucher_code', sa.String(50), nullable=True),
        sa.Column('reviewed_by', sa.String(255), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['ticket_type_id'], ['ticket_types.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_applications_email', 'applications', ['email'])

    # --- referrals ---
    op.create_table('referrals',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('owner_name', sa.String(255), nullable=False),
        sa.Column('owner_email', sa.String(255), nullable=False),
        sa.Column('clicks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('orders_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('revenue_eur', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_referrals_code', 'referrals', ['code'], unique=True)
    op.create_index('ix_referrals_owner_email', 'referrals', ['owner_email'])

    # --- referral_attributions ---
    op.create_table('referral_attributions',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('referral_id', UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['referral_id'], ['referrals.id']),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_id'),
    )

    # --- check_ins ---
    op.create_table('check_ins',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', UUID(as_uuid=True), nullable=False),
        sa.Column('checked_in_by', sa.String(255), nullable=True),
        sa.Column('device_id', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_synced', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('checked_in_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_check_ins_order_id', 'check_ins', ['order_id'], unique=True)

    # --- waitlist_entries ---
    op.create_table('waitlist_entries',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('ticket_type_id', UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('notified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['ticket_type_id'], ['ticket_types.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_waitlist_entries_ticket_type_id', 'waitlist_entries', ['ticket_type_id'])


def downgrade() -> None:
    op.drop_index('ix_waitlist_entries_ticket_type_id', table_name='waitlist_entries')
    op.drop_table('waitlist_entries')
    op.drop_index('ix_check_ins_order_id', table_name='check_ins')
    op.drop_table('check_ins')
    op.drop_table('referral_attributions')
    op.drop_index('ix_referrals_owner_email', table_name='referrals')
    op.drop_index('ix_referrals_code', table_name='referrals')
    op.drop_table('referrals')
    op.drop_index('ix_applications_email', table_name='applications')
    op.drop_table('applications')
    op.drop_index('ix_vouchers_code', table_name='vouchers')
    op.drop_table('vouchers')
    op.drop_table('order_items')
    op.drop_index('ix_orders_voucher_code', table_name='orders')
    op.drop_index('ix_orders_order_number', table_name='orders')
    op.drop_table('orders')
    op.drop_table('admin_users')
    op.drop_table('attendees')
    op.drop_table('ticket_types')
