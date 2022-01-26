from django_fsm import FSMFieldMixin
from model_utils.fields import StatusField as ModelUtilsStatusField


class StateField(FSMFieldMixin, ModelUtilsStatusField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("choices_name", "")
        super().__init__(*args, **kwargs)
