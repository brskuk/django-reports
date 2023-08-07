"""Django report serializers."""
from rest_framework import serializers

from django_reports.filter import Connector


class FilterFieldSerializer(serializers.Serializer):
    """Filter field serializer."""

    field = serializers.CharField()
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
        print(args, kwargs)
        if "data" not in kwargs and len(args) < 2:
            # This is a nested serializer.
            return super().__new__(cls, *args, **kwargs)
        elif "children" in kwargs["data"]:
            return super().__new__(FilterConnectorNodeSerializer, *args, **kwargs)

        return super().__new__(FilterLeafNodeSerializer, *args, **kwargs)


class FilterConnectorNodeSerializer(serializers.Serializer):
    """Filter connector node serializer."""

    connector = serializers.ChoiceField(choices=Connector)
    children = FilterNodeSerializer(many=True)

    def validate_connector(self, connector):
        """Validate filter connector."""
        if connector not in Connector:
            raise serializers.ValidationError(
                f"Filter connector must be one of {', '.join(Connector)}.",
                code="invalid",
            )
        return connector


class FilterLeafNodeSerializer(serializers.Serializer):
    """Filter leaf node serializer."""

    field = FilterFieldSerializer()
    lookup_expression = serializers.CharField()
    # The type of this value is determined by the field type.
    value = serializers.Field()

    def validate_lookup_expression(self, lookup_expression):
        """Validate filter lookup expression."""
        # Todo: Implement lookup expression validation
        return lookup_expression

    def validate_value(self, value):
        """Validate filter value."""
        # Todo: Implement filter value validation
        return value


class FilterSerializer(serializers.Serializer):
    """Deserialize report filters."""

    def validate_field(self, field):
        """Validate filter field."""
        return field
