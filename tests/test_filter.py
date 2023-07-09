import pytest
from django.db import models

from django_reports.filter import SUPPORTS_XOR, Connector, to_query


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
