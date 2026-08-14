import json
import logging
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, ConfigDict

from app.taxonomy import load_taxonomy

logger = logging.getLogger(__name__)


class StructuredFilters(BaseModel):
    model_config = ConfigDict(extra="ignore")

    subject: str | None = None
    style: str | None = None
    placement: str | None = None
    size: str | None = None


class OpenAIQueryParser:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def parse(self, query: str) -> StructuredFilters:
        taxonomy = load_taxonomy()
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Parse the tattoo search query into JSON fields subject, style, "
                        "placement, and size. Return null when a field is not specified. "
                        f"Use only these taxonomy values: {json.dumps(taxonomy)}"
                    ),
                },
                {"role": "user", "content": query},
            ],
        )
        content = response.choices[0].message.content or "{}"
        filters = StructuredFilters.model_validate(json.loads(content))
        logger.info("query_filters_parsed query=%r filters=%s", query, filters.model_dump_json())
        return filters


def filters_to_dict(filters: StructuredFilters) -> dict[str, Any]:
    return filters.model_dump(exclude_none=True)
