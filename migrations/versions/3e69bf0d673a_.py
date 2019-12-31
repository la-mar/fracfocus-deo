"""empty message

Revision ID: 3e69bf0d673a
Revises: 4d5a7f435434
Create Date: 2019-12-30 11:45:51.314068

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e69bf0d673a'
down_revision = '4d5a7f435434'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_registry_updated_at', table_name='registry')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_registry_updated_at', 'registry', ['updated_at'], unique=False)
    # ### end Alembic commands ###
