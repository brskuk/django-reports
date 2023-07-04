from typing import Type

from django.db import models

from django_reports.index import fields


class TreeNode:
    def __init__(self, key, data, children=None, **kwargs) -> None:
        self.key = key
        self.data = data
        self.children = children or []

    @property
    def is_leaf_node(self):
        return bool(self.children)

    def add(self, node):
        self.children.append(node)

    def remove(self, child_node):
        self.children.remove(child_node)

    def __str__(self) -> str:
        return "<{name}: {children}>".format(
            name=self.key, children=", ".join(str(child) for child in self.children)
        )


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


def create_model_field_branch(index_field: fields.Field, visited_models) -> TreeNode:
    children = []

    if index_field.is_relation and index_field.related_model not in visited_models:
        related_model_index_fields = fields.get_model_index_fields(
            index_field.related_model
        )
        children = [
            create_model_field_branch(
                index_field, {*visited_models, index_field.related_model}
            )
            for index_field in related_model_index_fields
        ]

    node_data = {
        "field": index_field,
    }

    return TreeNode(
        key=index_field.name,
        children=children,
        data=node_data,
    )


def build_model_field_tree(model: Type[models.Model]):
    return FieldTree(
        root=TreeNode(
            key="root",
            children=[
                create_model_field_branch(index_field, visited_models={model})
                for index_field in fields.get_model_index_fields(model)
            ],
            data=None,
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
