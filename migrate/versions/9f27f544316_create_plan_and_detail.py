"""create plan and detail

Revision ID: 9f27f544316
Revises: 15ea0bb1a5df
Create Date: 2014-09-21 11:08:42.150325

"""

# revision identifiers, used by Alembic.
revision = '9f27f544316'
down_revision = '15ea0bb1a5df'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('plan',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.String(length=64), nullable=False),
                    sa.Column('content', sa.String(length=512), nullable=True),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('create_at', sa.DateTime(), nullable=True),
                    sa.Column('update_at', sa.DateTime(), nullable=True),
                    sa.Column(
                        'is_enable', sa.Boolean(), default='1', nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('plan_detail',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('plan_id', sa.Integer(), nullable=False),
                    sa.Column('note_kind_id', sa.Integer(), nullable=False),
                    sa.Column('quantity', sa.Integer(), nullable=False),
                    sa.Column('create_at', sa.DateTime(), nullable=True),
                    sa.Column('update_at', sa.DateTime(), nullable=True),
                    sa.Column(
                        'is_enable', sa.Boolean(), default='1', nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('plan_detail')
    op.drop_table('plan')
    ### end Alembic commands ###
