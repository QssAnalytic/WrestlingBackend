"""create_empty_migration

Revision ID: 5f825feceafd
Revises: fc43347575c3
Create Date: 2023-12-21 16:19:13.606610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f825feceafd'
down_revision: Union[str, None] = 'fc43347575c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Example: Changing column name from 'old_column' to 'new_column'
    op.alter_column('fightinfos', 'type', new_column_name='decision')



def downgrade() -> None:
    # Example: Rolling back the column name change
    op.alter_column('fightinfos', 'decision', new_column_name='type')

