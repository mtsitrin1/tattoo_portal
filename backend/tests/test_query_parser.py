from unittest.mock import Mock

from app.query_parser import StructuredFilters, filters_to_dict


def test_structured_filters_are_serializable_for_search_and_evaluation() -> None:
    filters = StructuredFilters(style="blackwork", placement="forearm")

    assert filters_to_dict(filters) == {"style": "blackwork", "placement": "forearm"}


def test_provider_contract_returns_structured_filters() -> None:
    provider = Mock()
    provider.parse.return_value = StructuredFilters(subject="bird", size="small")

    result = provider.parse("small bird tattoo")

    assert result == StructuredFilters(subject="bird", size="small")
