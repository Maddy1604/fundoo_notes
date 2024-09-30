"""Initialization Notes Model

Revision ID: ccd0f74ac852
Revises: 1db49f615a6a
Create Date: 2024-09-30 18:32:59.792628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccd0f74ac852'
down_revision: Union[str, None] = '1db49f615a6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('notes', 'color',
               existing_type=sa.CHAR(length=1),
               type_=sa.String(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('notes', 'color',
               existing_type=sa.String(),
               type_=sa.CHAR(length=1),
               existing_nullable=True)
    # ### end Alembic commands ###
