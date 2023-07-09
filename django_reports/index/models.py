"""Classes and utilities for indexing Django models."""
from functools import cached_property
from typing import Type

from django.db import models

from django_reports.index import fields


class ModelIndex:
    """Index model information and provide utility methods to access model metadata."""

    def __init__(self, model: Type[models.Model]) -> None:
        self._model = model

    @cached_property
    def field_index(self):
        return fields.build_model_field_tree(self._model)

    @cached_property
    def name(self):
        return self._model._meta.verbose_name.title()

    @cached_property
    def label(self):
        return self._model._meta.label
