from app.taxonomy import CURRENT_VERSION, load_taxonomy


def test_current_taxonomy_is_versioned_and_contains_required_values() -> None:
    taxonomy = load_taxonomy()

    assert taxonomy["version"] == CURRENT_VERSION
    assert taxonomy["styles"] == [
        "fine-line",
        "minimalist",
        "traditional",
        "neo-traditional",
        "realism",
        "blackwork",
        "geometric",
        "ornamental",
        "watercolor",
        "japanese",
        "tribal",
        "abstract",
    ]
    assert "forearm" in taxonomy["placements"]
    assert taxonomy["size"] == ["small", "medium", "large"]
    assert taxonomy["complexity"] == ["simple", "moderate", "detailed"]
    assert taxonomy["color"] == ["black", "black-and-grey", "color"]
    assert taxonomy["orientation"] == ["vertical", "horizontal", "square", "wrap"]
