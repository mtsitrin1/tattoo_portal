from unittest.mock import Mock
from uuid import uuid4

from app.metadata import TattooMetadata, extract_metadata_batch


def test_metadata_batch_updates_records_and_continues_after_failure() -> None:
    first_id, second_id = uuid4(), uuid4()
    first_tattoo = Mock()
    session = Mock()
    session.get.side_effect = [first_tattoo, Mock(side_effect=RuntimeError("unused"))]
    provider = Mock()
    provider.extract.side_effect = [
        TattooMetadata(style="blackwork", subject="bird"),
        RuntimeError("vision request failed"),
    ]

    succeeded, failed = extract_metadata_batch(
        session,
        provider,
        [(first_id, b"first"), (second_id, b"second")],
    )

    assert (succeeded, failed) == (1, 1)
    assert first_tattoo.style == "blackwork"
    assert first_tattoo.subject == "bird"
    session.commit.assert_called_once_with()
    session.rollback.assert_called_once_with()
