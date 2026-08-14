"""Add perceptual hashes for image deduplication."""

from alembic import op

revision = "0002_image_deduplication"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE tattoos ADD COLUMN image_hash text")
    op.execute("ALTER TABLE tattoos ADD COLUMN duplicate_of uuid REFERENCES tattoos(id)")
    op.execute("CREATE INDEX tattoos_image_hash_idx ON tattoos (image_hash)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS tattoos_image_hash_idx")
    op.execute("ALTER TABLE tattoos DROP COLUMN IF EXISTS duplicate_of")
    op.execute("ALTER TABLE tattoos DROP COLUMN IF EXISTS image_hash")
