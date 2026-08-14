from unittest.mock import Mock
from uuid import uuid4

from app.metadata import TattooMetadata, generate_descriptions_batch


def test_description_batch_persists_description_and_continues_after_failure() -> None:
    first_id, second_id = uuid4(), uuid4()
    first_tattoo = Mock()
    session = Mock()
    session.get.return_value = first_tattoo
    provider = Mock()
    provider.generate.side_effect = ["A blackwork bird on the forearm.", RuntimeError("failed")]
    metadata = TattooMetadata(style="blackwork", subject="bird")

    succeeded, failed = generate_descriptions_batch(
        session,
        provider,
        [(first_id, b"first", metadata), (second_id, b"second", metadata)],
    )

    assert (succeeded, failed) == (1, 1)
    assert first_tattoo.semantic_description == "A blackwork bird on the forearm."
    session.commit.assert_called_once_with()
    session.rollback.assert_called_once_with()
