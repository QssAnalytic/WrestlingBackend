"""figter level and birth_date add nullable fighter

Revision ID: 64b4f09329c8
Revises: 58905ea144d5
Create Date: 2024-01-26 15:57:53.203383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64b4f09329c8'
down_revision: Union[str, None] = '58905ea144d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('fighters', 'birth_date',
               existing_type=sa.DATE(),
               nullable=True)
    op.alter_column('fighters', 'level',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('fighters', 'level',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('fighters', 'birth_date',
               existing_type=sa.DATE(),
               nullable=False)
    # ### end Alembic commands ###
