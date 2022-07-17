from django_fsm import FSMFieldMixin
from rest_framework import serializers
from model_utils.fields import StatusField as ModelUtilsStatusField
from versatileimagefield.serializers import (
    VersatileImageFieldSerializer as BaseVersatileImageFieldSerializer,
)


class StateField(FSMFieldMixin, ModelUtilsStatusField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("choices_name", "")
        super().__init__(*args, **kwargs)


class VersatileImageFieldSerializer(BaseVersatileImageFieldSerializer):
    """Extension to return null instead of {} when the image is not set."""

    def to_representation(self, value):
        return super().to_representation(value) or None


class FileField(serializers.FileField):
    def to_representation(self, value):
        data = super().to_representation(value)
        if data:
            return {"url": data}
        return None


class URLField(serializers.URLField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if "://" not in value:
            value = "http://" + value
        return value
