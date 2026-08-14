from unittest.mock import Mock
from uuid import uuid4

from app.metadata import generate_embeddings_batch


def test_embedding_batch_is_rerunnable_and_persists_vectors() -> None:
    tattoo_id = uuid4()
    tattoo = Mock(semantic_description="A blackwork bird on the forearm.")
    session = Mock()
    session.get.return_value = tattoo
    provider = Mock()
    provider.embed.return_value = [0.1, 0.2]

    first = generate_embeddings_batch(session, provider, [tattoo_id])
    second = generate_embeddings_batch(session, provider, [tattoo_id])

    assert first == (1, 0)
    assert second == (1, 0)
    assert tattoo.embedding == [0.1, 0.2]
    assert provider.embed.call_count == 2
    assert session.commit.call_count == 2
