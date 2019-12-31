"""empty message

Revision ID: 10f881dcc11b
Revises: 3d20bae505be
Create Date: 2019-12-29 13:57:55.027137

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '10f881dcc11b'
down_revision = '3d20bae505be'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('registry', 'pkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('registry', sa.Column('pkey', postgresql.UUID(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
