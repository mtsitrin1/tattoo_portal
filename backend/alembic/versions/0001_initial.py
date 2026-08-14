"""Create the initial tattoo portal schema."""

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute(
        """
        CREATE TABLE sources (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name text NOT NULL,
            url text,
            license_notes text,
            created_at timestamptz NOT NULL DEFAULT now()
        );
        CREATE TABLE artists (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name text NOT NULL,
            profile_url text,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        );
        CREATE TABLE users (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            email text UNIQUE,
            created_at timestamptz NOT NULL DEFAULT now()
        );
        CREATE TABLE tattoos (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            image_url text NOT NULL,
            source_id uuid NOT NULL REFERENCES sources(id),
            artist_id uuid REFERENCES artists(id),
            semantic_description text,
            subject text,
            style text,
            placement text,
            color text,
            size text,
            complexity text,
            orientation text,
            embedding vector(1536),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        );
        CREATE INDEX tattoos_embedding_idx ON tattoos USING hnsw (embedding vector_cosine_ops);
        CREATE TABLE user_interactions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid REFERENCES users(id),
            session_id text NOT NULL,
            tattoo_id uuid NOT NULL REFERENCES tattoos(id),
            event_type text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now()
        );
        CREATE INDEX user_interactions_tattoo_idx ON user_interactions (tattoo_id, created_at);
        CREATE TABLE saved_tattoos (
            user_id uuid NOT NULL REFERENCES users(id),
            tattoo_id uuid NOT NULL REFERENCES tattoos(id),
            created_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (user_id, tattoo_id)
        );
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TABLE IF EXISTS saved_tattoos, user_interactions, tattoos, users, artists, sources"
    )
