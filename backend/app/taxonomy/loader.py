import json
from functools import lru_cache
from pathlib import Path
from typing import Any

CURRENT_VERSION = "v1"
_CONFIG_PATH = Path(__file__).with_name("configs") / f"{CURRENT_VERSION}.json"


@lru_cache(maxsize=1)
def load_taxonomy() -> dict[str, Any]:
    with _CONFIG_PATH.open(encoding="utf-8") as config_file:
        return json.load(config_file)
