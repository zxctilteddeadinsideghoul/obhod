import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel


def to_plain(value: Any) -> Any:
    if isinstance(value, BaseModel):
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")
        return value.dict()
    if isinstance(value, list):
        return [to_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: to_plain(item) for key, item in value.items()}
    return value


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, dict | list):
        return json.dumps(value, ensure_ascii=False, default=format_value)
    return str(value)


def json_bytes(value: Any) -> bytes:
    return json.dumps(to_plain(value), ensure_ascii=False, default=format_value, indent=2).encode("utf-8")
