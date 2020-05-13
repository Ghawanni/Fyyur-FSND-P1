"""empty message

Revision ID: fec7d73081bf
Revises: a60df4a6e1dd
Create Date: 2020-05-13 21:57:15.371717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fec7d73081bf'
down_revision = 'a60df4a6e1dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_name', sa.String(length=120), nullable=True),
    sa.Column('artist_name', sa.String(length=120), nullable=True),
    sa.Column('venue_image_link', sa.String(length=500), nullable=True),
    sa.Column('artist_image_link', sa.String(length=500), nullable=True),
    sa.Column('start_time', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['artist_image_link'], ['Artist.image_link'], ),
    sa.ForeignKeyConstraint(['artist_name'], ['Artist.name'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.ForeignKeyConstraint(['venue_image_link'], ['Venue.image_link'], ),
    sa.ForeignKeyConstraint(['venue_name'], ['Venue.name'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('artist_image_link'),
    sa.UniqueConstraint('artist_name'),
    sa.UniqueConstraint('venue_image_link'),
    sa.UniqueConstraint('venue_name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Show')
    # ### end Alembic commands ###