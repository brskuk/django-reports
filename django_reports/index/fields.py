"""Classes and utilities for indexing Django model fields."""
from functools import cached_property
from typing import Optional, Sequence, Tuple, Type

from django.db import models


class ChoiceFieldMixin:
    _field: models.Field

    @cached_property
    def choices(self) -> Sequence[Tuple[str, str]]:
        return self._field.choices


class Field:
    def __init__(self, model_field, **kwargs) -> None:
        self.model_field = model_field

    @cached_property
    def name(self) -> str:
        return self.model_field.name

    @cached_property
    def is_relation(self) -> bool:
        return self.model_field.is_relation

    @cached_property
    def related_model(self) -> Optional[Type[models.Model]]:
        return self.model_field.related_model

    def __new__(cls, *args, **kwargs):
        """Create a choice variant of the index field if the model field has choices."""
        if kwargs.get("model_field", {}).get("choices") is not None:
            return type(f"{cls.__name__[-5:]}ChoiceField", (ChoiceFieldMixin, cls), {})(
                *args, **kwargs
            )

        return super().__new__(cls)

    def __str__(self) -> str:
        return str(self.model_field)


# Todo: Conditionally include expressions like "isnull" when the field is nullable.
class CharField(Field):
    lookup_expressions = {
        "in",
        "contains",
        "icontains",
        "exact",
        "iexact",
        "startswith",
        "endswith",
    }


class ForeignKeyField(Field):
    lookup_expressions = {"pk", "pk__in", "isnull"}


class IntegerField(Field):
    pass


class BooleanField(Field):
    pass


class DateField(Field):
    pass


class DateTimeField(Field):
    pass


model_field_map = {
    models.CharField: CharField,
    models.ForeignKey: ForeignKeyField,
    models.IntegerField: IntegerField,
    models.DateField: DateField,
    models.DateTimeField: DateTimeField,
}


def to_model_index_field(model_field):
    for field_class, index_class in model_field_map.items():
        if isinstance(model_field, field_class):
            return index_class(model_field)

    # Todo: Replace this with appropriate exception
    raise KeyError


def get_model_index_fields(model):
    index_fields = []

    for field in model._meta.get_fields():
        try:
            index_fields.append(to_model_index_field(field))
        except KeyError:
            continue

    return index_fields


class FieldTreeNode:
    def __init__(self, field=None, **kwargs) -> None:
        self.key = field and field.name
        self.field = field
        self.lookup_path = kwargs.get("lookup_path", "")
        self.children = kwargs.get("children", [])

    @property
    def is_leaf_node(self):
        return not self.children

    def add(self, node):
        """Add a child `node`."""
        self.children.append(node)

    def remove(self, child_node):
        """Prune `child_node`."""
        self.children.remove(child_node)

    def __str__(self) -> str:
        return f"<{self.key} ({self.lookup_path}): {', '.join(str(child) for child in self.children)}>"


class FieldTree:
    """An tree structured index of model fields."""

    def __init__(self, root) -> None:
        self.root = root

    def find(self, path):
        current_node = self.root

        for target_node_key in path:
            try:
                current_node = next(
                    filter(
                        lambda node: node.key == target_node_key, current_node.children
                    )
                )
            except StopIteration:
                return None

        return current_node

    def __str__(self) -> str:
        return str(self.root)


def create_model_field_branch(
    index_field: Field, visited_models, lookup_path=None
) -> FieldTreeNode:
    """Create a model field tree structure with `index_field` root node."""
    children = []

    if lookup_path is not None:
        lookup_path = f"{lookup_path}__{index_field.name}"
    else:
        lookup_path = index_field.name

    if index_field.is_relation:
        related_model_index_fields = get_model_index_fields(index_field.related_model)
        for index_field in related_model_index_fields:
            # We want to avoid circular traversals so we ignore relations to models already encountered
            # in this sub branch.
            if index_field.is_relation and index_field.related_model in visited_models:
                continue

            children.append(
                create_model_field_branch(
                    index_field,
                    {*visited_models, index_field.related_model},
                    lookup_path,
                )
            )

    return FieldTreeNode(field=index_field, lookup_path=lookup_path, children=children)


def build_model_field_tree(model: Type[models.Model]):
    """Construct a tree structured index of `model`\'s fields."""
    return FieldTree(
        root=FieldTreeNode(
            field=None,
            children=[
                create_model_field_branch(index_field, visited_models={model})
                for index_field in get_model_index_fields(model)
            ],
        )
    )
