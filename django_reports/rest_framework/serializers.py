"""Django report serializers."""
from rest_framework import serializers

from django_reports.filter import Connector


class FilterFieldSerializer(serializers.Serializer):
    """Filter field serializer."""

    name = serializers.CharField()
    path = serializers.CharField()

    def validate_name(self, name):
        """Validate filter field name."""
        # Todo: Implement filter field name validation
        return name

    def validate_path(self, path):
        """Validate filter field path."""
        # Todo: Implement filter field path validation
        return path


class FilterNodeSerializer(serializers.Serializer):
    """Filter node serializer."""

    def __new__(cls, *args, **kwargs):
        """Instantiate a `FilterLeafNode` or `FilterConnectorNode` based on the data."""
        is_connector_node_data = "children" in kwargs.get("data", {}) or (
            len(args) >= 2 and "children" in args[1]
        )

        if is_connector_node_data:
            return FilterConnectorNodeSerializer(*args, **kwargs)

        return FilterLeafNodeSerializer(*args, **kwargs)


class FilterConnectorNodeChildren(serializers.Field):
    """Filter connector node nested children serializer field."""

    def to_internal_value(self, connector_node_children):
        """Validate and return the given filter connector node children."""
        if not connector_node_children:
            raise serializers.ValidationError(
                "This field may not be empty.", code="required"
            )

        children_serializer = FilterNodeSerializer(
            data=connector_node_children, many=True
        )
        children_serializer.is_valid(raise_exception=True)

        return children_serializer.validated_data


class FilterConnectorNodeSerializer(serializers.Serializer):
    """Filter connector node serializer."""

    connector = serializers.ChoiceField(choices=Connector)
    children = FilterConnectorNodeChildren()


class FilterLeafNodeSerializer(serializers.Serializer):
    """Filter leaf node serializer."""

    field = FilterFieldSerializer()
    lookup_expression = serializers.CharField()
    # The type of this value is determined by the field type.
    value = serializers.CharField()

    def validate_lookup_expression(self, lookup_expression):
        """Validate filter lookup expression."""
        # Todo: Implement lookup expression validation
        return lookup_expression

    def validate_value(self, value):
        """Validate filter value."""
        # Todo: Implement filter value validation
        return value
