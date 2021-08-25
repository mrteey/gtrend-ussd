"""Added transaction table

Revision ID: bcba69623fde
Revises: 09e62105865e
Create Date: 2021-08-24 20:58:21.790917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcba69623fde'
down_revision = '09e62105865e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agent_id', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('transaction_type', sa.String(), nullable=True),
    sa.Column('created_at', sa.String(), nullable=True),
    sa.Column('reference', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['agent.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('agent', sa.Column('email', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'agent', ['phone'])
    op.create_unique_constraint(None, 'agent', ['email'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'agent', type_='unique')
    op.drop_constraint(None, 'agent', type_='unique')
    op.drop_column('agent', 'email')
    op.drop_table('transaction')
    # ### end Alembic commands ###