"""empty message

Revision ID: 0c5c4286900c
Revises: 34f086d0943f
Create Date: 2025-01-25 19:47:33.565467

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0c5c4286900c'
down_revision = '34f086d0943f'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('task')
    sa.Enum('INITIAL', 'PENDING', 'IN_PROGRESS', 'SUCCESS', 'FAILED', name='taskstatus').drop(op.get_bind(), checkfirst=False)
    op.create_table('task',
    sa.Column('request_uuid', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('INITIAL', 'PENDING', 'IN_PROGRESS', 'SUCCESS', 'FAILED', name='taskstatus'), nullable=False),
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('input_file_metadata_id', sa.BIGINT(), nullable=False),
    sa.Column('result_file_metadata_id', sa.BIGINT(), nullable=True),
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('dt_created', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('dt_updated', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['result_file_metadata_id'], ['minio_metadata.id'], ),
    sa.ForeignKeyConstraint(['input_file_metadata_id'], ['minio_metadata.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('request_uuid'),
    sa.UniqueConstraint('result_file_metadata_id'),
    sa.UniqueConstraint('input_file_metadata_id'),
    )


def downgrade():
    ...