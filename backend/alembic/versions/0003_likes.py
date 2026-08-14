"""Add persisted likes."""

from alembic import op

revision = "0003_likes"
down_revision = "0002_image_deduplication"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE likes (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid REFERENCES users(id),
            session_id text NOT NULL,
            tattoo_id uuid NOT NULL REFERENCES tattoos(id),
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (session_id, tattoo_id)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS likes")
