"""Initial migration.

Revision ID: d0fbc43f0c0d
Revises: 
Create Date: 2023-10-08 18:02:46.476057

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd0fbc43f0c0d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=150), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.alter_column('content',
               existing_type=mysql.TEXT(),
               nullable=False)
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=10),
               type_=sa.String(length=50),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.String(length=50),
               type_=mysql.VARCHAR(length=10),
               nullable=True)
        batch_op.alter_column('content',
               existing_type=mysql.TEXT(),
               nullable=True)

    op.drop_table('user')
    # ### end Alembic commands ###
