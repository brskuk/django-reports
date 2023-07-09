import pytest
from django.core.exceptions import ValidationError
from django.db import models

from django_reports.filter import (
    SUPPORTS_XOR,
    Connector,
    _validate_filter_connector_node,
    to_query,
)
from tests.conftest import does_not_raise


class TestToQuery:
    @pytest.mark.parametrize(
        "filter_node_data,expected_query",
        [
            (
                {
                    "connector": Connector.AND,
                    "children": [
                        {
                            "name": "name",
                            "path": "name",
                            "lookup_expression": "startswith",
                            "value": "A",
                        },
                        {
                            "negated": True,
                            "children": [
                                {
                                    "name": "name",
                                    "path": "publisher__name",
                                    "value": "Springer",
                                }
                            ],
                        },
                        {
                            "connector": Connector.OR,
                            "children": [
                                {
                                    "name": "rating",
                                    "path": "books__rating",
                                    "lookup_expression": "gte",
                                    "value": 4.0,
                                },
                                {
                                    "name": "awards",
                                    "path": "books__awards",
                                    "lookup_expression": "isnull",
                                    "value": False,
                                },
                            ],
                        },
                    ],
                },
                (
                    models.Q(name__startswith="A")
                    & (~models.Q(publisher__name="Springer"))
                    & (
                        models.Q(books__rating__gte=4.0)
                        | models.Q(books__awards__isnull=False)
                    )
                ),
            ),
            # Skip this test case if django version under test < 4.1 since XOR is not supported.
            pytest.param(
                SUPPORTS_XOR
                and {
                    "connector": Connector.XOR,
                    "children": [
                        {"name": "country_id", "path": "country_id", "value": 401},
                        {
                            "name": "name",
                            "path": "country__name",
                            "lookup_expression": "iexact",
                            "value": "netherlands",
                        },
                    ],
                },
                SUPPORTS_XOR
                and (
                    models.Q(country_id=401)
                    ^ models.Q(country__name__iexact="netherlands")
                ),
                marks=(
                    pytest.mark.skipif(
                        not SUPPORTS_XOR, reason="Unsupported operator '^'"
                    )
                ),
            ),
            (
                {
                    "connector": Connector.OR,
                    "negated": True,
                    "children": [
                        {
                            "connector": Connector.AND,
                            "children": [
                                {
                                    "name": "publication_date",
                                    "path": "publication_date",
                                    "lookup_expression": "year",
                                    "value": "2020",
                                },
                                {
                                    "negated": True,
                                    "children": [
                                        {
                                            "name": "format",
                                            "path": "format",
                                            "value": "paperback",
                                        }
                                    ],
                                },
                            ],
                        },
                        {
                            "name": "name",
                            "path": "genre__name",
                            "lookup_expression": "in",
                            "value": ["mystery", "science fiction", "novel"],
                        },
                        {
                            "name": "publication_date",
                            "path": "publication_date",
                            "lookup_expression": "year__lt",
                            "value": "1990",
                        },
                    ],
                },
                (
                    models.Q(
                        models.Q(publication_date__year="2020")
                        & ~models.Q(format="paperback"),
                        genre__name__in=["mystery", "science fiction", "novel"],
                        publication_date__year__lt="1990",
                        _connector=Connector.OR,
                        _negated=True,
                    )
                ),
            ),
        ],
    )
    def test_to_query(self, filter_node_data, expected_query):
        """Test that the correct query instance is instantiated from the filter data dictionary."""
        assert to_query(filter_node_data) == expected_query


class TestValidateFilterData:
    @pytest.mark.parametrize(
        "filter_node_data,expectation",
        [
            # Depends on Django version
            pytest.param(
                {"connector": "XOR", "children": ["child1", "child2"]},
                (
                    does_not_raise()
                    if SUPPORTS_XOR
                    else pytest.raises(
                        ValidationError, match="'XOR' is not a valid connector"
                    )
                ),
            ),
            # ==================== Positive Test Cases ====================
            # Valid filter node data
            # =============================================================
            (
                {"connector": Connector.AND, "children": ["child1", "child2"]},
                does_not_raise(),
            ),
            (
                {"connector": Connector.OR, "children": ["child1", "child2"]},
                does_not_raise(),
            ),
            # ==================== Negative Test Cases ====================
            # Invalid filter node data
            # =============================================================
            (
                {
                    "connector": Connector.AND,
                },
                pytest.raises(ValidationError, match="'children' can not be empty."),
            ),
            (
                {
                    "children": ["child1", "child2"],
                },
                pytest.raises(ValidationError, match="'connector' is required."),
            ),
            (
                {
                    "connector": "INVALID",
                    "children": ["child1", "child2"],
                },
                pytest.raises(
                    ValidationError, match="'INVALID' is not a valid connector."
                ),
            ),
        ],
    )
    def test_validate_filter_connector(self, filter_node_data, expectation):
        """Test that connector filter node data is validated correctly."""
        with expectation:
            _validate_filter_connector_node(filter_node_data)
