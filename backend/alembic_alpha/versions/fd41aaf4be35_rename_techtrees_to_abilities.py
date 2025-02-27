"""rename techtrees to abilities

Revision ID: fd41aaf4be35
Revises: cc37daa79a8e
Create Date: 2024-12-12 00:00:00.000000
"""
from alembic import op

# revision identifiers, used by Alembic
revision = 'fd41aaf4be35'
down_revision = 'cc37daa79a8e'  # Updated to point to previous migration
branch_labels = None
depends_on = None

def upgrade():
    op.rename_table('tech_trees', 'abilities')

def downgrade():
    op.rename_table('abilities', 'tech_trees')