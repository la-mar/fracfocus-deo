"""empty message

Revision ID: 37c8ce16ff47
Revises: 35b9394003cb
Create Date: 2019-12-30 09:22:10.599571

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '37c8ce16ff47'
down_revision = '35b9394003cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('integration_log')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('integration_log',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('integrated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('model_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('inserts', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('updates', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('deletes', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('updated_by', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='integration_log_pkey')
    )
    # ### end Alembic commands ###