"""change extracted_text to LONGTEXT"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = '0001_initial' 
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'manuscripts',
        'extracted_text',
        existing_type=sa.Text(),
        type_=sa.dialects.mysql.LONGTEXT(),
        existing_nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        'manuscripts',
        'extracted_text',
        existing_type=sa.dialects.mysql.LONGTEXT(),
        type_=sa.Text(),
        existing_nullable=True
    )
