"""Django report serializer tests."""
import pytest
from rest_framework import serializers

from django_reports.rest_framework.serializers import (
    FilterConnectorNodeSerializer,
    FilterLeafNodeSerializer,
    FilterNodeSerializer,
)
from tests.conftest import does_not_raise


class TestFilterNodeSerializer(object):
    """Test filter node serializer."""

    @pytest.mark.parametrize(
        "filter_node_data, expected_serializer_class",
        [
            ({"children": []}, FilterConnectorNodeSerializer),
            ({"field": {}}, FilterLeafNodeSerializer),
        ],
    )
    def test_correct_node_type_instantiated(
        self, filter_node_data, expected_serializer_class
    ):
        """Test that the correct node type is instantiated."""
        serializer = FilterNodeSerializer(data=filter_node_data)

        assert isinstance(serializer, expected_serializer_class)


class TestFilterSerializer(object):
    """Test filter serializer."""

    @pytest.mark.parametrize(
        "filter_data, expected_representation",
        [
            (
                {
                    "connector": "AND",
                    "children": [
                        {
                            "field": {
                                "name": "publication_date",
                                "path": "publication_date",
                            },
                            "lookup_expression": "date__gte",
                            "value": "2023-06-01",
                        }
                    ],
                },
                {
                    "connector": "AND",
                    "children": [
                        {
                            "field": {
                                "name": "publication_date",
                                "path": "publication_date",
                            },
                            "lookup_expression": "date__gte",
                            "value": "2023-06-01",
                        }
                    ],
                },
            )
        ],
    )
    def test_filter_deserialization(self, filter_data, expected_representation):
        """Test filter representation."""
        serializer = FilterNodeSerializer(data=filter_data)

        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        assert serializer.validated_data == expected_representation

    @pytest.mark.parametrize(
        "filter_data, expectation",
        [
            (
                {
                    "connector": "AND",
                    "children": [
                        {
                            "field": {
                                "name": "publication_date",
                                "path": "publication_date",
                            },
                            "lookup_expression": "date__gte",
                            "value": "2023-06-01",
                        }
                    ],
                },
                does_not_raise(),
            ),
            (
                {
                    "connector": "NAND",
                    "children": [
                        {
                            "field": {
                                "name": "publication_date",
                                "path": "publication_date",
                            },
                            "lookup_expression": "date__gte",
                            "value": "2023-06-01",
                        }
                    ],
                },
                pytest.raises(
                    serializers.ValidationError, match='"NAND" is not a valid choice.'
                ),
            ),
            (
                {
                    "connector": "AND",
                    "children": [],
                },
                pytest.raises(
                    serializers.ValidationError,
                    match=".+children.+This field may not be empty.",
                ),
            ),
        ],
    )
    def test_filter_serializer_validation(self, filter_data, expectation):
        """Test filter serializer validation."""
        serializer = FilterNodeSerializer(data=filter_data)

        with expectation:
            assert serializer.is_valid(raise_exception=True)
