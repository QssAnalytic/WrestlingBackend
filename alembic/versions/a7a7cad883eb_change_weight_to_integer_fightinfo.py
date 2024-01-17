"""change weight to integer fightinfo

Revision ID: a7a7cad883eb
Revises: 2c9448ab1cfc
Create Date: 2024-01-16 15:57:28.043300

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7a7cad883eb'
down_revision: Union[str, None] = '2c9448ab1cfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa

def upgrade():
    # Use the `using` clause to specify the conversion
    op.execute('ALTER TABLE fightinfos ALTER COLUMN weight_category TYPE INTEGER USING weight_category::integer')

def downgrade():
    # If you need to rollback the change, you can specify the downgrade logic here
    op.alter_column('fightinfos', 'weight_category', type_=sa.String)
    # ### end Alembic commands ###
