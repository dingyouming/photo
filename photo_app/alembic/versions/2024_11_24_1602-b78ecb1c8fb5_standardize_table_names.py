"""standardize_table_names

Revision ID: b78ecb1c8fb5
Revises: 
Create Date: 2024-11-24 16:02:55.108946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b78ecb1c8fb5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=True),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('storage_quota', sa.Integer(), nullable=False),
    sa.Column('storage_used', sa.Integer(), nullable=False),
    sa.Column('encryption_key', sa.String(length=255), nullable=True),
    sa.Column('encryption_enabled', sa.Boolean(), nullable=False),
    sa.Column('backup_enabled', sa.Boolean(), nullable=False),
    sa.Column('last_backup_date', sa.DateTime(), nullable=True),
    sa.Column('backup_frequency', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('photos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('filepath', sa.String(length=255), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('storage_status', sa.String(length=20), nullable=False),
    sa.Column('failure_reason', sa.String(length=255), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=False),
    sa.Column('backup_status', sa.String(length=20), nullable=False),
    sa.Column('backup_path', sa.String(length=255), nullable=True),
    sa.Column('restore_status', sa.String(length=20), nullable=True),
    sa.Column('is_encrypted', sa.Boolean(), nullable=False),
    sa.Column('encryption_date', sa.DateTime(), nullable=True),
    sa.Column('encryption_method', sa.String(length=50), nullable=True),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('version_date', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('filepath')
    )
    op.create_table('albums',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('cover_photo_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['cover_photo_id'], ['photos.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('photo_metadata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('photo_id', sa.Integer(), nullable=False),
    sa.Column('color_profile', sa.String(length=50), nullable=True),
    sa.Column('dominant_colors', sa.String(length=255), nullable=True),
    sa.Column('faces_detected', sa.Integer(), nullable=True),
    sa.Column('face_locations', sa.String(length=1000), nullable=True),
    sa.Column('scene_type', sa.String(length=50), nullable=True),
    sa.Column('scene_confidence', sa.Integer(), nullable=True),
    sa.Column('blur_score', sa.Integer(), nullable=True),
    sa.Column('exposure_score', sa.Integer(), nullable=True),
    sa.Column('aesthetic_score', sa.Integer(), nullable=True),
    sa.Column('raw_exif', sa.String(length=4000), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['photo_id'], ['photos.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('photo_id')
    )
    op.create_table('photo_tags',
    sa.Column('photo_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('added_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['photo_id'], ['photos.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('photo_id', 'tag_id')
    )
    op.create_table('photo_albums',
    sa.Column('photo_id', sa.Integer(), nullable=False),
    sa.Column('album_id', sa.Integer(), nullable=False),
    sa.Column('added_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['album_id'], ['albums.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['photo_id'], ['photos.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('photo_id', 'album_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('photo_albums')
    op.drop_table('photo_tags')
    op.drop_table('photo_metadata')
    op.drop_table('albums')
    op.drop_table('photos')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('tags')
    # ### end Alembic commands ###
