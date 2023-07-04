from enum import Enum
from typing import Any, Dict, Optional

from django.db import models


class Connectors(str, Enum):
    OR = "OR"
    AND = "AND"
    XOR = "XOR"


def to_query(filter_node: Dict[str, Any]):
    if isinstance(filter_node, tuple):
        return filter_node

    children = [to_query(child) for child in filter_node.get("children", [])]

    return models.Q(
        *children, _connector=filter_node["connector"], _negated=filter_node["negated"]
    )


def to_dict(filter_query):
    if isinstance(filter_query, tuple):
        return filter_query

    return {
        "connector": filter_query.connector,
        "negated": filter_query.negated,
        "children": (
            [to_dict(child) for child in filter_query.children]
            if filter_query.children
            else []
        ),
    }


class Filter:
    def __init__(self, data, model_index) -> None:
        self._query = to_query(data)
        self.model_index = model_index

    @property
    def data(self):
        return to_dict(self._query)

    def validate(self):
        pass
