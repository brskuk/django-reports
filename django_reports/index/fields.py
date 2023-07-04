from typing import Sequence, Tuple

from django.db import models


class ChoiceFieldMixin:
    _field: models.Field

    @property
    def choices(self) -> Sequence[Tuple[str, str]]:
        return self._field.choices

    def options(self):
        options = super().options()
        options.update(choices=self.choices)

        return options


class Field:
    def __init__(self, model_field, **kwargs) -> None:
        self.model_field = model_field

    @property
    def name(self):
        return self.model_field.name

    @property
    def is_relation(self):
        return self.model_field.is_relation

    @property
    def related_model(self):
        return self.model_field.related_model

    def __new__(cls, *args, **kwargs):
        """Create a choice variant of the report field if the model field has choices."""
        if kwargs.get("model_field", {}).get("choices") is not None:
            return type(
                f"{cls.__name__[-5:]}ChoiceField",
                (ChoiceFieldMixin, cls),
                {},
            )(*args, **kwargs)

        return super().__new__(cls)

    def __str__(self) -> str:
        return str(self.model_field)

    def options(self):
        return {
            "name": self.name,
            "type": self.type,
        }


class CharField(Field):
    pass


class ForeignKeyField(Field):
    pass


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
