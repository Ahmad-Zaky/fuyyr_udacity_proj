"""empty message

Revision ID: 5afe185d195e
Revises: 9aebba5f4f5b
Create Date: 2021-03-06 18:47:22.305734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5afe185d195e'
down_revision = '9aebba5f4f5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'artists', ['phone'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'artists', type_='unique')
    # ### end Alembic commands ###
