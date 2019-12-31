"""empty message

Revision ID: 35b9394003cb
Revises: 0939e60510fd
Create Date: 2019-12-29 16:26:45.261559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35b9394003cb'
down_revision = '0939e60510fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'registry', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'registry', type_='unique')
    # ### end Alembic commands ###