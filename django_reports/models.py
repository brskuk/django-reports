"""Django report models."""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from django_reports.filter import validate_filter_data
from django_reports.validators import validate_model_label


class Report(models.Model):
    """Store report metadata needed to process a queryset into data used for the report."""

    class Type(models.TextChoices):
        """Report types."""

        # Django QS group by + annotation operations
        TABLE = "TB", "table"
        CHART = "CH", "chart"

        # Django QS aggregation operations
        SUMMARY = "SU", "summary"

    name = models.CharField(verbose_name=_("name"), unique=True, max_length=100)
    model_label = models.CharField(
        verbose_name=_("report model label"), validators=[validate_model_label]
    )
    description = models.TextField(
        verbose_name=_("Description"), blank=True, default=str
    )
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reports"
    )
    type = models.CharField(verbose_name=_("type"), choices=Type.choices, max_length=2)

    # Store information about annotations (boolean flags, day/week/year of datetime field, etc.)
    annotations = models.JSONField(
        verbose_name=_("annotations"), blank=True, default=dict
    )
    # Store information about how the report QS will be filtered (created in 1 week ago to now, type is T, etc.)
    filters = models.JSONField(
        verbose_name=_("filters"),
        blank=True,
        default=dict,
        validators=[validate_filter_data],
    )
    # Store information about how the report QS will be aggregated (Group by, Count, Average, etc.)
    aggregations = models.JSONField(verbose_name=_("aggregations"))

    # Store report metadata, including chart type, chart settings (ApexChart options for example)
    options = models.JSONField(verbose_name=_("options"), blank=True, default=dict)

    class Meta(object):
        """Model metadata."""

        abstract = "django_reports" not in settings.INSTALLED_APPS
