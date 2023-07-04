from typing import Type

from django.db import models

from django_reports.index import fields


class TreeNode:
    def __init__(self, field=None, **kwargs) -> None:
        self.key = field and field.name
        self.field = field
        self.lookup_path = kwargs.get("lookup_path", "")
        self.children = kwargs.get("children", [])

    @property
    def is_leaf_node(self):
        return bool(self.children)

    def add(self, node):
        self.children.append(node)

    def remove(self, child_node):
        self.children.remove(child_node)

    def __str__(self) -> str:
        return f"<{self.key} ({self.lookup_path}): {', '.join(str(child) for child in self.children)}>"


class FieldTree:
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
    index_field: fields.Field, visited_models, lookup_path=None
) -> TreeNode:
    children = []

    if lookup_path is not None:
        lookup_path = f"{lookup_path}__{index_field.name}"
    else:
        lookup_path = index_field.name

    if index_field.is_relation:
        related_model_index_fields = fields.get_model_index_fields(
            index_field.related_model
        )
        for index_field in related_model_index_fields:
            if index_field.is_relation and index_field.related_model in visited_models:
                continue

            children.append(
                create_model_field_branch(
                    index_field,
                    {*visited_models, index_field.related_model},
                    lookup_path,
                )
            )

    return TreeNode(
        field=index_field,
        lookup_path=lookup_path,
        children=children,
    )


def build_model_field_tree(model: Type[models.Model]):
    return FieldTree(
        root=TreeNode(
            field=None,
            children=[
                create_model_field_branch(index_field, visited_models={model})
                for index_field in fields.get_model_index_fields(model)
            ],
        )
    )


class ModelIndex:
    def __init__(self, model: Type[models.Model]) -> None:
        self._model = model
        self._fields = None
        self._field_tree = None

    @property
    def field_tree(self):
        if self._field_tree is None:
            self._field_tree = build_model_field_tree(self._model)

        return self._field_tree

    def look_up_field(self, lookup_expression):
        field_path = lookup_expression.split("__")
