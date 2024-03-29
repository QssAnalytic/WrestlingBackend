"""add check_author and order field fightinfo

Revision ID: 6828f305a507
Revises: 47ce59983414
Create Date: 2024-02-01 12:16:17.516212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6828f305a507'
down_revision: Union[str, None] = '47ce59983414'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fightinfos', sa.Column('check_author', sa.String(length=60), nullable=True))
    op.add_column('fightinfos', sa.Column('order', sa.String(length=60), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fightinfos', 'order')
    op.drop_column('fightinfos', 'check_author')
    # ### end Alembic commands ###
