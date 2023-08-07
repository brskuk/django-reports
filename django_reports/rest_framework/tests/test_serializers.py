"""Django report serializer tests."""
import pytest

from django_reports.rest_framework.serializers import (
    FilterLeafNodeSerializer,
    FilterNodeSerializer,
    FilterConnectorNodeSerializer,
)


class TestFilterNodeSerializer:
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
