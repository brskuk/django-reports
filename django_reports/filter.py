from typing import Any, Dict

from django import VERSION as DJANGO_VERSION
from django.core.exceptions import ValidationError
from django.db import models

from django_reports.index.models import ModelIndex
from django_reports.structs import Option

# Query XOR is not supported for django version < 4.1.
SUPPORTS_XOR = DJANGO_VERSION[0] > 4 or (
    DJANGO_VERSION[0] == 4 and DJANGO_VERSION[1] >= 1
)


class Connector(str, Option):
    OR = "OR"
    AND = "AND"

    if SUPPORTS_XOR:
        XOR = "XOR"


class Filter:
    def __init__(self, data, model_index: ModelIndex) -> None:
        self._query = to_query(data)
        self.model_index = model_index

    def __call__(self, queryset):
        """Filter the report queryset with the initialized query."""
        return queryset.filter(self._query)


def to_query(filter_node_data: Dict[str, Any]):
    if "children" not in filter_node_data:
        # Leaf node
        field_lookup_path = filter_node_data["path"]

        if filter_node_data.get("lookup_expression"):
            field_lookup_path += f"__{filter_node_data.get('lookup_expression')}"

        return (field_lookup_path, filter_node_data["value"])

    children = [to_query(child) for child in filter_node_data.get("children", [])]

    return models.Q(
        *children,
        _connector=filter_node_data.get("connector"),
        _negated=filter_node_data.get("negated", False),
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


def validate_filter_data(filter_node_data, field_index):
    """Recursively validate the filter data tree."""
    children = filter_node_data.get("children")
    if children:
        _validate_filter_connector_node(filter_node_data)
        for child_node in children:
            validate_filter_data(child_node, field_index)
    else:
        _validate_filter_leaf_node(filter_node_data, field_index)


def _validate_filter_connector_node(filter_node_data):
    """Validate filter connector data."""
    connector = filter_node_data.get("connector")
    children = filter_node_data.get("children")

    if not connector:
        raise ValidationError("'connector' is required.", code="required")
    elif connector not in Connector:
        raise ValidationError(
            f"'{connector}' is not a valid connector.", code="invalid"
        )
    elif not children:
        raise ValidationError("'children' can not be empty.", code="required")

    connector = filter_node_data["connector"]

    if connector not in set(Connector):
        raise ValidationError(f"{connector} is not a valid connector.", code="invalid")


def _validate_filter_leaf_node(filter_node_data, field_index):
    """Validate the data that will be used to filter against a specific field."""
    field_path = filter_node_data["path"]

    index_field = field_index.find(field_path)

    if index_field is None:
        raise ValidationError(
            f"Field with path '{field_path}' does not exist or is not supported.",
            code="invalid",
        )

    # Todo: Implement missing validation checks
    # Validate lookup expression
    # Validate value for field and lookup expression
